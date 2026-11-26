# Registro de alterações

As versões anteriores à 0.4.1 estão resumidas no histórico do [README](README.md).

## 0.9.0

Lições de dois habeas corpus reais redigidos com o plugin em novembro de 2026: um de revogação de cautelares diversas da prisão e um contra manutenção de preventiva em processo do júri. Fatos, nomes e números dos casos não entram no pacote.

### Habeas Corpus

- Estrutura de referência reescrita em `redacao-pedidos.md`: cabeçalho de identificação e preâmbulo fixo em três blocos (impetrantes e fundamento terminando em "impetrar", título, parágrafo "em favor de" com paciente qualificado, situação de liberdade e ato coator com data e identificador), seguidos de síntese argumentativa, cabimento, histórico processual, DO CONSTRANGIMENTO ILEGAL, liminar e pedidos. Motivo: as minutas saíam sem padrão de abertura e misturavam síntese com cronologia.
- Peça datada com a data da revisão final. Nova seção "Minuta parada antes do protocolo" em `cronologia-supervenientes.md`: confirmar se houve protocolo, levantar os atos posteriores, ler os despachos do relator do recurso pendente e atualizar cabimento, perigo da demora e pedidos. Motivo: uma minuta antiga foi revisada sem que se soubesse se tinha sido protocolada, e outra peça da defesa a dava como impetrada.
- `cabimento-admissibilidade.md`: nova linha para HC sobre prisão ou cautelar com apelação pendente que contém o mesmo pedido, e regra de coerência entre pedidos de peças paralelas.
- `confronto-literal.md`: nova seção sobre ato coator com fundamento formal (documento não juntado, preclusão, inércia) e sobre decisão que reproduz o texto de decisão anterior.
- `merito-cautelar.md`: item 8 do roteiro de cautelares diversas, sobre preclusão e atraso da defesa, e nova seção "Preventiva mantida em revisão ou indeferimento de revogação" (confissão extrajudicial retratada, elementos excludentes, gravidade do grupo, reiteração, HC anterior de corréu e cautelares alternativas afastadas por fórmula genérica).
- `cognicao-prova.md`: quadro de horários extraído de documentos oficiais tratado como leitura, com a fonte de cada linha.
- `triagem-documentos.md`: cuidados de precisão para períodos, conduta do paciente e dado que não está nos autos.
- `revisao-entrega.md`: o item do checklist sobre exagero do texto legal passa a exigir a preservação do verbo do dispositivo; novos itens sobre a premissa do parecer do Ministério Público, a conferência de paciente e relator dos HCs usados para prevenção, a coerência com peças paralelas e a minuta parada.
- `regimentos-tribunais.md`: ficha do TJAM com o conteúdo dos arts. 24 e 81 a 83 na consolidação lida em 16/11/2026, modo de levantar a prevenção e aviso sobre PDF de regimento que recusa busca automática.
- `redacao-pedidos.md`, pedidos: alternativa de prazo breve ao pedir a dispensa de informações, pedido de intimação para sustentação oral, tramitação prioritária só quando houver causa, escada de subsidiários em cautelares diversas e teste da consequência antes de pedir cassação com novo exame.
- `pistas-de-pesquisa.md`: nova formação de 16/11/2026, com cinco julgados lidos em fontes secundárias, três julgados citados em peça e não localizados, e uma lacuna de pesquisa registrada.
- `SKILL.md`: remissões ao preâmbulo fixo e à rotina de minuta parada. A descrição da habilidade não mudou.

### Distribuição

- O plugin passa a aparecer como **IA Trilha Criminal** (`displayName`). O identificador `trilha-criminal` e os nomes das habilidades não mudaram, para não quebrar instalações nem a forma de chamar cada habilidade.
- Guia de início: orientação sobre a atualização automática.

### Todas as habilidades

- `nucleo-comum.md`: súmula ou julgado só entra na entrega se foi aberto no portal do tribunal na execução; site jurídico privado, blog e resumo de busca servem para localizar; o que não foi aberto vem marcado como não conferido, ou não entra. Motivo: achado registrado na execução dos testes da 0.8.3, em que julgados foram citados a partir de sites privados. A regra já existia em Cálculos Penais desde a 0.8.1.
- `localizacao-de-documentos.md`: a data do ato é a do texto assinado, distinta da data da movimentação no sistema.
- Recurso de Apelação (`pena-e-pedidos.md`) e Peças Defensivas (`pecas/liberdade-e-cautelares.md`): pedidos sobre a mesma restrição em peças paralelas devem ser coerentes; em Peças Defensivas, cumprir no prazo a diligência e identificar a que pedido ela se refere.

### Comportamento e limites

- Mudança de comportamento: o Habeas Corpus tende a reabrir o andamento antes de revisar minuta antiga, a abrir toda minuta pelo preâmbulo fixo e a pedir intimação para sustentação oral por padrão. Todas as habilidades tendem a marcar mais julgados como não conferidos quando o portal do tribunal não abrir.
- Os julgados da nova formação de pistas não tiveram o inteiro teor aberto. A existência da Lei 15.272/2025 e os dados de quatro deles foram confirmados só em fontes secundárias, em busca de 16/11/2026.
- Testado em 16/11/2026 fora do claude.ai: os casos fictícios H6.6, H6.7 e H6.8 rodaram uma vez cada, em agentes isolados que leram os arquivos desta versão, com o modelo Opus e sem acesso à internet. Os três atenderam ao esperado. O acionamento da habilidade na conta e a pesquisa com internet não foram testados nesta versão.
- Fora do pacote: `testes/casos-de-teste.md` ganha os casos H6.6 a H6.9, e `testes/materiais/` guarda os documentos fictícios usados.

## 0.8.3

Ajuste de acionamento. Regras, referências e script não mudaram; só as descrições.

- Recursos nos Tribunais Superiores: a descrição passa a dizer quando usar em termos de situação, e não só de espécie recursal: decisão de ministro relator, da Presidência ou de turma do STJ ou do STF, e recurso especial ou extraordinário inadmitido na origem, mesmo em pergunta curta e sem documentos. Traz três exemplos de pedido, entre eles o do caso de teste A8. Motivo: o A8 ("o relator do STJ negou seguimento ao meu agravo, qual o recurso e o prazo?") não acionou a habilidade em nenhuma execução registrada.
- A mesma descrição diz que, havendo data para contar, a contagem pode usar Cálculos Penais, mas a escolha do recurso fica nela.
- Habeas Corpus: a descrição passa a incluir decisão de relator ou de turma em HC ou RHC no STJ e no STF, como a liminar indeferida. Motivo: impedir que a descrição nova de Tribunais Superiores atraia o caso A9.
- Cálculos Penais: a descrição foi reordenada para abrir pelo gatilho ("use sempre que a resposta depender de contar...") e diz que a regra vale mesmo quando o resultado parecer óbvio. O conteúdo é o da 0.8.2. Motivo: o A15 entrou em uma de duas execuções.
- Recurso de Apelação: a descrição passa a remeter a contagem do prazo a partir de data informada a Cálculos Penais.
- Mudança de comportamento: Tribunais Superiores tende a entrar em mais perguntas sobre decisões do STJ e do STF. O risco é invadir Habeas Corpus em decisões de HC, coberto pelo A9.
- Este ajuste não foi testado em conversa. Acionamento varia entre execuções, e uma execução isolada não o confirma.

## 0.8.2

Ajuste de acionamento da habilidade Cálculos Penais. Regras e script não mudaram.

- A descrição passa a dizer que a habilidade entra sempre que a resposta depender de contar dias, meses ou anos a partir de uma data informada, mesmo em conta simples, e traz exemplos de pedido. Motivo: na reexecução de 11/11/2026, a pergunta "fui intimado na sexta, até quando posso apelar?" foi respondida sem a habilidade, com a data certa e sem memória de cálculo; na execução anterior, a mesma pergunta a tinha acionado.
- A descrição passa a dizer também que pergunta sobre a regra, sem data para contar, não exige a habilidade, para preservar o caso de teste A16.
- Mudança de comportamento: a habilidade tende a entrar em mais pedidos que tragam uma data. O efeito sobre as outras habilidades não foi medido.
- O corpo da habilidade explica por que pergunta de prazo com data passa pelo script. O guia de início ensina a chamar a habilidade pelo nome quando a conta vier sem memória de cálculo.
- Este ajuste não foi testado em conversa. Acionamento varia entre execuções, e uma execução isolada não o confirma.

## 0.8.1

Correções na habilidade Cálculos Penais, a partir da primeira execução dos casos de teste, em 11/11/2026. O script não mudou.

- O retrato datado das referências não pode ser apresentado como conferência da execução. A regra entra no `SKILL.md` e na abertura de cada retrato, com a fórmula a usar na nota quando nenhuma fonte oficial abrir. Motivo: em um dos casos, a resposta afirmou conferência no Planalto sem ter aberto o site.
- A descrição da habilidade passa a citar dosimetria e a conferência da conta de sentença ou acórdão. Motivo: o pedido de conferir a conta da pena não a acionou. Mudança de comportamento: a habilidade tende a entrar em mais pedidos sobre dosimetria. A crítica jurídica da dosimetria continua em Recurso de Apelação e em Peças Defensivas.
- Súmula e julgado só entram na resposta a partir do portal do tribunal, ou marcados como não conferidos. Site jurídico privado serve para localizar. Motivo: quase todas as respostas citaram julgados por sites privados.
- A nota ao advogado passa a ser exigida também na resposta curta, em duas linhas.
- Pendência conhecida, não tratada nesta versão: o caso de teste A8, de recurso contra decisão de relator do STJ, não acionou Recursos nos Tribunais Superiores.
- Estas correções ainda não foram testadas em conversa.
- Fora do pacote: `testes/casos-de-teste.md` registra a execução de nove casos na 0.8.0 e os achados.

## 0.8.0

Nova habilidade e primeiro script do pacote.

- Nova habilidade Trilha Criminal Cálculos Penais: prescrição, prazos processuais, aritmética de pena e requisitos temporais da execução, com memória de cálculo. A decisão jurídica (prazo, fração, marcos, data-base e lei aplicável) é tomada antes, com documento e lei conferida. A aritmética é feita por script.
- Novo `scripts/calculos.py` na habilidade, só com a biblioteca padrão do Python, com seis comandos (`prazo`, `prescricao`, `pena`, `execucao`, `remicao` e `periodos`) e autoteste. Nenhum prazo, fração ou percentual legal está fixado no código: entram como dado. O script recusa campo desconhecido, data inexistente e períodos sobrepostos.
- Os dispositivos das referências novas foram lidos no Planalto em 11/11/2026 e estão registrados como retrato datado, que não dispensa a conferência na execução: Código Penal, arts. 10, 11, 33, 42, 44, 69 a 71, 75, 77, 83 e 109 a 119; LEP, arts. 111, 112, 126 a 128 e 197; CPP, arts. 366, 392, 396, 403, 406, 586, 588, 593, 600, 609, 619, 798 e 798-A; Lei 9.099/1995, arts. 82, 83 e 89; Lei 11.419/2006, arts. 4º e 5º. Súmulas, temas e orientações de tribunais citados nessas referências são pistas de pesquisa e não foram conferidos.
- Achado da leitura: o art. 112 da LEP foi alterado pelas Leis 15.358 e 15.402, de 2026, e o art. 115 do Código Penal pela Lei 15.160, de 2025. As referências novas registram as duas mudanças. O mapa de institutos de `pecas/execucao-penal.md` já mandava conferir a redação e não foi alterado.
- Remissões à nova habilidade em Estudo de Caso, Peças Defensivas (inclusive no módulo de execução penal), Recurso de Apelação, Habeas Corpus e Recursos nos Tribunais Superiores.
- Mudança de comportamento: a descrição da nova habilidade pode acioná-la em perguntas sobre prescrição e contagem de prazo que antes eram respondidas sem habilidade ou por outra. A escolha do recurso cabível continua nas habilidades próprias.
- Limite conhecido: o script depende de execução de código na conversa. Sem ela, a habilidade orienta a conta manual pelas mesmas convenções e marca a entrega como não executada pelo script.
- Fora do pacote: `ferramentas/verificar.py` passa a exigir os arquivos comuns nas oito habilidades e a rodar o autoteste dos scripts; `ferramentas/empacotar.py` deixa de fora os arquivos de cache do Python. `testes/casos-de-teste.md` ganha casos de acionamento e da nova habilidade. A bateria continua não executada.

## 0.7.0

Qualidade e distribuição. Nenhuma regra de método foi alterada.

- Cada habilidade ganha `references/exemplo-de-entrega.md`, com um exemplo inteiramente fictício de entrega para calibrar formato, proporção e tom.
- Novo `GUIA-DE-INICIO.md`, para quem acabou de instalar o plugin.
- Novo `LICENSE.md`, texto-base de condições de uso, pendente de revisão do titular.
- Fora do pacote: `testes/casos-de-teste.md`, bateria manual de acionamento, regras comuns e casos por habilidade. Ainda não executada.

## 0.6.0

Ampliação de cobertura. Todo dispositivo, súmula ou tema citado nos módulos novos é localizador para conferência na execução; nenhum foi reaberto em fonte oficial na formação desta versão.

- Peças Defensivas: novo módulo `pecas/justica-negociada.md` para acordo de não persecução penal, transação penal e suspensão condicional do processo, com quadro comparativo para a decisão do cliente. Colaboração premiada permanece fora do escopo.
- Peças Defensivas: `pecas/tribunal-do-juri.md` ganha a tabela de peças da segunda fase; `pecas/execucao-penal.md` ganha o mapa de institutos, o agravo em execução e o habeas corpus na execução.
- Preparação de Audiência: novo módulo `plenario-do-juri.md` (calendário de providências, jurados, instrução, debates, quesitos e ata). A descrição da habilidade passa a mencionar o plenário, o que amplia seu acionamento.
- Recurso de Apelação, Habeas Corpus e Recursos nos Tribunais Superiores: novo módulo `sustentacao-oral.md`, idêntico nas três.
- Decisão de projeto: júri e execução penal continuam como módulos, e não como habilidades próprias.

## 0.5.0

Consistência entre as habilidades.

- Novo `references/nucleo-comum.md`, idêntico nas sete habilidades: autorização e sigilo, limites de afirmação, peça e nota ao advogado, estados de entrega, linguagem e formato. Regra específica da habilidade prevalece.
- Mudança de comportamento: a preferência de parágrafo com no máximo um ponto seguido interno, antes presente só em Habeas Corpus e Apelação, passa a valer para todo texto escrito destinado ao juízo. Não se aplica a citações nem a roteiros de fala.
- Mudança de comportamento: os estados de entrega (minuta elaborada, revisada no escopo indicado, com pendências), antes só no Habeas Corpus, passam a valer em todas as habilidades.
- Habeas Corpus: os julgados e normas lidos na formação saem de `base-badaro.md` e `fontes-de-partida.md` e vão para `pistas-de-pesquisa.md`, com data de formação e validade de doze meses.
- Recursos nos Tribunais Superiores: a matriz de prazos passa a trazer valores de referência (REsp, RE, agravos, embargos), sempre marcados como a confirmar. O ponto de atenção sobre decisão da Presidência foi reescrito em termos gerais.
- Recurso de Apelação: retirada a menção ao caso que inspirou a habilidade.
- Peças Defensivas: os módulos de ações autônomas e de liberdade remetem ao Habeas Corpus quando disponível.
- Fora do pacote: `ferramentas/verificar.py` e `ferramentas/empacotar.py` conferem cópias compartilhadas, links, manifestos e geram o zip.

## 0.4.1

Correções de consistência entre as habilidades. Nenhuma mudança de método, de escopo ou de acionamento.

### Conferência legislativa

- `references/conferencia-legislativa.md`, idêntico nas sete habilidades, passa a prever ordem de fontes: Planalto na versão compilada; outra fonte oficial (Senado, Câmara, LexML ou Diário Oficial da União) quando o Planalto não puder ser aberto; texto oficial fornecido pelo usuário.
- O registro da conferência indica a fonte efetivamente aberta e a data, e fica na nota ao advogado ou na seção de fontes do relatório, não no texto destinado ao juízo.
- Sem fonte oficial acessível, o ponto é marcado na minuta como `[CONFIRMAR: ...]`.
- A rotina passa a mencionar expressamente a Constituição, regimentos, resoluções e súmulas.

### Localização de documentos

- Novo arquivo `references/localizacao-de-documentos.md`, idêntico nas sete habilidades.
- Na peça, apenas o identificador do sistema de origem (movimento, ID, evento ou folha). Em relatórios e notas, o identificador e, quando útil, a página do arquivo rotulada como tal.
- Ajustados os trechos que traziam regras diferentes: Estudo de Caso (`SKILL.md`), Flagrante e Custódia (triagem e entregas), Habeas Corpus (confronto literal e triagem), Peças Defensivas (construção argumentativa, fontes e alegações finais), Preparação de Audiência (planejamento) e Recurso de Apelação (`SKILL.md`, sentença e prova, revisão).
- Mudança de comportamento na Apelação: a regra anterior vedava a página do PDF também na nota ao advogado e citava apenas "movimento". Agora a página pode aparecer na nota, rotulada, e o identificador segue o sistema do processo.

### Fontes

- Preparação de Audiência: links do CPP e da Lei 9.099/1995 passam do portal da Câmara para o Planalto.
- Habeas Corpus: `regimentos-tribunais.md` e `fontes-de-partida.md` passam a tratar do tribunal local de forma geral, mantendo o TJAM como exemplo de ficha preenchida.

### Empacotamento

- Logo reduzido de 1254 px para 512 px e cópia duplicada removida. O pacote cai de cerca de 2,3 MB para menos de 0,6 MB.
- `agents/openai.yaml` de Peças Defensivas, Preparação de Audiência e Recurso de Apelação recebem o bloco `policy` já presente nas demais.
- Versão 0.4.1 nos três manifestos.
