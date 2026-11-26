# Guia de início

Este guia é para quem acabou de instalar o plugin IA Trilha Criminal. Leva cinco minutos.

## O que o plugin faz

Ele ensina ao assistente um método de trabalho defensivo criminal. São oito habilidades, cada uma para um tipo de trabalho. Você não precisa decorar os nomes: descreva o que quer e a habilidade certa é acionada. Se preferir, chame pelo nome no seletor de habilidades.

| Você precisa de | Diga algo como |
|---|---|
| Entender um processo e achar as teses | "Estude este processo. Meu cliente é [nome]. Meu objetivo é [objetivo]." |
| Atuar em flagrante e custódia hoje | "Meu cliente foi preso em flagrante. A custódia é às 14h. Faça a triagem e o roteiro." |
| Uma peça | "Redija a resposta à acusação com base nestes documentos." |
| Avaliar um acordo | "O Ministério Público ofereceu acordo de não persecução. Compare os cenários para eu conversar com o cliente." |
| Preparar audiência ou plenário | "Prepare a audiência de instrução, com perguntas por depoente." |
| Apelar | "Examine a sentença e planeje a apelação, sem redigir ainda." |
| Habeas corpus | "Analise o cabimento e planeje o HC deste paciente." |
| Recorrer ao STJ ou ao STF | "Identifique o recurso cabível e o prazo contra esta decisão." |
| Sustentar oralmente | "Prepare o roteiro de sustentação oral desta apelação." |
| Calcular prescrição, prazo, pena ou progressão | "Calcule se este crime prescreveu, com os marcos destes documentos." |

## Três regras para tirar o melhor resultado

**1. Envie os documentos e diga quem é o cliente.** O método parte do que está nos autos. Sem documento, o assistente avisa o que falta em vez de inventar.

**2. Diga se quer plano ou peça.** "Planeje, sem redigir ainda" produz estratégia e para. "Redija" produz a minuta. Pedir estudo não gera peça, e pedir peça não gera protocolo.

**3. Leia a nota ao advogado.** Toda entrega vem em duas partes: o texto para o juízo e uma nota separada para você. A nota diz o que foi lido, o que não foi, quais artigos e julgados foram conferidos e em que data, e o que ainda precisa de confirmação. Marcas como `[CONFIRMAR: data da intimação]` na minuta são pontos que só você pode resolver.

## Antes do primeiro pedido

Confira se a pesquisa na web está ligada na sua conversa. Sem ela, o assistente não consegue conferir lei nem jurisprudência, e toda entrega sai com esses pontos pendentes. A criação de arquivos também precisa estar disponível para receber o Word e o arquivo de fontes.

A pesquisa de jurisprudência do STJ e a do STF costumam recusar ferramentas automáticas. Por isso é normal que parte dos julgados venha como pista a conferir: o arquivo de fontes traz o número e o caminho, e a conferência leva um minuto no portal do tribunal.

## O que esperar

- **Nenhum precedente de memória.** A jurisprudência é pesquisada na hora, no STF, no STJ e no tribunal do seu processo, em fonte oficial. Se a pesquisa não for possível, a entrega diz que o ponto está pendente.
- **Um arquivo de fontes para você conferir.** Junto com a peça ou o estudo vem o arquivo `Fontes - [nome da entrega].md`: cada artigo e cada julgado com o link de onde saiu, o que foi lido e se foi conferido. Clique, confira e só então use. Julgado que a IA não conseguiu abrir no portal oficial aparece como pista, com o caminho para você conferir, e não entra na peça como fundamento.
- **Artigos de lei conferidos.** O texto é lido em fonte oficial na execução, com a data registrada na nota.
- **Citações literais só do original.** Trecho entre aspas ou em itálico foi conferido no documento. Se o original não estava disponível, a nota avisa.
- **Nenhuma conta de cabeça.** Datas, frações e penas são calculadas por um script, e a entrega traz a memória de cálculo para você refazer. A data projetada é uma conta sobre os dados informados, e não um direito reconhecido. Se a sua conversa não executa código, a entrega avisa que a conta foi feita à mão.
- **Minuta em Word.** A minuta completa de uma petição vem também em Word, em Times New Roman e toda em preto, sem timbrado. Se quiser o seu timbrado, envie o modelo do escritório em Word junto com o pedido.
- **Nenhuma peça "pronta para protocolo".** O plugin entrega minuta elaborada, revisada no escopo indicado ou com pendências. A conferência final e a decisão de protocolar são suas.

## O que o plugin não faz

Não acessa tribunais, não protocola, não acompanha processos, não ouve audiências e não substitui a sua leitura dos autos nem a sua responsabilidade profissional. O que ele consegue ler, pesquisar e gerar depende das ferramentas disponíveis na sua conversa: leitura de PDF, pesquisa na internet, navegador e criação de arquivos.

## Sigilo

Os documentos que você envia são tratados como fonte do caso. O método proíbe mandar autos ou dados do cliente a serviços externos sem a sua autorização e usa termos abstratos na pesquisa pública. Ainda assim, confira as regras de sigilo da ferramenta que você usa e as normas da OAB antes de enviar documentos de clientes.

## Se algo sair errado

- **A habilidade errada foi acionada:** chame a certa pelo nome.
- **A conta veio sem memória de cálculo:** a habilidade de cálculos não entrou. Chame-a pelo nome, `/trilha-criminal-calculos-penais`, e repita o pedido.
- **A entrega veio longa demais:** peça o recorte. "Só o capítulo da dosimetria."
- **Um artigo ou julgado parece errado:** abra o arquivo de fontes e clique no link. Se a entrega veio sem ele, peça: "gere o registro de fontes desta entrega". O que não tiver link aberto e data, trate como não conferido.
- **A versão está desatualizada:** confira se a atualização automática do marketplace está ligada, ou peça a atualização na hora (no Claude, "Verificar atualizações" na tela de plugins), e abra uma conversa nova.

Histórico de versões em [CHANGELOG.md](CHANGELOG.md). Condições de uso em [LICENSE.md](LICENSE.md).
