---
name: trilha-criminal-transcricao
description: "Transcreve áudio e vídeo de audiências, depoimentos, interrogatórios e outras mídias do processo no próprio computador do advogado, sem enviar o arquivo a nenhum serviço, com minutagem em cada trecho e registro do arquivo de origem. Use quando o usuário pedir para transcrever, degravar ou passar para texto uma gravação, ou para localizar em que minuto algo foi dito. Exige ambiente que execute programas no computador do usuário; não identifica quem fala e não substitui a conferência na mídia original."
---

# Trilha Criminal Transcrição

## Objetivo e limites

Transforme a gravação em texto com minutagem, para o advogado ler, localizar trechos e conferir na mídia. A transcrição é feita por programa, no computador do usuário, com o script [scripts/transcrever.py](scripts/transcrever.py). O resultado orienta a leitura; não prova o que foi dito.

- **Sigilo.** A mídia não sai do computador. A internet é usada só na primeira vez, para baixar o programa e o modelo. Não envie a mídia a serviço de transcrição na nuvem, pago ou gratuito, sem autorização específica do usuário para aquele arquivo.
- **Sem identificação de falante.** O programa não sabe quem fala. Não atribua fala a juiz, promotor, defensor ou depoente no arquivo da transcrição.
- **Sem literalidade presumida.** Transcrição automática erra nomes, números, negações e trechos com ruído ou vozes sobrepostas, e pode criar frases em silêncio. Aspas em peça exigem conferência do trecho na mídia, na minutagem indicada.
- **O pedido define o trabalho.** Transcrever não autoriza estudo do caso, resumo, peça ou preparação de audiência. Ofereça o passo seguinte e aguarde.
- **Originais preservados.** Não edite, converta no lugar, renomeie nem mova a mídia recebida.

## 1. Conferir onde a conversa está rodando

A transcrição depende de executar um programa na máquina do usuário e de ler o arquivo no disco dele. Verifique; não presuma.

| Situação | O que fazer |
|---|---|
| Há terminal no computador do usuário e a mídia está numa pasta acessível | Siga para o passo 2 |
| O ambiente é isolado ou remoto (conversa no site, ou sandbox sem acesso às pastas do usuário) | Tente o `diagnostico` só se houver execução de código e a mídia já estiver ali. Se a instalação ou o download do modelo forem bloqueados, ou se a mídia não couber no envio, diga isso em uma frase e oriente o usuário a abrir a mesma conversa no aplicativo de computador, no modo que trabalha com as pastas da máquina |
| Não há execução de código | Diga que a transcrição não pode ser feita ali e oriente do mesmo modo. Não simule transcrição nem descreva o conteúdo de mídia que não foi processada |

Nunca entregue como transcrição um texto que não saiu do script.

## 2. Delimitar o pedido

Extraia do pedido, e pergunte só o que faltar e mudar o resultado:

- Quais arquivos. Audiência costuma vir em vários; liste o que encontrou na pasta e confirme antes de processar tudo.
- A mídia inteira ou um trecho (por exemplo, só o depoimento de uma testemunha, de 00:10:00 a 00:25:00). Trecho menor termina antes.
- Nomes próprios, apelidos, lugares e termos do caso, para a grafia. Use apenas os que o usuário informou ou que constam de documento do caso já disponível.
- Onde gravar. Na falta de indicação, crie a subpasta `transcricoes` ao lado da mídia.

## 3. Preparar o computador na primeira vez

Use o caminho completo da pasta em que este arquivo foi lido. Comece sempre por:

```
python "<pasta desta habilidade>/scripts/transcrever.py" diagnostico
```

Em alguns sistemas o comando é `python3`. No Windows, se `python` apenas abrir a loja de aplicativos ou não responder, trate o Python como ausente e verifique se há `uv` com `uv --version`. O diagnóstico informa se a biblioteca e o modelo já estão no computador, se há `uv`, quantos núcleos há e o espaço livre.

Se faltar instalar, avise o usuário antes, em linguagem simples: a primeira vez baixa cerca de 250 MB do programa e 1,6 GB do modelo, só uma vez, e a mídia continua no computador. Com a concordância dele:

- **Com `uv` instalado:** não há passo de preparação. Use `uv run --script` no lugar de `python` nos comandos do passo 4; ele monta o ambiente sozinho.
- **Só com Python (3.9 a 3.13):** rode `python "<pasta>/scripts/transcrever.py" preparar --modelo turbo`. Ele cria um ambiente próprio na pasta do usuário, sem alterar o Python do sistema. Depois disso, o comando `transcrever` usa esse ambiente sozinho.
- **Sem Python e sem `uv`:** proponha instalar o `uv` pelo instalador oficial da Astral e instale somente com a autorização do usuário. Se ele preferir não instalar nada, a transcrição não é feita.

Se a instalação falhar, mostre a mensagem de erro em resumo e pare. Não tente contornar bloqueio de rede, antivírus ou política da máquina.

## 4. Transcrever

```
python "<pasta>/scripts/transcrever.py" transcrever "<mídia>" --saida "<pasta de saída>" --termos "<nomes e termos do caso>"
```

| Opção | Uso |
|---|---|
| `--inicio 00:10:00 --fim 00:25:00` | Transcreve só o trecho; a minutagem continua sendo a da mídia original |
| `--termos "..."` | Melhora a grafia de nomes e termos. Não escreva frases que possam ser copiadas para o texto |
| `--modelo small` | Computador fraco ou pressa: mais rápido e menos preciso. O padrão é `turbo` |
| `--dispositivo cuda` | Só se o diagnóstico indicar placa NVIDIA utilizável. Se falhar, volte ao padrão |
| `--formatos txt` | Grava só o texto. O padrão grava `txt`, `srt` e `json` |
| `--sem-filtro-de-silencio` | Só se o usuário notar fala que ficou de fora; aumenta o risco de frase inventada em silêncio |

Cuidados de execução:

- O tempo depende do computador e pode chegar a várias vezes a duração da mídia em máquina modesta. Diga isso antes de começar gravação longa. O script informa o progresso e a previsão a cada meio minuto; repasse a previsão ao usuário, sem prometer prazo.
- Rode gravação longa em segundo plano e acompanhe a saída. Não rode duas transcrições ao mesmo tempo.
- Vários arquivos podem ir no mesmo comando; são processados em sequência.
- Se a execução for interrompida, o arquivo `.parcial.txt` guarda o que já foi transcrito. Diga ao usuário até que minuto ele vai e retome com `--inicio` a partir dali.
- O script não sobrescreve transcrição anterior: grava com sufixo `-2`, `-3`.

## 5. Conferir e entregar

Abra o `.txt` gerado antes de responder. Confira se há texto, se a minutagem final é compatível com a duração e quantos trechos vieram marcados com `[conferir: ...]`. A marca indica onde o próprio programa teve baixa confiança ou repetiu texto; trecho sem marca não está conferido.

Entregue no chat, de forma curta:

- os arquivos gravados e a pasta;
- a duração, o trecho coberto e o tempo que levou;
- o aviso de que o texto é automático, não identifica falantes e precisa ser conferido na mídia antes de qualquer citação;
- os trechos marcados, com a minutagem, quando forem poucos; quando forem muitos, a quantidade e os intervalos em que se concentram;
- sinais de problema que você notou na leitura: frase repetida em sequência, trecho sem sentido, salto longo de minutagem, nome grafado de formas diferentes.

Não cole a transcrição inteira no chat, salvo pedido. Não corrija o arquivo gerado. Se o usuário pedir uma versão organizada (parágrafos, falas separadas, correção de grafia), grave outro arquivo, com nome que indique isso, mantenha a minutagem e escreva no topo que é versão organizada a partir da transcrição automática. Nessa versão, a indicação de quem fala é inferência pelo contexto: marque como `[falante provável: ...]` somente onde o próprio texto sustenta, e deixe sem indicação onde não sustenta.

## 6. Uso do resultado no caso

- O cabeçalho do `.txt` registra o nome do arquivo, o SHA-256 da mídia, o modelo e a data. Esses dados identificam de qual arquivo a transcrição saiu; não certificam o conteúdo.
- Na peça, fala de depoente entra com o identificador da mídia no sistema e a minutagem conferida. A minutagem do arquivo de transcrição serve para localizar o trecho na mídia, não para dispensar a conferência.
- Para saber em que minuto algo foi dito, pesquise no `.txt` e devolva os trechos com a minutagem, dizendo que a busca foi feita na transcrição automática e pode ter perdido falas grafadas de outro modo.
- Ausência de um assunto na transcrição não demonstra que ele não foi tratado na audiência.
- Trabalho posterior sobre o conteúdo (estudo, perguntas, alegações, razões) pertence às outras habilidades da Trilha Criminal, quando disponíveis e quando pedido.

## Linguagem

Português brasileiro direto e natural, sem travessão e sem jargão de informática com o usuário: diga "programa de transcrição" e "modelo", explique o que será baixado e quanto tempo pode levar. Não inclua autos, nomes de clientes ou caminhos privados em recursos distribuíveis da habilidade.
