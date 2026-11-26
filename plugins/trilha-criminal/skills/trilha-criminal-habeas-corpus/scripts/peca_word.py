#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Peça em Word da Trilha Criminal.

Gera a minuta em Word no padrão neutro da Trilha: A4, Times New Roman, texto
todo em preto, sem timbrado. Também audita um Word existente e procura, num
texto qualquer, as marcas de escrita automática (travessão, muletas de
transição, ênfase artificial, marcação de chat).

O script não redige, não pesquisa e não escolhe o que destacar: distribui nos
estilos o texto que recebe, na ordem em que recebe.

Uso:
  python peca_word.py modelo [peca|hc]                    imprime um modelo de entrada
  python peca_word.py gerar --entrada peca.json --saida peca.docx
  python peca_word.py gerar --entrada peca.json --saida peca.docx --base timbrado.docx
  python peca_word.py auditar peca.docx
  python peca_word.py revisar-texto --entrada minuta.md
  python peca_word.py autoteste

Gerar e auditar exigem python-docx (pip install python-docx). Revisar texto
usa só a biblioteca padrão. Python 3.8 ou superior.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime

try:
    from docx import Document
    from docx.enum.style import WD_STYLE_TYPE
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor
    from docx.text.paragraph import Paragraph
    TEM_DOCX = True
except ImportError:  # revisar-texto e parte do autoteste funcionam sem python-docx
    TEM_DOCX = False

VERSAO = "1.0.0"
FONTE = "Times New Roman"
PRETO = "000000"
ATRIBUTOS_FONTE = ("ascii", "hAnsi", "eastAsia", "cs")
ATRIBUTOS_TEMA = ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme", "csTheme")
ARTIGO = re.compile(r"\bArt\.\s+\d+(?:\.\d{3})*[º°]?(?:-[A-Za-z]+)?\.?", re.IGNORECASE)
LETRA_PEDIDO = re.compile(r"(?:[a-z]{1,2}|\d{1,2})\)")


class ErroEntrada(Exception):
    pass


# --------------------------------------------------------------------------
# Marcas de escrita automática (só biblioteca padrão)
# --------------------------------------------------------------------------
# Cada marca: (categoria, descrição, expressão). "corrigir" deve sair do texto
# destinado ao juízo; "conferir" costuma ser vício, mas pode ser necessário.

MARCAS = [
    ("corrigir", "travessão", re.compile(r"[—―]|\s–\s|\s-\s|--")),
    ("corrigir", "muleta de transição", re.compile(
        r"\bcumpre (?:destacar|ressaltar|salientar|registrar|observar|frisar|consignar|pontuar)\b"
        r"|\b(?:é )?(?:importante|relevante|fundamental|imperioso|oportuno|necessário) "
        r"(?:destacar|ressaltar|salientar|frisar|registrar|observar|mencionar|pontuar|lembrar)\b"
        r"|\bvale (?:destacar|ressaltar|salientar|frisar|lembrar|registrar|mencionar|pontuar|dizer)\b"
        r"|\b(?:ressalte|destaque|frise|registre|saliente|sublinhe)-se\b"
        r"|\binsta (?:salientar|destacar|ressaltar|consignar|registrar)\b"
        r"|\bdiapasão\b|\bnessa toada\b|\bnessa (?:mesma )?esteira\b|\bna mesma esteira\b",
        re.IGNORECASE)),
    ("corrigir", "ênfase artificial", re.compile(
        r"\bcristalin[oa]s?\b|\bcristalinamente\b|\bgritante|\bsalta aos olhos\b"
        r"|\bnão restam? (?:qualquer |nenhuma )?dúvidas?\b"
        r"|\bé (?:evidente|cristalino|inegável|indiscutível|inquestionável) que\b"
        r"|\bpatentes? ilegalidade|\baberrante|\bescandalos[oa]",
        re.IGNORECASE)),
    ("corrigir", "fórmula retórica", re.compile(
        r"\bnão por acaso\b|\be não é só\b|\bmais do que isso\b|\bdito de outro modo\b"
        r"|\bem outras palavras\b|\bpior ainda\b",
        re.IGNORECASE)),
    ("corrigir", "marcação de chat", re.compile(r"\*\*|__|^\s*#{1,6}\s|^\s*[-*•]\s|`", re.MULTILINE)),
    ("conferir", "contraste fabricado (não é X, mas Y)", re.compile(
        r"\bnão (?:se trata|é|foi|era|está|são)\b(?: apenas| somente| só| meramente)?[^.;:?!]{1,80}?,\s*(?:mas|e sim|senão)\b",
        re.IGNORECASE)),
    ("conferir", "pergunta retórica", re.compile(r"\?")),
]
PENDENCIA = re.compile(r"\[(?:CONFIRMAR|[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇ /]{2,})[^\]]*\]")


def trecho(texto, inicio, fim, folga=40):
    a, b = max(0, inicio - folga), min(len(texto), fim + folga)
    return ("…" if a else "") + texto[a:b].replace("\n", " ").strip() + ("…" if b < len(texto) else "")


def marcas_no_texto(texto):
    """Devolve [(categoria, descrição, trecho)] para as marcas encontradas no texto."""
    achados = []
    for categoria, descricao, expressao in MARCAS:
        for m in expressao.finditer(texto):
            achados.append((categoria, descricao, trecho(texto, m.start(), m.end())))
    return achados


def pendencias_no_texto(texto):
    return [m.group() for m in PENDENCIA.finditer(texto)]


def revisar_texto(texto):
    """Revisa texto corrido ou Markdown. Linhas de citação (começadas por >) ficam de fora."""
    autoral = "\n".join(l for l in texto.splitlines() if not l.lstrip().startswith(">"))
    return marcas_no_texto(autoral), pendencias_no_texto(autoral)


def relatorio(achados, pendencias, cabecalho):
    linhas = [cabecalho]
    corrigir = [a for a in achados if a[0] == "corrigir"]
    conferir = [a for a in achados if a[0] == "conferir"]
    if not achados and not pendencias:
        linhas.append("Nenhuma marca de escrita automática encontrada.")
    for titulo, grupo in (("Corrigir", corrigir), ("Conferir", conferir)):
        if grupo:
            linhas.append(f"{titulo} ({len(grupo)}):")
            linhas.extend(f"- {d}: {t}" for _, d, t in grupo)
    if pendencias:
        unicos = sorted(set(pendencias))
        linhas.append(f"Campos pendentes ({len(unicos)}): " + "; ".join(unicos))
    return "\n".join(linhas)


# --------------------------------------------------------------------------
# Estilos
# --------------------------------------------------------------------------

def _val(pai, nome, valor):
    el = pai.find(qn("w:" + nome))
    if el is None:
        el = OxmlElement("w:" + nome)
        pai.append(el)
    el.set(qn("w:val"), valor)
    return el


def _idioma(rpr):
    lang = _val(rpr, "lang", "pt-BR")
    for chave in ("eastAsia", "bidi"):
        lang.set(qn("w:" + chave), "pt-BR")
    for velho in rpr.findall(qn("w:noProof")):
        rpr.remove(velho)


def _fonte(rpr):
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for atributo in ATRIBUTOS_TEMA:
        rf.attrib.pop(qn("w:" + atributo), None)
    for atributo in ATRIBUTOS_FONTE:
        rf.set(qn("w:" + atributo), FONTE)


ESTILOS = {
    # nome: (tamanho, opções)
    "Normal": (12, dict(primeira=1.5)),
    "TC Título": (14, dict(negrito=True, alinha="centro", antes=12, depois=12, junto=True)),
    "TC Tópico": (13, dict(negrito=True, alinha="esquerda", antes=12, junto=True)),
    "TC Subtópico": (12, dict(negrito=True, alinha="esquerda", antes=10, depois=4, junto=True)),
    "TC Endereçamento": (12, dict(negrito=True, alinha="centro", depois=10, junto=True)),
    "TC Identificação": (11, dict(alinha="esquerda", depois=3)),
    "TC Abertura": (12, dict(junto=True)),
    "TC Pedido": (12, dict(primeira=1.5)),
    "TC Citação": (11, dict(recuo=4, linha=1, antes=6)),
    "TC Transcrição": (11, dict(recuo=4, linha=1, antes=6, italico=True)),
    "TC Ementa": (11, dict(recuo=4, linha=1, depois=0)),
    "TC Referência": (10, dict(alinha="direita", linha=1)),
    "TC Fecho": (12, dict(alinha="centro", depois=4, junto=True)),
    "TC Assinatura": (12, dict(alinha="centro", depois=2, junto=True)),
    "TC Tabela": (11, dict(alinha="esquerda", linha=1.1, depois=0)),
    "TC Nota": (11, dict(alinha="esquerda")),
    "TC Rodapé": (10, dict(alinha="direita", linha=1, depois=0, nivel=False)),
}
# Estilos que trazem texto alheio, fora da revisão de escrita automática.
ESTILOS_ALHEIOS = {"TC Citação", "TC Transcrição", "TC Ementa"}


def _estilo(doc, nome, tamanho, negrito=False, italico=False, alinha="justificado",
            antes=0, depois=6, linha=1.15, junto=False, recuo=0, primeira=0, nivel=True):
    alinhamentos = {"justificado": WD_ALIGN_PARAGRAPH.JUSTIFY, "centro": WD_ALIGN_PARAGRAPH.CENTER,
                    "esquerda": WD_ALIGN_PARAGRAPH.LEFT, "direita": WD_ALIGN_PARAGRAPH.RIGHT}
    if nome in [s.name for s in doc.styles]:
        s = doc.styles[nome]
    else:
        s = doc.styles.add_style(nome, WD_STYLE_TYPE.PARAGRAPH)
    if nome != "Normal":
        s.base_style = doc.styles["Normal"]
        s.quick_style = True
    s.font.name, s.font.size = FONTE, Pt(tamanho)
    s.font.bold, s.font.italic = negrito, italico
    s.font.color.rgb = RGBColor.from_string(PRETO)
    rpr = s.element.get_or_add_rPr()
    _fonte(rpr)
    _idioma(rpr)
    pf = s.paragraph_format
    pf.alignment = alinhamentos[alinha]
    pf.space_before, pf.space_after = Pt(antes), Pt(depois)
    pf.line_spacing = linha
    pf.left_indent, pf.right_indent, pf.first_line_indent = Cm(recuo), Cm(0), Cm(primeira)
    pf.keep_with_next, pf.keep_together, pf.widow_control = junto, junto, True
    pf.page_break_before = False
    if nivel:
        _val(s.element.get_or_add_pPr(), "outlineLvl", "9")  # nível Corpo de Texto: nada se recolhe no Word
    for borda in s.element.xpath("./w:pPr/w:pBdr"):
        borda.getparent().remove(borda)
    return s


def _numero_de_pagina(doc, secao):
    rodape = secao.footer
    rodape.is_linked_to_previous = False
    p = rodape.paragraphs[0] if rodape.paragraphs else rodape.add_paragraph()
    p.style = doc.styles["TC Rodapé"]
    for tipo, texto in (("begin", None), (None, " PAGE "), ("separate", None), (None, "1"), ("end", None)):
        r = OxmlElement("w:r")
        if tipo:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tipo)
        elif texto.strip() == "PAGE":
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = texto
        else:
            el = OxmlElement("w:t")
            el.text = texto
        r.append(el)
        p._p.append(r)


def _configuracoes(doc):
    """Hifenização automática, revisão ortográfica refeita e idioma do tema em pt-BR, na ordem do esquema."""
    st = doc.settings.element
    if st.find(qn("w:autoHyphenation")) is None:
        hifen = OxmlElement("w:autoHyphenation")
        hifen.set(qn("w:val"), "1")
        tab = st.find(qn("w:defaultTabStop"))
        if tab is not None:
            tab.addnext(hifen)
        else:
            depois = next((st.find(qn("w:" + n)) for n in ("characterSpacingControl", "compat", "rsids", "themeFontLang")
                           if st.find(qn("w:" + n)) is not None), None)
            depois.addprevious(hifen) if depois is not None else st.append(hifen)
    revisao = st.find(qn("w:proofState"))
    if revisao is not None:
        revisao.set(qn("w:spelling"), "dirty")
        revisao.set(qn("w:grammar"), "dirty")
    tema = st.find(qn("w:themeFontLang"))
    if tema is not None:
        tema.set(qn("w:val"), "pt-BR")
        tema.attrib.pop(qn("w:eastAsia"), None)


def novo_documento(base=None):
    """Documento vazio no padrão da Trilha. Com 'base', aproveita página, margens, cabeçalho e rodapé dela."""
    doc = Document(base) if base else Document()
    for filho in list(doc.element.body):
        if filho.tag != qn("w:sectPr"):
            doc.element.body.remove(filho)
    if not base:
        for secao in doc.sections:
            secao.page_width, secao.page_height = Cm(21), Cm(29.7)
            secao.top_margin = secao.left_margin = Cm(3)
            secao.bottom_margin = secao.right_margin = Cm(2)
            secao.header_distance = secao.footer_distance = Cm(1.25)
    for nome, (tamanho, opcoes) in ESTILOS.items():
        _estilo(doc, nome, tamanho, **opcoes)
    # Fonte e idioma em todos os estilos e nos padrões do documento, nunca run por run.
    for rpr in doc.styles.element.xpath(".//w:docDefaults/w:rPrDefault/w:rPr"):
        _fonte(rpr)
        _idioma(rpr)
    for rf in doc.styles.element.xpath("./w:style/w:rPr/w:rFonts"):
        _fonte(rf.getparent())
    for s in doc.styles:
        _idioma(s.element.get_or_add_rPr())
    _configuracoes(doc)
    if not base:
        _numero_de_pagina(doc, doc.sections[0])
    cp = doc.core_properties
    cp.title = cp.subject = cp.author = cp.last_modified_by = cp.comments = cp.keywords = cp.category = ""
    cp.revision = 1
    cp.created = cp.modified = datetime.now().replace(microsecond=0)
    return doc


# --------------------------------------------------------------------------
# Blocos
# --------------------------------------------------------------------------

TIPOS = {
    "enderecamento": "TC Endereçamento", "identificacao": "TC Identificação", "abertura": "TC Abertura",
    "titulo": "TC Título", "topico": "TC Tópico", "subtopico": "TC Subtópico", "corpo": "Normal",
    "artigo": "TC Citação", "citacao": "TC Citação", "transcricao": "TC Transcrição",
    "referencia": "TC Referência", "pedido": "TC Pedido", "fecho": "TC Fecho",
    "assinatura": "TC Assinatura", "nota": "TC Nota",
}
TIPOS_ESPECIAIS = ("ementa", "tabela", "anexos")


def _trechos(bloco):
    if "trechos" in bloco:
        itens = bloco["trechos"]
        if not isinstance(itens, list) or not all(isinstance(i, dict) and "texto" in i for i in itens):
            raise ErroEntrada("'trechos' deve ser uma lista de objetos com 'texto'.")
        return itens
    if "texto" not in bloco:
        raise ErroEntrada(f"bloco '{bloco.get('tipo', 'corpo')}' sem 'texto' nem 'trechos'.")
    return [{"texto": bloco["texto"]}]


def _paragrafo(doc, estilo, bloco):
    p = doc.add_paragraph(style=estilo)
    if bloco.get("quebra_antes"):
        p.paragraph_format.page_break_before = True
    return p


def _texto(doc, bloco):
    tipo = bloco.get("tipo", "corpo")
    itens = _trechos(bloco)
    texto = "".join(str(i["texto"]) for i in itens)
    if "\n" in texto:
        raise ErroEntrada(f"bloco '{tipo}' com quebra de linha: cada parágrafo é um bloco próprio.")
    if tipo in ("topico", "subtopico"):
        padrao = r"^(\d+)\.?\s+(.+)$" if tipo == "topico" else r"^(\d+(?:\.\d+)+)\.?\s+(.+)$"
        m = re.fullmatch(padrao, texto.strip())
        if not m:
            raise ErroEntrada("tópico precisa da numeração escrita pelo autor, como '1. TÍTULO' ou '2.1. Subtítulo'.")
        rotulo = m.group(2).upper() if tipo == "topico" else m.group(2)
        itens = [{"texto": f"{m.group(1)}. {rotulo}"}]
    elif tipo == "titulo":
        itens = [{"texto": texto.strip().upper()}]
    p = _paragrafo(doc, TIPOS[tipo], bloco)
    artigo = ARTIGO.search(texto) if tipo in ("artigo", "citacao") and "trechos" not in bloco else None
    if tipo == "artigo" or artigo:
        if artigo:
            p.add_run(texto[:artigo.start()])
            p.add_run(artigo.group()).bold = True
            p.add_run(texto[artigo.end():])
        else:
            p.add_run(texto)
        return p
    if tipo == "pedido" and "trechos" not in bloco:
        m = LETRA_PEDIDO.match(texto)
        if m:
            p.add_run(m.group()).bold = True
            p.add_run(texto[m.end():])
            return p
    for item in itens:
        r = p.add_run(str(item["texto"]))
        if "negrito" in item:
            r.bold = bool(item["negrito"])
        if tipo == "transcricao":
            r.italic = True
        elif "italico" in item:
            r.italic = bool(item["italico"])
    return p


def _ementa(doc, bloco):
    texto, tribunal = bloco.get("texto", ""), bloco.get("tribunal")
    partes = [t.strip() for t in str(texto).splitlines() if t.strip()]
    if not partes:
        raise ErroEntrada("ementa sem 'texto' integral.")
    if tribunal:
        p = _paragrafo(doc, "TC Ementa", bloco)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.keep_with_next = True
        p.add_run(str(tribunal)).bold = True
    for i, parte in enumerate(partes):
        p = _paragrafo(doc, "TC Ementa", bloco if i == 0 and not tribunal else {})
        if i == 0 and not tribunal:
            p.paragraph_format.space_before = Pt(6)
        p.add_run(parte)
    p.paragraph_format.space_after = Pt(6)


def _tabela(doc, bloco):
    cabecalho, linhas = bloco.get("cabecalho") or [], bloco.get("linhas") or []
    if not cabecalho or any(len(l) != len(cabecalho) for l in linhas):
        raise ErroEntrada("tabela precisa de 'cabecalho' e de 'linhas' com o mesmo número de colunas.")
    t = doc.add_table(rows=1, cols=len(cabecalho))
    t.style = "Table Grid"
    for celula, texto in zip(t.rows[0].cells, cabecalho):
        celula.text = str(texto)
    for valores in linhas:
        for celula, texto in zip(t.add_row().cells, valores):
            celula.text = str(texto)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
    for indice, linha in enumerate(t.rows):
        linha._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for celula in linha.cells:
            for p in celula.paragraphs:
                p.style = doc.styles["TC Tabela"]
                for r in p.runs:
                    r.bold = True if indice == 0 else None
    bordas = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement("w:" + lado)
        for chave, valor in (("val", "single"), ("sz", "4"), ("color", PRETO)):
            e.set(qn("w:" + chave), valor)
        bordas.append(e)
    t._tbl.tblPr.append(bordas)


def _anexos(doc, bloco):
    itens = bloco.get("itens") or []
    if not itens:
        raise ErroEntrada("rol de anexos sem 'itens' no formato 'Doc. NN: descrição'.")
    titulo = _paragrafo(doc, "TC Nota", bloco)
    titulo.paragraph_format.space_before = Pt(18)
    titulo.paragraph_format.keep_with_next = True
    titulo.add_run(bloco.get("titulo", "Rol de documentos anexos")).bold = True
    for item in itens:
        texto = item if isinstance(item, str) else f"Doc. {item.get('doc')}: {item.get('texto')}"
        if not re.match(r"^Doc\.\s+\d+(?:-[A-Z])?:\s+\S", texto):
            raise ErroEntrada(f"item do rol fora do formato 'Doc. NN: descrição': {texto!r}")
        doc.add_paragraph(texto, "TC Nota")


def avisos_habeas_corpus(blocos):
    """Cabeçalho e preâmbulo em três blocos quando a peça é habeas corpus."""
    def texto(b):
        return "".join(str(i["texto"]) for i in b.get("trechos", [{"texto": b.get("texto", "")}])).strip()
    tipos = [b.get("tipo", "corpo") for b in blocos]
    i = next((k for k, b in enumerate(blocos)
              if tipos[k] == "titulo" and texto(b).upper().startswith("HABEAS CORPUS")), None)
    if i is None:
        return []
    avisos = []
    ident = [texto(b) for b, t in zip(blocos[:i], tipos) if t == "identificacao"]
    for rotulo in ("Paciente:", "Autoridade coatora:"):
        if not any(l.startswith(rotulo) for l in ident):
            avisos.append(f"falta a linha '{rotulo}' em bloco 'identificacao' antes do título.")
    if i == 0 or tipos[i - 1] != "abertura" or not texto(blocos[i - 1]).rstrip(" ,").endswith("impetrar"):
        avisos.append("o bloco anterior ao título deve ser 'abertura' e terminar em 'impetrar'.")
    if i + 1 >= len(blocos) or tipos[i + 1] != "abertura" or not texto(blocos[i + 1]).lower().startswith("em favor de"):
        avisos.append("o bloco seguinte ao título deve ser 'abertura' e começar com 'em favor de'.")
    return avisos


def montar(doc, blocos):
    if not isinstance(blocos, list) or not blocos:
        raise ErroEntrada("a entrada precisa de uma lista 'blocos' não vazia.")
    anterior = None
    for n, bloco in enumerate(blocos, 1):
        if not isinstance(bloco, dict):
            raise ErroEntrada(f"bloco {n} não é um objeto.")
        tipo = bloco.get("tipo", "corpo")
        if tipo not in TIPOS and tipo not in TIPOS_ESPECIAIS:
            raise ErroEntrada(f"bloco {n}: tipo desconhecido '{tipo}'. Tipos: "
                              + ", ".join(list(TIPOS) + list(TIPOS_ESPECIAIS)))
        if tipo == "fecho" and anterior not in (None, "fecho") and doc.paragraphs:
            # o fecho e as assinaturas não ficam sozinhos numa página sem texto da peça
            doc.paragraphs[-1].paragraph_format.keep_with_next = True
        try:
            if tipo == "ementa":
                _ementa(doc, bloco)
            elif tipo == "tabela":
                _tabela(doc, bloco)
            elif tipo == "anexos":
                if anterior != "assinatura":
                    raise ErroEntrada("o rol de documentos anexos vem logo depois das assinaturas.")
                doc.paragraphs[-1].paragraph_format.keep_with_next = False
                _anexos(doc, bloco)
            else:
                p = _texto(doc, bloco)
                if anterior == "tabela":
                    p.paragraph_format.space_before = Pt(10)  # respiro depois do quadro, sem parágrafo vazio
                elif tipo == "fecho" and anterior != "fecho":
                    p.paragraph_format.space_before = Pt(12)
                elif tipo == "assinatura" and anterior == "fecho":
                    p.paragraph_format.space_before = Pt(24)
                elif tipo == "abertura" and anterior == "identificacao":
                    p.paragraph_format.space_before = Pt(10)
        except ErroEntrada as erro:
            raise ErroEntrada(f"bloco {n} ({tipo}): {erro}") from None
        anterior = tipo
    return doc


# --------------------------------------------------------------------------
# Auditoria de um Word
# --------------------------------------------------------------------------

def _fonte_efetiva(doc, estilo):
    while estilo is not None:
        if estilo.font.name:
            return estilo.font.name
        estilo = estilo.base_style
    padrao = doc.styles.element.xpath(".//w:docDefaults/w:rPrDefault/w:rPr/w:rFonts/@w:ascii")
    return padrao[0] if padrao else "fonte do tema"


def _paragrafos_do_corpo(doc):
    for el in doc.element.body.iter(qn("w:p")):
        yield Paragraph(el, doc)


def auditar(doc):
    """Lista desvios de forma e marcas de escrita automática, sem alterar o arquivo."""
    forma, achados, pendencias = [], [], []
    paragrafos = list(_paragrafos_do_corpo(doc))
    usados = {p.style.name: p.style for p in paragrafos if p.style is not None}
    fontes = {nome: _fonte_efetiva(doc, s) for nome, s in usados.items()}
    outras = sorted({f for f in fontes.values() if f != FONTE})
    if outras:
        forma.append("estilos com fonte diferente de Times New Roman: " + ", ".join(outras))
    diretas = {v for v in doc.element.body.xpath(".//w:r/w:rPr/w:rFonts/@w:ascii") if v != FONTE}
    if diretas:
        forma.append("texto com fonte aplicada à mão: " + ", ".join(sorted(diretas)))
    cores = {c.upper() for c in doc.element.body.xpath(".//w:r/w:rPr/w:color/@w:val")} - {PRETO, "AUTO"}
    for s in usados.values():
        if s.font.color is not None and s.font.color.rgb is not None and str(s.font.color.rgb) != PRETO:
            cores.add(str(s.font.color.rgb))
    if cores:
        forma.append("texto em cor diferente de preto: " + ", ".join(sorted(cores)))
    titulos = sorted(n for n in usados if re.match(r"(Heading|Título)\s*\d", n))
    if titulos:
        forma.append("estilos de título do Word que recolhem seções: " + ", ".join(titulos))
    vazios = [p for p in paragrafos if not p.text.strip() and p._p.getparent().tag == qn("w:body")
              and not p._p.xpath(".//w:drawing | .//w:br[@w:type='page'] | .//w:sectPr")]
    if vazios:
        forma.append(f"{len(vazios)} parágrafo(s) vazio(s) usados como espaço")
    inteiros = [p.text[:50] for p in paragrafos
                if p.style is not None and p.style.name in ("Normal", "TC Pedido") and len(p.text) > 60
                and all(r.bold for r in p.runs if r.text.strip())]
    for t in inteiros:
        forma.append(f"parágrafo inteiro em negrito: {t}…")
    for p in paragrafos:
        if p.style is not None and p.style.name in ESTILOS_ALHEIOS:
            continue
        achados.extend(marcas_no_texto(p.text))
        pendencias.extend(pendencias_no_texto(p.text))
    secao = doc.sections[0]
    if abs(secao.page_width - Cm(21)) > Cm(0.1) or abs(secao.page_height - Cm(29.7)) > Cm(0.1):
        forma.append("página fora do A4")
    return forma, achados, pendencias


def relatorio_word(forma, achados, pendencias):
    linhas = []
    if forma:
        linhas.append(f"Forma ({len(forma)}):")
        linhas.extend("- " + f for f in forma)
    else:
        linhas.append("Forma: nenhum desvio encontrado.")
    linhas.append(relatorio(achados, pendencias, "Escrita (fora das citações, transcrições e ementas):"))
    return "\n".join(linhas)


# --------------------------------------------------------------------------
# Modelos de entrada
# --------------------------------------------------------------------------

MODELOS = {
    "peca": {"blocos": [
        {"tipo": "enderecamento", "texto": "EXCELENTÍSSIMO SENHOR JUIZ DE DIREITO DA [VARA] DA COMARCA DE [COMARCA]"},
        {"tipo": "identificacao", "texto": "Processo nº [número]"},
        {"tipo": "abertura", "trechos": [
            {"texto": "[NOME DO ACUSADO]", "negrito": True},
            {"texto": ", já qualificado nos autos, por seu advogado, com endereço profissional na [endereço], vem apresentar"}]},
        {"tipo": "titulo", "texto": "Resposta à acusação"},
        {"tipo": "abertura", "texto": "com fundamento nos arts. 396 e 396-A do Código de Processo Penal, pelas razões a seguir."},
        {"tipo": "topico", "texto": "1. Síntese da acusação"},
        {"tipo": "corpo", "texto": "[Parágrafo com uma ideia completa, datado e localizado nos autos.]"},
        {"tipo": "subtopico", "texto": "1.1. [Questão concreta]"},
        {"tipo": "corpo", "trechos": [
            {"texto": "O relato registra "}, {"texto": "[premissa decisiva]", "negrito": True},
            {"texto": ", e a consequência é [consequência]."}]},
        {"tipo": "transcricao", "texto": "[Trecho literal da decisão ou do depoimento.]"},
        {"tipo": "referencia", "texto": "(Decisão de [dd/mm/aaaa], mov. [x])"},
        {"tipo": "artigo", "texto": "Art. 396-A. [Texto conferido na fonte oficial.]"},
        {"tipo": "ementa", "tribunal": "[Tribunal, classe, número, relator, data]", "texto": "[Ementa integral, aberta no portal do tribunal.]"},
        {"tipo": "topico", "texto": "2. Pedidos"},
        {"tipo": "pedido", "texto": "a) [pedido principal];"},
        {"tipo": "pedido", "texto": "b) [pedido subsidiário]."},
        {"tipo": "fecho", "texto": "[Cidade], [data]."},
        {"tipo": "assinatura", "trechos": [{"texto": "[NOME DO ADVOGADO]", "negrito": True}]},
        {"tipo": "assinatura", "texto": "OAB/[UF] [número]"},
        {"tipo": "anexos", "itens": ["Doc. 01: [descrição]"]},
    ]},
    "hc": {"blocos": [
        {"tipo": "enderecamento", "texto": "EXCELENTÍSSIMO SENHOR DESEMBARGADOR PRESIDENTE DO TRIBUNAL DE JUSTIÇA DO ESTADO DE [UF]"},
        {"tipo": "identificacao", "texto": "Paciente: [nome] ([situação de liberdade])"},
        {"tipo": "identificacao", "texto": "Autoridade coatora: [juízo]"},
        {"tipo": "identificacao", "texto": "Processo de origem: [número]"},
        {"tipo": "abertura", "trechos": [
            {"texto": "[NOME DO ADVOGADO]", "negrito": True},
            {"texto": ", advogado inscrito na OAB/[UF] sob o nº [número], com escritório profissional na [endereço], onde recebe intimações, vem, com fundamento no art. 5º, LXVIII, da Constituição Federal e nos arts. 647 e seguintes do Código de Processo Penal, impetrar"}]},
        {"tipo": "titulo", "texto": "Habeas corpus com pedido liminar"},
        {"tipo": "abertura", "trechos": [
            {"texto": "em favor de "}, {"texto": "[NOME DO PACIENTE]", "negrito": True},
            {"texto": ", [qualificação], [situação de liberdade], contra a decisão do [juízo] que, em [data], [ato] ([processo], [identificador]), pelas razões a seguir expostas."}]},
        {"tipo": "topico", "texto": "1. Síntese da impetração"},
        {"tipo": "corpo", "texto": "[Restrição atual, teses centrais e documentos.]"},
        {"tipo": "topico", "texto": "6. Dos pedidos"},
        {"tipo": "pedido", "texto": "a) [liminar];"},
        {"tipo": "pedido", "texto": "b) [mérito]."},
        {"tipo": "fecho", "texto": "[Cidade], [data]."},
        {"tipo": "assinatura", "trechos": [{"texto": "[NOME DO ADVOGADO]", "negrito": True}]},
        {"tipo": "assinatura", "texto": "OAB/[UF] [número]"},
        {"tipo": "anexos", "itens": ["Doc. 01: [decisão impugnada]"]},
    ]},
}


# --------------------------------------------------------------------------
# Autoteste
# --------------------------------------------------------------------------

def autoteste():
    feitos = []

    def confere(nome, condicao):
        if not condicao:
            raise AssertionError(nome)
        feitos.append(nome)

    def tem(texto, descricao):
        return any(d == descricao for _, d, _ in marcas_no_texto(texto))

    confere("travessão longo", tem("A prova — que é frágil — não basta.", "travessão"))
    confere("meia-risca entre espaços", tem("A prova – frágil – não basta.", "travessão"))
    confere("hífen no lugar de travessão", tem("A prova - frágil - não basta.", "travessão"))
    confere("intervalo de folhas não é travessão", not tem("Fls. 10–12 e mov. 7.1-A.", "travessão"))
    confere("palavra composta não é travessão", not tem("O auto de prisão em flagrante foi lavrado.", "travessão"))
    confere("muleta de transição", tem("Cumpre destacar que o laudo não veio.", "muleta de transição"))
    confere("muleta com -se", tem("Ressalte-se que o laudo não veio.", "muleta de transição"))
    confere("ênfase artificial", tem("É evidente que o réu não estava lá.", "ênfase artificial"))
    confere("fórmula retórica", tem("E não é só: o laudo também falta.", "fórmula retórica"))
    confere("marcação de chat", tem("O ponto **decisivo** é a data.", "marcação de chat"))
    confere("contraste fabricado", tem("Não se trata de mera irregularidade, mas de nulidade.",
                                       "contraste fabricado (não é X, mas Y)"))
    confere("pergunta retórica", tem("Como sustentar a prisão?", "pergunta retórica"))
    confere("flagrante técnico não é ênfase", not tem("A prisão em flagrante foi convertida.", "ênfase artificial"))
    confere("texto limpo", not marcas_no_texto(
        "O relato registra uma comunicação, mas não revela seu conteúdo. Sem outro elemento, ele não "
        "demonstra a participação atribuída ao acusado (mov. 7.1)."))
    confere("pendência", pendencias_no_texto("Intimado em [CONFIRMAR: data]. [NOME DO ADVOGADO]")
            == ["[CONFIRMAR: data]", "[NOME DO ADVOGADO]"])
    confere("citação fora da revisão", not revisar_texto("> A prova — dizia a sentença — basta.\nTexto limpo.")[0])
    confere("aviso de habeas corpus", not avisos_habeas_corpus(MODELOS["hc"]["blocos"]))
    confere("aviso de habeas corpus incompleto",
            len(avisos_habeas_corpus([{"tipo": "titulo", "texto": "Habeas corpus"}])) == 4)
    if not TEM_DOCX:
        return feitos, "geração não testada: python-docx ausente neste Python"

    pasta = tempfile.mkdtemp()
    caminho = os.path.join(pasta, "teste.docx")
    try:
        for nome, modelo in MODELOS.items():
            montar(novo_documento(), modelo["blocos"]).save(caminho)
            doc = Document(caminho)
            forma, achados, _ = auditar(doc)
            confere(f"modelo {nome} sem desvio de forma", not forma)
            confere(f"modelo {nome} sem marca de escrita", not achados)
        confere("A4", abs(doc.sections[0].page_width - Cm(21)) < Cm(0.05))
        confere("margem esquerda de 3 cm", abs(doc.sections[0].left_margin - Cm(3)) < Cm(0.05))
        confere("fonte do corpo", doc.styles["Normal"].font.name == FONTE)
        confere("corpo justificado com recuo", abs(doc.styles["Normal"].paragraph_format.first_line_indent - Cm(1.5)) < Cm(0.01))
        confere("título em maiúsculas", any(p.text == "HABEAS CORPUS COM PEDIDO LIMINAR" for p in doc.paragraphs))
        pedido = next(p for p in doc.paragraphs if p.style.name == "TC Pedido")
        confere("letra do pedido em negrito", pedido.runs[0].text == "a)" and pedido.runs[0].bold)
        confere("número de página no rodapé", "PAGE" in doc.sections[0].footer._element.xml)
        confere("autor em branco", not doc.core_properties.author)
        try:
            montar(novo_documento(), [{"tipo": "topico", "texto": "Sem número"}])
            confere("tópico sem número recusado", False)
        except ErroEntrada:
            feitos.append("tópico sem número recusado")
        try:
            montar(novo_documento(), [{"tipo": "corpo", "texto": "a\nb"}])
            confere("quebra de linha recusada", False)
        except ErroEntrada:
            feitos.append("quebra de linha recusada")
        ruim = novo_documento()
        p = ruim.add_paragraph("A prova — frágil — não basta.")
        p.runs[0].font.color.rgb = RGBColor.from_string("1B365D")
        ruim.add_paragraph()
        ruim.save(caminho)
        forma, achados, _ = auditar(Document(caminho))
        confere("auditoria acha cor", any("cor" in f for f in forma))
        confere("auditoria acha parágrafo vazio", any("vazio" in f for f in forma))
        confere("auditoria acha travessão", any(d == "travessão" for _, d, _ in achados))
    finally:
        if os.path.exists(caminho):
            os.remove(caminho)
        os.rmdir(pasta)
    return feitos, None


# --------------------------------------------------------------------------
# Linha de comando
# --------------------------------------------------------------------------

def _ler(caminho):
    if caminho:
        with open(caminho, encoding="utf-8-sig") as arq:
            return arq.read()
    return sys.stdin.buffer.read().decode("utf-8-sig")


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(prog="peca_word.py", description="Peça em Word no padrão neutro da Trilha Criminal.")
    ap.add_argument("comando", choices=["gerar", "auditar", "revisar-texto", "modelo", "autoteste"])
    ap.add_argument("alvo", nargs="?", help="com 'auditar': o .docx; com 'modelo': peca ou hc")
    ap.add_argument("--entrada", help="arquivo JSON (gerar) ou de texto (revisar-texto); sem ele, lê da entrada padrão")
    ap.add_argument("--saida", help="caminho do .docx a gerar")
    ap.add_argument("--base", help="Word com timbrado ou modelo do usuário, cujas página, margens, cabeçalho e rodapé são mantidos")
    args = ap.parse_args(argv)

    if args.comando == "autoteste":
        try:
            feitos, ressalva = autoteste()
        except AssertionError as erro:
            print(f"FALHA NO AUTOTESTE: {erro}")
            return 1
        print(f"Autoteste: {len(feitos)} verificações, todas corretas" + (f" ({ressalva})." if ressalva else "."))
        return 0
    if args.comando == "modelo":
        nome = args.alvo or "peca"
        if nome not in MODELOS:
            print("Modelos: " + ", ".join(MODELOS))
            return 2
        print(json.dumps(MODELOS[nome], ensure_ascii=False, indent=2))
        return 0
    if args.comando == "revisar-texto":
        achados, pendencias = revisar_texto(_ler(args.entrada))
        print(relatorio(achados, pendencias, "Escrita (fora das linhas de citação iniciadas por >):"))
        return 0
    if not TEM_DOCX:
        print("python-docx não está instalado. Rode 'pip install python-docx' e repita; se não for possível, "
              "entregue a minuta no chat e diga que o Word não foi gerado.", file=sys.stderr)
        return 3
    if args.comando == "auditar":
        if not args.alvo:
            ap.error("informe o .docx a auditar")
        print(relatorio_word(*auditar(Document(args.alvo))))
        return 0
    if not args.saida:
        ap.error("informe --saida para gerar a peça")
    try:
        try:
            entrada = json.loads(_ler(args.entrada))
        except json.JSONDecodeError as erro:
            raise ErroEntrada(f"JSON inválido: {erro}") from None
        blocos = entrada.get("blocos") if isinstance(entrada, dict) else None
        doc = montar(novo_documento(args.base), blocos)
    except ErroEntrada as erro:
        print(f"ERRO DE ENTRADA: {erro}", file=sys.stderr)
        print("Nada foi gerado. Corrija a entrada; não complete dado por suposição.", file=sys.stderr)
        return 2
    pasta = os.path.dirname(os.path.abspath(args.saida))
    os.makedirs(pasta, exist_ok=True)
    doc.save(args.saida)
    print(args.saida)
    for aviso in avisos_habeas_corpus(blocos):
        print("Aviso (habeas corpus): " + aviso)
    print(relatorio_word(*auditar(Document(args.saida))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
