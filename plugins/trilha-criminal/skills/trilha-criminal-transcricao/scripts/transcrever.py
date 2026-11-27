#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /// script
# requires-python = ">=3.9,<3.14"
# dependencies = ["faster-whisper>=1.1.0,<2", "av>=11,<19"]
# ///
"""Transcrição local de áudio e vídeo da Trilha Criminal.

Transcreve a mídia no próprio computador, com o modelo Whisper (biblioteca
faster-whisper). A mídia não é enviada a nenhum serviço: a internet só é usada
na primeira vez, para baixar o programa e o modelo.

O script não identifica quem fala, não corrige o texto e não resume. Grava o
que o modelo devolveu, com a minutagem de cada trecho, e marca os trechos em
que o próprio modelo indicou baixa confiança ou repetição.

Uso:
  python transcrever.py diagnostico
  python transcrever.py preparar [--modelo turbo]
  python transcrever.py transcrever MIDIA [MIDIA ...] --saida PASTA
         [--modelo turbo] [--idioma pt] [--termos "nomes e termos do caso"]
         [--inicio HH:MM:SS] [--fim HH:MM:SS] [--formatos txt,srt,json]
         [--dispositivo cpu|cuda] [--threads N] [--sem-filtro-de-silencio]
  python transcrever.py autoteste

Com o uv instalado, troque "python" por "uv run --script": ele cria sozinho o
ambiente com a biblioteca, sem o passo "preparar". O autoteste usa só a
biblioteca padrão. Python 3.9 a 3.13.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

VERSAO = "0.1.0"
TAXA = 16000  # amostras por segundo que o modelo recebe
PASTA_AMBIENTE = Path.home() / ".trilha-criminal" / "transcricao" / "venv"
# As mesmas do bloco "script" acima. A biblioteca av 19 deixou de aceitar um
# parâmetro que o faster-whisper 1.2.1 usa para ler a mídia; por isso o teto.
DEPENDENCIAS = ["faster-whisper>=1.1.0,<2", "av>=11,<19"]
MODELO_PADRAO = "turbo"
MODELOS = {
    "turbo": "cerca de 1,6 GB, o mais preciso entre os rápidos (padrão)",
    "small": "cerca de 0,5 GB, mais rápido e menos preciso",
    "medium": "cerca de 1,5 GB, mais lento que o turbo",
    "large-v3": "cerca de 3 GB, o mais lento",
}
# Limites que o próprio Whisper usa para desconfiar de um trecho.
LIMITE_LOGPROB = -1.0
LIMITE_COMPRESSAO = 2.4
REPETICOES_SEGUIDAS = 3
# Silêncio, em segundos, que abre nova linha dentro de um mesmo trecho do modelo.
PAUSA_QUE_DIVIDE = 2.0

AVISO = (
    "Texto produzido por programa, sem conferência humana. Não identifica quem fala, "
    "pode errar nomes, números e trechos com ruído ou vozes sobrepostas, e pode criar "
    "frases em trechos de silêncio. A mídia original é a fonte: confira na minutagem "
    "indicada antes de citar."
)


class ErroEntrada(Exception):
    pass


# --------------------------------------------------------------------------
# Tempo e nomes de arquivo (só biblioteca padrão)
# --------------------------------------------------------------------------

def fmt_tempo(segundos, milissegundos=False, separador=","):
    """71.5 -> '00:01:11' ou '00:01:11,500'."""
    total_ms = int(round(max(0.0, float(segundos)) * 1000))
    h, resto = divmod(total_ms, 3_600_000)
    m, resto = divmod(resto, 60_000)
    s, ms = divmod(resto, 1000)
    base = f"{h:02d}:{m:02d}:{s:02d}"
    return f"{base}{separador}{ms:03d}" if milissegundos else base


def ler_tempo(texto):
    """'90', '01:30' ou '00:01:30' -> 90.0 segundos."""
    partes = str(texto).strip().replace(",", ".").split(":")
    if not 1 <= len(partes) <= 3 or any(p == "" for p in partes):
        raise ErroEntrada(f"tempo inválido: {texto!r}. Use HH:MM:SS, MM:SS ou segundos.")
    try:
        valores = [float(p) for p in partes]
    except ValueError:
        raise ErroEntrada(f"tempo inválido: {texto!r}. Use HH:MM:SS, MM:SS ou segundos.") from None
    if any(v < 0 for v in valores):
        raise ErroEntrada(f"tempo inválido: {texto!r}.")
    segundos = 0.0
    for v in valores:
        segundos = segundos * 60 + v
    return segundos


def base_de_saida(midia, pasta, inicio=None, fim=None, formatos=("txt", "srt", "json")):
    """Devolve o caminho-base (sem extensão) que não sobrescreve nada existente."""
    nome = Path(midia).stem
    if inicio is not None or fim is not None:
        a = fmt_tempo(inicio or 0).replace(":", "")
        b = fmt_tempo(fim).replace(":", "") if fim is not None else "fim"
        nome += f".trecho-{a}-{b}"
    nome += ".transcricao"
    pasta = Path(pasta)
    n = 1
    while True:
        base = pasta / (nome if n == 1 else f"{nome}-{n}")
        ocupados = [base.with_name(base.name + "." + f) for f in formatos]
        ocupados.append(base.with_name(base.name + ".parcial.txt"))
        if not any(p.exists() for p in ocupados):
            return base
        n += 1


def sha256_do_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


# --------------------------------------------------------------------------
# Marcação e escrita dos trechos (só biblioteca padrão)
# --------------------------------------------------------------------------

def normalizar(texto):
    return " ".join(str(texto).lower().split()).strip(" .,!?;:")


def dividir_por_pausa(palavras, pausa=PAUSA_QUE_DIVIDE):
    """Agrupa palavras (inicio, fim, texto) em linhas, abrindo outra a cada pausa longa.

    A minutagem de cada linha passa a ser a da primeira palavra dita. Sem isso,
    depois de um silêncio o início do trecho pode cair vários segundos antes da fala.
    """
    linhas, atual = [], []
    for p in palavras:
        if atual and p[0] - atual[-1][1] > pausa:
            linhas.append(atual)
            atual = []
        atual.append(p)
    if atual:
        linhas.append(atual)
    # Palavra solta antes da pausa, sem ponto final, é começo da frase seguinte que o
    # alinhamento deixou para trás: junta à frente, com a minutagem da frase.
    i = 0
    while i < len(linhas) - 1:
        grupo = linhas[i]
        if len(grupo) == 1 and not grupo[0][2].strip().endswith((".", "?", "!", "…")):
            seguinte = linhas.pop(i + 1)
            palavra = (seguinte[0][0], seguinte[0][0], grupo[0][2])
            linhas[i] = [palavra] + seguinte
        else:
            i += 1
    saida = []
    for grupo in linhas:
        texto = "".join(p[2] for p in grupo).strip()
        if texto:
            saida.append((grupo[0][0], grupo[-1][1], texto))
    return saida


def marcar(trechos):
    """Acrescenta a cada trecho a lista 'conferir' com os sinais do próprio modelo."""
    seguidas = 1
    for i, t in enumerate(trechos):
        sinais = []
        if t.get("logprob") is not None and t["logprob"] < LIMITE_LOGPROB:
            sinais.append("baixa confiança")
        if t.get("compressao") is not None and t["compressao"] > LIMITE_COMPRESSAO:
            sinais.append("texto repetitivo")
        if i and normalizar(t["texto"]) and normalizar(t["texto"]) == normalizar(trechos[i - 1]["texto"]):
            seguidas += 1
        else:
            seguidas = 1
        if seguidas >= REPETICOES_SEGUIDAS:
            for anterior in trechos[i - seguidas + 1:i + 1]:
                if "repetição em sequência" not in anterior.setdefault("conferir", []):
                    anterior["conferir"].append("repetição em sequência")
        t["conferir"] = sinais + [s for s in t.get("conferir", []) if s not in sinais]
    return trechos


def linha_txt(t):
    marca = f" [conferir: {', '.join(t['conferir'])}]" if t.get("conferir") else ""
    return f"[{fmt_tempo(t['inicio'])}] {t['texto'].strip()}{marca}"


def cabecalho_txt(meta):
    trecho = f"{fmt_tempo(meta['trecho_inicio'])} a {fmt_tempo(meta['trecho_fim'])}"
    return "\n".join([
        "TRANSCRIÇÃO AUTOMÁTICA, NÃO CONFERIDA",
        "",
        f"Arquivo: {meta['arquivo']}",
        f"SHA-256 do arquivo: {meta['sha256']}",
        f"Duração da mídia: {fmt_tempo(meta['duracao'])}",
        f"Trecho transcrito: {trecho}",
        f"Programa: faster-whisper, modelo {meta['modelo']} ({meta['dispositivo']}, {meta['precisao']})",
        f"Idioma: {meta['idioma']}",
        f"Filtro de silêncio: {'ligado' if meta['filtro_de_silencio'] else 'desligado'}",
        f"Termos informados: {meta['termos'] or 'nenhum'}",
        f"Gerada em: {meta['gerada_em']}",
        "",
        f"Aviso: {AVISO}",
        "",
        "A minutagem entre colchetes é o início de cada trecho na mídia original.",
        "",
        "",
    ])


def rodape_txt(trechos):
    marcados = sum(1 for t in trechos if t.get("conferir"))
    linhas = ["", "", f"Fim da transcrição. Trechos: {len(trechos)}."]
    if marcados:
        linhas.append(
            f"Trechos com sinal do programa para conferir primeiro: {marcados}. "
            "A falta do sinal não indica trecho correto."
        )
    return "\n".join(linhas) + "\n"


def texto_srt(trechos):
    blocos = []
    for i, t in enumerate(trechos, 1):
        blocos.append(
            f"{i}\n{fmt_tempo(t['inicio'], True)} --> {fmt_tempo(t['fim'], True)}\n{t['texto'].strip()}\n"
        )
    return "\n".join(blocos)


def gravar_saidas(base, meta, trechos, formatos, parcial=None):
    """Grava os arquivos finais. 'parcial' é o TXT escrito durante a transcrição."""
    gravados = []
    base = Path(base)
    if "txt" in formatos:
        destino = base.with_name(base.name + ".txt")
        corpo = cabecalho_txt(meta) + "\n".join(linha_txt(t) for t in trechos) + rodape_txt(trechos)
        destino.write_text(corpo, encoding="utf-8")
        gravados.append(destino)
    if "srt" in formatos:
        destino = base.with_name(base.name + ".srt")
        destino.write_text(texto_srt(trechos), encoding="utf-8")
        gravados.append(destino)
    if "json" in formatos:
        destino = base.with_name(base.name + ".json")
        dados = dict(meta, aviso=AVISO, trechos=trechos)
        destino.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        gravados.append(destino)
    if parcial is not None and Path(parcial).exists():
        Path(parcial).unlink()
    return gravados


# --------------------------------------------------------------------------
# Ambiente
# --------------------------------------------------------------------------

def python_do_ambiente():
    sub = "Scripts/python.exe" if os.name == "nt" else "bin/python"
    return PASTA_AMBIENTE / sub


def tem_biblioteca():
    try:
        import faster_whisper  # noqa: F401
        return True
    except Exception:  # noqa: BLE001  (importação pode falhar por DLL, não só por ausência)
        return False


def no_ambiente_preparado():
    try:
        return Path(sys.executable).resolve() == python_do_ambiente().resolve()
    except OSError:
        return False


def reexecutar_no_ambiente():
    """Se a biblioteca falta aqui mas o ambiente preparado existe, roda nele."""
    if tem_biblioteca() or no_ambiente_preparado() or not python_do_ambiente().exists():
        return None
    return subprocess.call([str(python_do_ambiente()), "-B", os.path.abspath(__file__), *sys.argv[1:]])


def modelo_em_cache(modelo):
    try:
        from faster_whisper.utils import download_model
        download_model(modelo, local_files_only=True)
        return True
    except Exception:  # noqa: BLE001
        return False


def placas_cuda():
    try:
        import ctranslate2
        return int(ctranslate2.get_cuda_device_count())
    except Exception:  # noqa: BLE001
        return 0


def threads_padrao():
    return max(1, min(8, (os.cpu_count() or 4) // 2))


def instrucoes_de_instalacao():
    aqui = os.path.abspath(__file__)
    return "\n".join([
        "A biblioteca de transcrição ainda não está instalada neste computador.",
        "Escolha um caminho (a instalação baixa cerca de 250 MB; o modelo, cerca de 1,6 GB):",
        f'  1. Com o uv instalado:   uv run --script "{aqui}" transcrever ...',
        f'  2. Só com o Python:      python "{aqui}" preparar   (cria {PASTA_AMBIENTE})',
        "Depois do passo 2, o comando transcrever usa o ambiente criado sozinho.",
    ])


def cmd_diagnostico(_args):
    livre = shutil.disk_usage(Path.home()).free / 1024 ** 3
    biblioteca = tem_biblioteca()
    print(f"transcrever.py {VERSAO}")
    print(f"Sistema: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python em uso: {platform.python_version()} ({sys.executable})")
    print(f"uv: {'instalado' if shutil.which('uv') else 'não encontrado'}")
    print(f"Ambiente preparado ({PASTA_AMBIENTE}): {'existe' if python_do_ambiente().exists() else 'não existe'}")
    print(f"Biblioteca faster-whisper neste Python: {'instalada' if biblioteca else 'ausente'}")
    if biblioteca:
        for nome in MODELOS:
            print(f"Modelo {nome}: {'já baixado' if modelo_em_cache(nome) else 'não baixado'} ({MODELOS[nome]})")
        n = placas_cuda()
        print(f"Placa NVIDIA utilizável: {'sim, ' + str(n) if n else 'não (a transcrição roda no processador)'}")
    print(f"Núcleos do processador: {os.cpu_count() or '?'} (threads usadas por padrão: {threads_padrao()})")
    print(f"Espaço livre na pasta do usuário: {livre:.1f} GB")
    if not biblioteca:
        print()
        print(instrucoes_de_instalacao())
    return 0


def cmd_preparar(args):
    if sys.version_info >= (3, 14):
        print("Aviso: este Python é mais novo que os testados (3.9 a 3.13). "
              "Se a instalação falhar, use o uv, que baixa a versão certa do Python.")
    if not python_do_ambiente().exists():
        print(f"Criando o ambiente em {PASTA_AMBIENTE} ...", flush=True)
        PASTA_AMBIENTE.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.call([sys.executable, "-m", "venv", str(PASTA_AMBIENTE)])
        if r != 0 or not python_do_ambiente().exists():
            print("Não foi possível criar o ambiente. Em alguns sistemas falta o pacote python3-venv.")
            return 3
    print("Instalando a biblioteca faster-whisper (cerca de 250 MB) ...", flush=True)
    r = subprocess.call([str(python_do_ambiente()), "-m", "pip", "install", "--upgrade",
                         "--disable-pip-version-check", *DEPENDENCIAS])
    if r != 0:
        print("A instalação falhou. Leia a mensagem acima; sem internet ou com rede restrita ela não conclui.")
        return 3
    if args.modelo:
        print(f"Baixando o modelo {args.modelo} ({MODELOS.get(args.modelo, 'tamanho não catalogado')}) ...", flush=True)
        codigo = "import sys; from faster_whisper.utils import download_model; download_model(sys.argv[1])"
        r = subprocess.call([str(python_do_ambiente()), "-c", codigo, args.modelo])
        if r != 0:
            print("O download do modelo falhou. Ele será tentado de novo na primeira transcrição.")
            return 3
    print("Ambiente pronto.")
    return 0


# --------------------------------------------------------------------------
# Transcrição
# --------------------------------------------------------------------------

def carregar_modelo(args):
    from faster_whisper import WhisperModel
    precisao = "float16" if args.dispositivo == "cuda" else "int8"
    em_cache = modelo_em_cache(args.modelo)
    if not em_cache:
        print(f"Baixando o modelo {args.modelo} ({MODELOS.get(args.modelo, 'tamanho não catalogado')}). "
              "Isso acontece só na primeira vez e a mídia não é enviada.", flush=True)
    modelo = WhisperModel(args.modelo, device=args.dispositivo, compute_type=precisao,
                          cpu_threads=args.threads, local_files_only=em_cache)
    return modelo, precisao


def transcrever_arquivo(modelo, precisao, midia, args):
    from faster_whisper.audio import decode_audio

    midia = Path(midia)
    print(f"\nArquivo: {midia.name}", flush=True)
    print("Calculando o SHA-256 e lendo o áudio ...", flush=True)
    sha = sha256_do_arquivo(midia)
    try:
        audio = decode_audio(str(midia), sampling_rate=TAXA)
    except Exception as e:  # noqa: BLE001
        raise ErroEntrada(f"não foi possível ler o áudio de {midia.name}: {e}") from None
    duracao = len(audio) / TAXA
    if duracao <= 0:
        raise ErroEntrada(f"{midia.name} não tem faixa de áudio legível.")

    inicio = args.inicio or 0.0
    fim = min(args.fim, duracao) if args.fim is not None else duracao
    if inicio >= fim:
        raise ErroEntrada(f"trecho vazio: início {fmt_tempo(inicio)}, fim {fmt_tempo(fim)}, "
                          f"duração da mídia {fmt_tempo(duracao)}.")
    recortado = args.inicio is not None or args.fim is not None
    if recortado:
        audio = audio[int(inicio * TAXA):int(fim * TAXA)]
    alvo = fim - inicio
    print(f"Duração da mídia: {fmt_tempo(duracao)}. Trecho a transcrever: "
          f"{fmt_tempo(inicio)} a {fmt_tempo(fim)}.", flush=True)

    formatos = args.formatos
    pasta = Path(args.saida)
    pasta.mkdir(parents=True, exist_ok=True)
    base = base_de_saida(midia, pasta, inicio if recortado else None,
                         fim if args.fim is not None else None, formatos)
    meta = {
        "arquivo": midia.name,
        "sha256": sha,
        "duracao": round(duracao, 3),
        "trecho_inicio": round(inicio, 3),
        "trecho_fim": round(fim, 3),
        "modelo": args.modelo,
        "dispositivo": args.dispositivo,
        "precisao": precisao,
        "idioma": args.idioma,
        "filtro_de_silencio": not args.sem_filtro_de_silencio,
        "termos": args.termos or "",
        "gerada_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "versao_do_script": VERSAO,
    }

    segmentos, _info = modelo.transcribe(
        audio,
        language=args.idioma,
        task="transcribe",
        beam_size=5,
        vad_filter=not args.sem_filtro_de_silencio,
        condition_on_previous_text=False,  # evita que um erro contamine os trechos seguintes
        initial_prompt=args.termos or None,
        hotwords=args.termos or None,
        word_timestamps=True,  # minutagem pela primeira palavra dita, não pelo bloco
    )

    parcial = base.with_name(base.name + ".parcial.txt")
    trechos = []
    t0 = time.time()
    ultimo_aviso = t0
    with open(parcial, "w", encoding="utf-8") as f:
        f.write(cabecalho_txt(meta))
        f.flush()
        for s in segmentos:
            if not s.text.strip():
                continue
            palavras = [(w.start, w.end, w.word) for w in (s.words or [])]
            linhas = dividir_por_pausa(palavras) or [(s.start, s.end, s.text.strip())]
            for ini, final, texto in linhas:
                t = {
                    "inicio": round(inicio + ini, 3),
                    "fim": round(inicio + final, 3),
                    "texto": texto,
                    "logprob": round(float(s.avg_logprob), 3),
                    "compressao": round(float(s.compression_ratio), 3),
                    "prob_sem_fala": round(float(s.no_speech_prob), 3),
                }
                trechos.append(t)
                f.write(f"[{fmt_tempo(t['inicio'])}] {texto}\n")
            f.flush()
            agora = time.time()
            if agora - ultimo_aviso >= 30:
                ultimo_aviso = agora
                feito = min(alvo, max(0.001, s.end))
                decorrido = agora - t0
                falta = decorrido * (alvo - feito) / feito
                print(f"Progresso: {100 * feito / alvo:.0f}% ({fmt_tempo(feito)} de {fmt_tempo(alvo)}), "
                      f"decorrido {fmt_tempo(decorrido)}, falta cerca de {fmt_tempo(falta)}", flush=True)

    marcar(trechos)
    gasto = time.time() - t0
    meta["tempo_de_processamento"] = fmt_tempo(gasto)
    gravados = gravar_saidas(base, meta, trechos, formatos, parcial)
    marcados = sum(1 for t in trechos if t.get("conferir"))
    print(f"Concluído em {fmt_tempo(gasto)} ({gasto / alvo:.2f} vez a duração do trecho). "
          f"Trechos: {len(trechos)}; com sinal para conferir: {marcados}.", flush=True)
    if not trechos:
        print("Nenhuma fala foi reconhecida neste trecho.", flush=True)
    for g in gravados:
        print(f"Gravado: {g}", flush=True)
    return gravados


def cmd_transcrever(args):
    midias = [Path(m) for m in args.midias]
    for m in midias:
        if not m.is_file():
            raise ErroEntrada(f"arquivo não encontrado: {m}")
    if (args.inicio is not None or args.fim is not None) and len(midias) > 1:
        raise ErroEntrada("--inicio e --fim valem para uma mídia por vez.")
    if not tem_biblioteca():
        print(instrucoes_de_instalacao())
        return 3
    if args.modelo not in MODELOS:
        print(f"Aviso: modelo {args.modelo!r} fora da lista conhecida ({', '.join(MODELOS)}).")
    modelo, precisao = carregar_modelo(args)
    falhas = 0
    for m in midias:
        try:
            transcrever_arquivo(modelo, precisao, m, args)
        except ErroEntrada as e:
            falhas += 1
            print(f"ERRO: {e}", flush=True)
    return 2 if falhas else 0


# --------------------------------------------------------------------------
# Autoteste (não usa o modelo)
# --------------------------------------------------------------------------

def cmd_autoteste(_args):
    feitas, falhas = 0, []

    def confere(nome, condicao):
        nonlocal feitas
        feitas += 1
        if not condicao:
            falhas.append(nome)

    confere("tempo simples", fmt_tempo(71.5) == "00:01:11")
    confere("tempo com milissegundos", fmt_tempo(3661.25, True) == "01:01:01,250")
    confere("tempo negativo vira zero", fmt_tempo(-3) == "00:00:00")
    confere("arredondamento não passa de 59", fmt_tempo(59.9996, True) == "00:01:00,000")
    confere("lê segundos", ler_tempo("90") == 90.0)
    confere("lê MM:SS", ler_tempo("01:30") == 90.0)
    confere("lê HH:MM:SS", ler_tempo("01:02:03") == 3723.0)
    for ruim in ("", "a:b", "1:2:3:4", "-5", "1::2"):
        try:
            ler_tempo(ruim)
            confere(f"recusa tempo {ruim!r}", False)
        except ErroEntrada:
            confere(f"recusa tempo {ruim!r}", True)

    trechos = marcar([
        {"inicio": 0.0, "fim": 2.0, "texto": "Bom dia.", "logprob": -0.2, "compressao": 1.1},
        {"inicio": 2.0, "fim": 4.0, "texto": "Obrigado.", "logprob": -0.3, "compressao": 1.0},
        {"inicio": 4.0, "fim": 6.0, "texto": "obrigado", "logprob": -0.3, "compressao": 1.0},
        {"inicio": 6.0, "fim": 8.0, "texto": "Obrigado!", "logprob": -0.3, "compressao": 1.0},
        {"inicio": 8.0, "fim": 9.0, "texto": "Trecho ruim", "logprob": -1.4, "compressao": 2.9},
    ])
    confere("trecho bom sem sinal", trechos[0]["conferir"] == [])
    confere("repetição marca os três", all("repetição em sequência" in t["conferir"] for t in trechos[1:4]))
    confere("baixa confiança", "baixa confiança" in trechos[4]["conferir"])
    confere("texto repetitivo", "texto repetitivo" in trechos[4]["conferir"])
    confere("linha com sinal", linha_txt(trechos[4]).startswith("[00:00:08] Trecho ruim [conferir: "))
    confere("linha sem sinal", linha_txt(trechos[0]) == "[00:00:00] Bom dia.")
    confere("duas repetições não marcam", marcar([
        {"inicio": 0, "fim": 1, "texto": "Sim.", "logprob": -0.1, "compressao": 1.0},
        {"inicio": 1, "fim": 2, "texto": "Sim.", "logprob": -0.1, "compressao": 1.0},
    ])[1]["conferir"] == [])

    linhas = dividir_por_pausa([(10.0, 10.4, " Sim,"), (10.5, 11.0, " excelência."),
                                (23.5, 24.0, " A"), (24.0, 24.6, " senhora"), (25.0, 25.2, " viu?")])
    confere("pausa longa abre linha", len(linhas) == 2)
    confere("linha começa na primeira palavra", linhas[1][0] == 23.5 and linhas[1][1] == 25.2)
    confere("texto da linha", linhas[0][2] == "Sim, excelência." and linhas[1][2] == "A senhora viu?")
    confere("sem palavras, sem linhas", dividir_por_pausa([]) == [])
    solta = dividir_por_pausa([(43.0, 43.2, " A"), (56.0, 56.5, " senhora"), (56.6, 57.0, " viu?")])
    confere("palavra solta vai para a frase", solta == [(56.0, 57.0, "A senhora viu?")])
    resposta = dividir_por_pausa([(10.0, 10.4, " Sim."), (20.0, 20.5, " E"), (20.6, 21.0, " depois?")])
    confere("resposta curta fica na sua linha", [r[2] for r in resposta] == ["Sim.", "E depois?"])

    srt = texto_srt(trechos[:2])
    confere("srt numera", srt.startswith("1\n00:00:00,000 --> 00:00:02,000\nBom dia.\n"))
    confere("srt segundo bloco", "\n2\n00:00:02,000 --> 00:00:04,000\nObrigado.\n" in srt)

    meta = {
        "arquivo": "audiencia-ficticia.mp4", "sha256": "0" * 64, "duracao": 9.0,
        "trecho_inicio": 0.0, "trecho_fim": 9.0, "modelo": "turbo", "dispositivo": "cpu",
        "precisao": "int8", "idioma": "pt", "filtro_de_silencio": True, "termos": "",
        "gerada_em": "01/01/2026 10:00", "versao_do_script": VERSAO,
    }
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        base = base_de_saida("audiencia-ficticia.mp4", tmp)
        confere("nome-base", base.name == "audiencia-ficticia.transcricao")
        parcial = base.with_name(base.name + ".parcial.txt")
        parcial.write_text("rascunho", encoding="utf-8")
        gravados = gravar_saidas(base, meta, trechos, ("txt", "srt", "json"), parcial)
        confere("grava três arquivos", [g.suffix for g in gravados] == [".txt", ".srt", ".json"])
        confere("apaga o parcial", not parcial.exists())
        txt = gravados[0].read_text(encoding="utf-8")
        confere("cabeçalho avisa", txt.startswith("TRANSCRIÇÃO AUTOMÁTICA, NÃO CONFERIDA"))
        confere("cabeçalho traz o hash", "SHA-256 do arquivo: " + "0" * 64 in txt)
        confere("rodapé conta os sinais", "conferir primeiro: 4." in txt)
        dados = json.loads(gravados[2].read_text(encoding="utf-8"))
        confere("json traz trechos", len(dados["trechos"]) == 5 and dados["arquivo"] == meta["arquivo"])
        confere("não sobrescreve",
                base_de_saida("audiencia-ficticia.mp4", tmp).name == "audiencia-ficticia.transcricao-2")
        recorte = base_de_saida("audiencia-ficticia.mp4", tmp, 600, 1500)
        confere("nome do recorte", recorte.name == "audiencia-ficticia.trecho-001000-002500.transcricao")
        aberto = base_de_saida("audiencia-ficticia.mp4", tmp, 600, None)
        confere("recorte sem fim", aberto.name == "audiencia-ficticia.trecho-001000-fim.transcricao")
        arq = tmp / "abc.bin"
        arq.write_bytes(b"abc")
        confere("sha256", sha256_do_arquivo(arq) ==
                "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    confere("travessão ausente no aviso", "—" not in AVISO and " – " not in AVISO)
    confere("threads padrão", 1 <= threads_padrao() <= 8)

    print(f"autoteste: {feitas} verificações, {len(falhas)} falha(s)"
          + (": " + "; ".join(falhas) if falhas else ""))
    return 1 if falhas else 0


# --------------------------------------------------------------------------
# Linha de comando
# --------------------------------------------------------------------------

def lista_de_formatos(texto):
    formatos = tuple(f.strip().lower() for f in texto.split(",") if f.strip())
    invalidos = [f for f in formatos if f not in ("txt", "srt", "json")]
    if not formatos or invalidos:
        raise argparse.ArgumentTypeError("formatos aceitos: txt, srt, json")
    return formatos


def tempo_arg(texto):
    try:
        return ler_tempo(texto)
    except ErroEntrada as e:
        raise argparse.ArgumentTypeError(str(e)) from None


def montar_parser():
    p = argparse.ArgumentParser(description="Transcrição local de áudio e vídeo (Trilha Criminal).")
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("diagnostico", help="mostra o que está instalado neste computador")
    pp = sub.add_parser("preparar", help="cria o ambiente e instala a biblioteca")
    pp.add_argument("--modelo", default=None, help="também baixa o modelo indicado")
    pt = sub.add_parser("transcrever", help="transcreve uma ou mais mídias")
    pt.add_argument("midias", nargs="+", help="arquivos de áudio ou vídeo")
    pt.add_argument("--saida", required=True, help="pasta onde gravar a transcrição")
    pt.add_argument("--modelo", default=MODELO_PADRAO)
    pt.add_argument("--idioma", default="pt")
    pt.add_argument("--termos", default="", help="nomes próprios e termos do caso, para melhorar a grafia")
    pt.add_argument("--inicio", type=tempo_arg, default=None, help="início do trecho (HH:MM:SS)")
    pt.add_argument("--fim", type=tempo_arg, default=None, help="fim do trecho (HH:MM:SS)")
    pt.add_argument("--formatos", type=lista_de_formatos, default=("txt", "srt", "json"))
    pt.add_argument("--dispositivo", choices=("cpu", "cuda"), default="cpu")
    pt.add_argument("--threads", type=int, default=threads_padrao())
    pt.add_argument("--sem-filtro-de-silencio", action="store_true",
                    help="não pula os trechos sem fala (aumenta o risco de frases inventadas)")
    sub.add_parser("autoteste", help="confere as funções do script, sem usar o modelo")
    return p


def main():
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    args = montar_parser().parse_args()
    if args.comando in ("diagnostico", "transcrever"):
        codigo = reexecutar_no_ambiente()
        if codigo is not None:
            return codigo
    comandos = {"diagnostico": cmd_diagnostico, "preparar": cmd_preparar,
                "transcrever": cmd_transcrever, "autoteste": cmd_autoteste}
    try:
        return comandos[args.comando](args)
    except ErroEntrada as e:
        print(f"ERRO: {e}")
        return 2
    except KeyboardInterrupt:
        print("\nInterrompido. O arquivo .parcial.txt guarda o que já tinha sido transcrito.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
