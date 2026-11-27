# Arquivos de continuidade do caso

Este arquivo é idêntico em todas as habilidades da Trilha Criminal. Alterações futuras devem ser feitas nele e replicadas nas oito.

Dois arquivos em Markdown guardam o que já se sabe de um caso, para que o trabalho seguinte não recomece do zero nem releia os autos inteiros a cada pergunta.

| Arquivo | Onde fica | Quantos | Para que serve |
|---|---|---|---|
| `DIRETRIZES-DO-CASO.md` | Pasta do cliente | Um por cliente, cobrindo todos os processos dele | Resumo do caso, processos, objetivo da defesa, estratégia, próximos passos, decisões, propostas, pendências e histórico |
| `indice.md` | Pasta de cada processo | Um por processo | O que existe nos autos e onde está: identificador do sistema, data, arquivo e páginas |

As diretrizes são uma por cliente porque os processos do mesmo cliente se influenciam: medida protetiva e ação penal, inquérito e ação penal, processo de conhecimento e execução. Estratégia separada por processo tende a ficar contraditória.

Se mais de um processo do mesmo cliente estiver na mesma pasta, sem subpasta para cada um, o índice de cada processo se chama `indice-<número do processo>.md`, para que um não sobrescreva o outro.

Se o usuário ou o escritório já usa outros nomes ou outra organização de pastas, siga a dele.

## Leitura no início do trabalho

Em todo trabalho sobre um caso cuja pasta esteja acessível:

1. Procure `DIRETRIZES-DO-CASO.md` na pasta do cliente e `indice.md` na pasta do processo (ou `indice-<número do processo>.md`, quando a pasta reúne mais de um processo).
2. Se existirem, leia-os antes dos autos. As diretrizes dão contexto, objetivo e o que já foi decidido. O índice diz onde está cada peça.
3. Use o índice para abrir só os trechos necessários dos autos, em vez de reler o processo inteiro.
4. Índice e diretrizes orientam a leitura, mas não comprovam. Aspas, identificadores, datas, nomes, penas e demais dados decisivos são conferidos no original antes de entrar em peça ou conclusão. A leitura do índice não conta como exame do documento para fins de cobertura.
5. Decisão do advogado registrada nas diretrizes vale como orientação até ele mudar. Se os autos ou o pedido atual contrariarem algo registrado, aponte a divergência em vez de seguir em silêncio.
6. Se a data da última conferência for anterior a atos já conhecidos, diga que os arquivos estão desatualizados.

## Criação e atualização

Só quando o ambiente permite gravar arquivos na pasta do caso:

- **Estudo de Caso** cria os dois arquivos quando não existem e os atualiza ao fim de cada estudo ou atualização.
- **Demais habilidades** leem os arquivos. Atualizam as diretrizes só nas seções que o trabalho alterou (próximos passos, decisões do advogado, propostas, pendências) e atualizam o índice quando examinaram documento dos autos que ainda não estava nele. Se os arquivos não existirem, oferecem criá-los em uma linha, sem criar por conta própria.
- Toda alteração nas diretrizes ganha uma linha no histórico, com data e motivo.
- A edição é pontual. Conteúdo escrito pelo usuário não é apagado nem reescrito sem pedido.
- Nomes de arquivo sem acento, para evitar problema de codificação na sincronização.

Com a pasta acessível, mas sem permissão para gravar, não prometa persistência. Ao final, ofereça no chat o trecho atualizado para o usuário salvar.

## Conversa sem pasta do caso

Quando o usuário trabalha por anexos, sem pasta conectada:

- Se ele anexar as diretrizes ou o índice, leia-os antes dos autos, com as mesmas regras da leitura no início do trabalho.
- **Estudo de Caso**, ao fim de cada estudo ou atualização, entrega os dois arquivos para baixar, quando a conversa cria arquivos, e avisa em uma linha que eles devem ser salvos na pasta do cliente e anexados no próximo pedido sobre o caso. Se a conversa não cria arquivos, oferece o conteúdo no chat.
- **Demais habilidades**, se os arquivos foram anexados, entregam ao final a versão atualizada, só com as seções que o trabalho alterou, ou o trecho alterado no chat quando a conversa não cria arquivos. Se não foram anexados, não os mencionam nem oferecem criá-los.
- Não prometa persistência: nesse ambiente, o que o usuário não salvar não estará na próxima conversa.

## Regras de conteúdo

- **Índice:** só factual. Diz o que existe e onde está. Sem avaliação, tese ou risco. Identificadores seguem [Localização de documentos](localizacao-de-documentos.md). Página do arquivo vem rotulada como tal e não se confunde com folha dos autos. Página não confirmada fica como "pág. a confirmar".
- **Diretrizes, parte factual:** sempre com identificador do sistema.
- **Diretrizes, parte estratégica:** separada em duas listas. "Decisões tomadas" recebe só o que o advogado decidiu. "Propostas em aberto" recebe as sugestões da ferramenta, com data, até o advogado aprovar ou descartar. Sugestão não vira decisão por falta de objeção.
- Na primeira criação, sem decisão do advogado, a estratégia fica como "a definir" ou em propostas. Não invente tese para preencher o modelo.
- Prazo só entra com marco confirmado. Não calcule a partir de intimação não confirmada. Quando houver Cálculos Penais, a conta vem dela.
- Os arquivos contêm dados do cliente e têm o mesmo sigilo dos autos: não vão para serviço externo e não entram no pacote distribuível.

## Modelo do índice

```markdown
# Indice dos autos - <número do processo>

- Cliente: <nome> (<posição>)
- Juízo: <juízo> | Classe: <classe> | Assunto: <assunto> | Sigilo: <nível>
- Situação em dd/mm/aaaa: <prisão, cautelares, apensos, fase>
- Última conferência no sistema: dd/mm/aaaa, até <identificador> (dd/mm/aaaa)

## Arquivos dos autos
| Arquivo | Atos abrangidos | Período | Páginas |
|---|---|---|---|

## Atalhos para as peças principais
- Denúncia: <identificador>, <arquivo>, p. <x-y> do PDF
- Recebimento da denúncia:
- Prisão e decisões sobre liberdade:
- Resposta à acusação:
- Audiências e termos:
- Sentença e acórdãos:
(só o que existe; uma linha descritiva, sem avaliação)

## Documentos
| Identificador | Data | Ato | Do que se trata (1 linha) | Arquivo | Páginas |
|---|---|---|---|---|---|

## Mídias e itens fora dos arquivos

## Pendências de leitura
(ilegível, sem OCR, sigiloso indisponível, página a confirmar)
```

## Modelo das diretrizes

```markdown
# Diretrizes do caso - <cliente>
Atualizado em: dd/mm/aaaa

## 1. Resumo do caso
(o que se imputa, quando, contexto, processos existentes e situação atual do cliente; só fatos, com identificadores)

## 2. Processos
| Processo | Juízo | Classe | Fase | Situação do cliente | Índice |
|---|---|---|---|---|---|

## 3. Relação entre os processos

## 4. Objetivo da defesa

## 5. Estratégia atual
### Linha principal
### Alternativas
### Riscos e pontos fracos

## 6. Próximos passos e prazos
| Providência | Processo | Responsável | Data ou prazo | Situação |
|---|---|---|---|---|

## 7. Decisões tomadas
- dd/mm/aaaa: <decisão do advogado> | motivo

## 8. Propostas em aberto
- dd/mm/aaaa: <sugestão ainda não aprovada>

## 9. Pendências de informação e documentos

## 10. Histórico de alterações
- dd/mm/aaaa: <o que mudou e por quê>
```
