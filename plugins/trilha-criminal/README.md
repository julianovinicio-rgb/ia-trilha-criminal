# IA Trilha Criminal

Versão 0.12.0, distribuída aos alunos da Trilha Criminal.

O plugin reúne oito habilidades independentes. Use a função correspondente ao pedido, sem impor uma sequência obrigatória ou iniciar atividades não solicitadas.

| Trabalho | Habilidade |
|---|---|
| Estudar autos, confrontar provas, auditar atos e formular estratégia | Trilha Criminal Estudo de Caso |
| Atuar entre a prisão em flagrante e o fim da audiência de custódia, inclusive na primeira peça de liberdade | Trilha Criminal Flagrante e Custódia |
| Planejar, redigir, revisar ou atualizar uma peça defensiva, inclusive memoriais de alegações finais | Trilha Criminal Peças Defensivas |
| Preparar audiência de instrução, perguntas, interrogatório e alegações finais orais, e o plenário do júri | Trilha Criminal Preparação de Audiência |
| Analisar a sentença, planejar, redigir ou revisar a apelação criminal | Trilha Criminal Recurso de Apelação |
| Analisar o constrangimento à liberdade, planejar, redigir, revisar ou atualizar HC, RHC e impugnações relacionadas | Trilha Criminal Habeas Corpus |
| Recurso especial, extraordinário, agravos, embargos, reclamação e tutela de urgência no STJ e no STF | Trilha Criminal Recursos nos Tribunais Superiores |
| Calcular prescrição, prazo processual, pena e requisito temporal da execução, com memória de cálculo | Trilha Criminal Cálculos Penais |

Preventiva decretada depois da custódia é tratada pelas habilidades de Habeas Corpus ou de Peças Defensivas. Habeas corpus e RHC permanecem na habilidade de Habeas Corpus, e a apelação permanece na habilidade própria. A habilidade de Cálculos Penais faz a conta; a escolha do recurso cabível continua na habilidade do recurso.

Quem está começando deve ler o [Guia de início](GUIA-DE-INICIO.md). As condições de uso estão em [LICENSE.md](LICENSE.md).

## Exemplos de uso

- “Estude este processo. Meu cliente é [nome]. Meu objetivo é [objetivo].”
- “Meu cliente foi preso em flagrante há três horas. Faça a triagem do auto e prepare o roteiro da audiência de custódia.”
- “Com base no auto de prisão, redija o pedido de relaxamento ou de liberdade provisória para o juízo da custódia.”
- “Planeje o pedido de revogação da prisão, sem redigir ainda.”
- “Redija os memoriais de alegações finais com base nos documentos deste caso.”
- “Revise juridicamente esta apelação e a correspondência entre fundamentos e pedidos.”
- “Prepare as perguntas por depoente e os cenários de encerramento da audiência.”
- “Analise o cabimento e planeje o habeas corpus deste paciente, sem redigir ainda.”
- “Identifique o recurso cabível e o prazo contra esta decisão monocrática do STJ e redija o agravo.”
- “Revise este recurso especial quanto a prequestionamento, Súmula 7 e impugnação de todos os fundamentos do acórdão.”
- “Calcule se este crime prescreveu, com os marcos destes documentos, e mostre a memória de cálculo.”
- “Confira a dosimetria desta sentença e diga qual tese leva a pena para até quatro anos.”

## Cálculos e script

A habilidade Cálculos Penais traz o arquivo `scripts/calculos.py`, que faz a aritmética de datas, frações e penas e devolve uma memória de cálculo. Ele usa apenas a biblioteca padrão do Python e tem seis comandos: `prazo`, `prescricao`, `pena`, `execucao`, `remicao` e `periodos`.

Nenhum prazo, fração ou percentual legal está fixado no código. Esses valores entram como dado, depois de conferidos em fonte oficial na execução, e o script recusa entrada incompleta ou incoerente em vez de completá-la. As tabelas das referências dessa habilidade são retratos datados da lei e não dispensam a conferência.

A execução do script depende de a conversa permitir execução de código. Sem isso, a habilidade orienta a conta manual pelas mesmas convenções e marca a entrega como não executada pelo script.

## Peça em Word

As habilidades que redigem petição (Peças Defensivas, Habeas Corpus, Recurso de Apelação, Recursos nos Tribunais Superiores e Flagrante e Custódia) têm o arquivo `scripts/peca_word.py`, idêntico nas cinco, e a referência `references/peca-em-word.md`. A minuta integral sai também em Word no padrão neutro da Trilha: A4, Times New Roman, corpo em 12 pt justificado, entrelinhas 1,15, citações em 11 pt com recuo de 4 cm, tópicos numerados em negrito, número de página e todo o texto em preto, sem timbrado. Quem tiver timbrado ou modelo próprio em Word pode enviá-lo, e o script o usa como base.

O mesmo script audita o Word gerado ou recebido: forma (fonte, cor, página, parágrafos vazios) e marcas de texto automático fora das citações, como travessão, muletas de transição e ênfase artificial. A lista dessas marcas está no núcleo comum. Gerar o Word exige execução de código e a biblioteca `python-docx`; sem elas, a minuta vem no chat com o aviso.

## Conferência legislativa

Todas as habilidades têm o arquivo `references/conferencia-legislativa.md`, com conteúdo idêntico. Ele concentra a regra de conferência de artigos de lei: texto em fonte oficial na própria execução, com preferência pelo Planalto na versão compilada e, se ele não puder ser aberto, outra fonte oficial identificada; análise da redação aplicável na data do fato; e registro da fonte e da data na nota ao advogado, fora do texto destinado ao juízo. Alterações futuras dessa regra devem ser feitas nesse arquivo em cada habilidade.

## Registro de fontes

Todas as habilidades têm o arquivo `references/registro-de-fontes.md`, com conteúdo idêntico. Ele torna a pesquisa parte obrigatória de toda execução (precedentes qualificados, STF, STJ e o tribunal em que o processo tramita) e define o arquivo de conferência que acompanha a entrega: `Fontes - [nome da entrega].md`, com cada artigo e cada julgado, o link efetivamente aberto, o que foi lido, a data e um de quatro estados de conferência. Julgado localizado só em fonte não oficial, ou não aberto na execução, fica como pista com caminho de conferência e não sustenta afirmação no texto destinado ao juízo. O arquivo traz também um retrato datado de quais portais oficiais abrem para ferramenta automática.

## Núcleo comum

Todas as habilidades têm o arquivo `references/nucleo-comum.md`, com conteúdo idêntico: autorização e sigilo, limites de afirmação, separação entre peça e nota ao advogado, estados de entrega, linguagem e marcas de texto automático a evitar. Regra mais específica de cada habilidade prevalece sobre ele.

## Localização de documentos

Todas as habilidades têm também o arquivo `references/localizacao-de-documentos.md`, com conteúdo idêntico. Ele define como indicar documentos, trechos e mídias dos autos: na peça, apenas o identificador do sistema de origem (movimento no Projudi, ID no PJe, evento no eproc, folha no e-SAJ e em autos físicos); em relatórios e notas ao advogado, o identificador e, quando útil, a página do arquivo rotulada como tal. A preferência expressa do usuário prevalece.

## Arquivos de continuidade

Todas as habilidades têm o arquivo `references/arquivos-de-continuidade.md`, com conteúdo idêntico. Ele define dois arquivos que guardam o que já se sabe de um caso: `DIRETRIZES-DO-CASO.md`, um por cliente, com resumo, processos, objetivo, estratégia, próximos passos, decisões do advogado e propostas em aberto; e `indice.md`, um por processo, com o que existe nos autos e onde está. Com a pasta do caso acessível, toda habilidade os lê antes dos autos. O Estudo de Caso os cria e atualiza; as demais atualizam só a parte que o trabalho delas alterou. Em conversa sem pasta conectada, o Estudo de Caso entrega os dois arquivos para baixar, e as demais habilidades só os usam quando o usuário os anexa. Havendo mais de um processo na mesma pasta, o índice leva o número do processo no nome. O índice orienta a leitura, mas não comprova nem conta como exame do documento, e sugestão da ferramenta só vira decisão quando o advogado decide.

## Limites

Relatórios anteriores orientam o trabalho. Afirmações decisivas devem ser conferidas nas fontes acessíveis, com indicação das lacunas e do último ato abrangido. Um pedido de estudo não autoriza automaticamente redigir uma peça.

O pacote contém instruções, referências metodológicas, o script de cálculo da habilidade Cálculos Penais e o script de Word das habilidades que redigem petição. Não inclui autos, peças reais usadas como amostras, credenciais, catálogo de precedentes verificados, servidor próprio ou ferramentas de protocolo. A leitura, o OCR, a pesquisa e a criação de arquivos dependem das capacidades disponíveis na conversa. Não configura por si só acesso a tribunais, protocolo, escuta automática ou monitoramento de audiência.

Toda jurisprudência é pesquisada e conferida na própria execução. Os poucos julgados lidos na formação do Habeas Corpus ficam em `pistas-de-pesquisa.md`, com data e validade, apenas como ponto de partida. Onde um dado não puder ser conferido, a entrega informa que está pendente de verificação.

O plugin não inclui timbrado de escritório. O Word sai no padrão neutro da Trilha, ou sobre o timbrado que o usuário enviar.

As habilidades também podem ser chamadas explicitamente pelo nome disponível no seletor de habilidades. A instalação de um plugin é distinta da instalação avulsa de cada habilidade. O pacote é instalável no Claude e no Codex, com manifestos em `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` e `plugin.json`.

Autoria: Juliano Negreiros. Uso e distribuição sujeitos à autorização do titular, nos termos de [LICENSE.md](LICENSE.md).

## Histórico de versões

- **0.3.1:** incorporação do aperfeiçoamento do Habeas Corpus 1.1.0 a partir do capítulo de Badaró: cognição e prova documental, decisões anteriores, tutela liminar, habeas corpus coletivo e execução da ordem, com distinção entre doutrina e direito vigente. As outras quatro habilidades permaneceram inalteradas.
- **0.3.3:** acréscimos ao Habeas Corpus sobre resposta à orientação que dispensa a enumeração individual das medidas do art. 319; medidas protetivas e monitoração em violência doméstica; prisão mantida na pronúncia com RESE pendente; fase e data de precedentes e vigência de leis; dispensa de informações e vista obrigatória ao Ministério Público; e conferência de arquivos já editados pelo advogado.
- **0.3.4:** versão de base desta atualização. O pacote base não traz registro das mudanças em relação à 0.3.3; descrição pendente de verificação pelo autor.
- **0.4.0:** regra de conferência legislativa unificada em `references/conferencia-legislativa.md` em todas as habilidades, com análise da redação aplicável na data do fato, acesso pelo navegador e registro da data de conferência; links do CPP padronizados para a versão compilada; Peças Defensivas passa a incluir ataque por literalidade, estrutura de memorial de alegações finais e tabela de linguagem com limite de dois precedentes por tese; criação das habilidades Flagrante e Custódia e Recursos nos Tribunais Superiores; manifestos e README atualizados para sete habilidades.
- **0.4.1:** correções de consistência, sem mudança de método. Conferência legislativa passa a admitir fonte oficial alternativa identificada e registra a conferência na nota ao advogado; convenção única de localização de documentos em todas as habilidades; links de legislação da skill de Audiência apontados para o Planalto; regimento do tribunal local generalizado no Habeas Corpus, com o TJAM como exemplo; logo reduzido. Detalhes em [CHANGELOG.md](CHANGELOG.md).
- **0.5.0:** núcleo comum de regras em todas as habilidades; julgados datados do Habeas Corpus reunidos em pistas de pesquisa com validade; matriz de prazos dos tribunais superiores com valores de referência a confirmar; remissões entre Peças Defensivas e as habilidades especializadas.
- **0.6.0:** ampliação de cobertura. Peças Defensivas ganha o módulo de justiça negociada (acordo de não persecução penal, transação e suspensão condicional do processo) e amplia os de júri e de execução penal; Preparação de Audiência ganha o módulo de plenário do júri; Apelação, Habeas Corpus e Recursos nos Tribunais Superiores ganham o módulo de sustentação oral.
- **0.7.0:** um exemplo fictício de entrega em cada habilidade, guia de início para quem instala o plugin e arquivo de condições de uso.
- **0.8.0:** nova habilidade Cálculos Penais, com script próprio para prescrição, prazos processuais, pena e execução, e remissões a ela nas demais habilidades.
- **0.8.1:** correções na habilidade Cálculos Penais depois da primeira execução dos testes: o retrato datado da lei não vale como conferência da execução, a descrição passa a citar dosimetria, e súmula ou julgado só entra a partir do portal do tribunal.
- **0.8.2:** descrição da habilidade Cálculos Penais reforçada para entrar em toda pergunta que dependa de contar tempo a partir de uma data informada, com exemplos de pedido.
- **0.8.3:** descrição de Recursos nos Tribunais Superiores reescrita para entrar em pergunta curta sobre decisão de relator, Presidência ou turma do STJ e do STF; descrição de Cálculos Penais começa pelo gatilho; fronteiras com Habeas Corpus e Recurso de Apelação explicitadas.
- **0.9.0:** Habeas Corpus revisto a partir de dois trabalhos reais: preâmbulo fixo em três blocos, síntese argumentativa separada do histórico, rotina para minuta parada antes do protocolo, HC concomitante a recurso com o mesmo pedido, enfrentamento de fundamento formal e de decisão reproduzida, escada de subsidiários em cautelares diversas e técnicas para preventiva mantida. Em todas as habilidades, súmula e julgado só entram a partir do portal do tribunal ou marcados como não conferidos, e a data do ato se distingue da data da movimentação.
- **0.10.0:** a minuta integral de petição sai também em Word, no padrão neutro da Trilha (Times New Roman, tudo em preto, sem timbrado), por um script com auditoria de forma e de escrita; o núcleo comum proíbe o travessão em qualquer função no texto ao juízo e lista as marcas de texto automático a evitar.
- **0.10.1:** logo da Trilha Criminal no campo `icon` do manifesto do Claude, para a página do plugin.
- **0.11.0:** registro de fontes em todas as habilidades: pesquisa de legislação e de jurisprudência em toda execução, no STF, no STJ e no tribunal do caso, e arquivo separado com o link, o que foi lido e o estado de conferência de cada fonte; dois endereços do STF que deixaram de abrir foram retirados.
- **0.12.0:** arquivos de continuidade do caso em todas as habilidades: diretrizes do caso, uma por cliente, e índice dos autos, um por processo, lidos antes dos autos quando a pasta do caso está acessível; o Estudo de Caso os cria e atualiza, com a conclusão registrada como proposta até o advogado decidir.
