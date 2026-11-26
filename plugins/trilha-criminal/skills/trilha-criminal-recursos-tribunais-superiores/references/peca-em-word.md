# Peça em Word

Leia ao entregar a minuta integral de uma petição. As regras de escrita estão no [Núcleo comum](nucleo-comum.md); este arquivo trata do arquivo Word e da conferência final.

## Quando gerar

Minuta integral de petição destinada ao juízo sai em Word, além do que vai no chat. Plano, estrutura, capítulo avulso, revisão de trecho, roteiro de fala e relatório continuam no chat, salvo pedido de arquivo. Se o usuário disser que não quer Word, ou pedir outro formato, atenda o pedido.

O padrão é o neutro da Trilha: A4, margens de 3 cm em cima e à esquerda e 2 cm embaixo e à direita, Times New Roman, corpo em 12 pt justificado com recuo de 1,5 cm na primeira linha e entrelinhas 1,15, citações em 11 pt com recuo de 4 cm, tópicos numerados em negrito, número de página no rodapé e todo o texto em preto. Não há timbrado nem nome de escritório.

Se o usuário enviar o timbrado ou o modelo do escritório em Word, gere com `--base`: o script mantém página, margens, cabeçalho e rodapé desse arquivo e aplica os estilos da Trilha ao texto. Depois confira se o texto não invade a arte do rodapé. Não invente timbrado, logotipo, endereço ou número de inscrição.

## Como gerar

O script é [scripts/peca_word.py](../scripts/peca_word.py), na pasta desta habilidade. Use o caminho completo da pasta em que este arquivo foi lido. Ele precisa de `python-docx`; se faltar, rode `pip install python-docx`. Se não houver execução de código ou a instalação falhar, entregue a minuta no chat e diga, na nota ao advogado, que o Word não foi gerado.

1. Termine a minuta e faça a revisão de escrita antes de montar o arquivo.
2. Grave a peça em um arquivo JSON com a lista `blocos`, um bloco por parágrafo, na ordem da peça. `python peca_word.py modelo` mostra o esqueleto de uma petição, e `python peca_word.py modelo hc`, o de habeas corpus.
3. Gere: `python peca_word.py gerar --entrada peca.json --saida "Nome da peça.docx"`. Salve onde o ambiente entrega arquivos ao usuário.
4. Leia o relatório que o script imprime ao final e corrija o que ele apontar (ver abaixo).

Tipos de bloco:

| Tipo | Uso |
|---|---|
| `enderecamento` | Endereçamento, em negrito e centralizado |
| `identificacao` | Uma linha por dado: processo, paciente, autoridade coatora, origem |
| `abertura` | Qualificação e retomada depois do título, sem recuo |
| `titulo` | Nome da peça; o script põe em maiúsculas |
| `topico`, `subtopico` | Com a numeração escrita pelo autor: `1. Síntese da acusação`, `2.1. O relato não identifica o autor` |
| `corpo` | Parágrafo de argumentação |
| `transcricao` | Trecho literal de decisão, depoimento ou documento, todo em itálico |
| `referencia` | Linha logo abaixo da transcrição, como `(Decisão de dd/mm/aaaa, mov. x)` |
| `artigo` | Artigo de lei transcrito; o script põe em negrito só a identificação, como `Art. 312.` |
| `citacao` | Outra citação em bloco, sem itálico |
| `ementa` | `tribunal` com a identificação do julgado e `texto` com a ementa integral |
| `tabela` | `cabecalho` e `linhas`, para quadro que resolva um problema de leitura |
| `pedido` | Um item por bloco, começando pela letra: `a) ...`; o script põe a letra em negrito |
| `fecho`, `assinatura` | Local e data; nome do advogado em negrito e inscrição em outro bloco |
| `nota` | Observação curta dentro da peça, como a indicação de documento juntado |
| `anexos` | Logo depois das assinaturas: `itens` no formato `Doc. NN: descrição` |

Cada bloco leva `texto` ou `trechos`, lista de partes com `texto` e, quando for o caso, `negrito` ou `italico`. O negrito argumentativo vai por `trechos`, só na informação decisiva. Não escreva Markdown dentro do texto: asteriscos e cerquilhas saem literalmente no Word. `quebra_antes: true` abre o bloco em nova página, para quebra lógica. Dado que falta fica entre colchetes, como `[CONFIRMAR: data da intimação]`, e o script o lista ao final.

## Conferência

O relatório do script tem três partes.

- **Forma:** fonte, cor, página, parágrafo vazio, título do Word que recolhe seções e parágrafo inteiro em negrito. Gerado pelo script, deve vir sem desvio.
- **Escrita:** marcas de texto automático fora das transcrições, citações e ementas. O que está em "Corrigir" sai do texto: reescreva o trecho no JSON e gere de novo. O que está em "Conferir" costuma ser vício, mas pode ser necessário; mantenha só se a frase perder sentido sem a construção.
- **Campos pendentes:** os colchetes que ficaram. Liste-os na nota ao advogado.

A auditoria acha só parte das marcas da lista do núcleo comum. Trios por hábito, fechos de efeito e simetria mecânica dependem da releitura.

Para conferir um Word que o usuário enviou ou editou: `python peca_word.py auditar peca.docx`. Para revisar um texto que vai no chat ou que veio do usuário: `python peca_word.py revisar-texto --entrada minuta.md`; linhas iniciadas por `>` ficam de fora, como citação.

O script não renderiza as páginas. Se o ambiente permitir converter o Word em PDF ou imagem, confira quebras de página, título isolado no fim da página e tabela cortada. Se não permitir, diga na nota que a conferência visual não foi feita.
