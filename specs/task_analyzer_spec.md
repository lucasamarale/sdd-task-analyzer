# Especificação SDD TaskAnalyzer

Especificação Técnica e Governança de Contexto (SDD e AI Harness).

| | |
|---|---|
| Autor | Lucas Amaral Evangelista, RA 22508120 |
| Curso | Ciência da Computação, CEUB, turma UN 0726 |
| Disciplina | Bootcamp III, Fase 1 |
| Versão | 1.0, 21 de agosto de 2026 |

> Transposição para Markdown do documento entregue na Fase 1, sem alteração de conteúdo.

## Repositório da Fase 2

O código gerado na próxima fase será versionado no repositório abaixo, com a estrutura descrita na seção 4.

| Item | Endereço |
|---|---|
| Repositório previsto para a Fase 2 | github.com/lucasamarale/sdd-task-analyzer |

## 1. Visão geral e contrato de negócio (SDD)

Esta seção define o contrato executável que serve de fonte da verdade para o código a ser gerado por assistentes de inteligência artificial na Fase 2. Tudo o que não estiver escrito aqui não deve ser implementado.

### 1.1 Identificação

| Campo | Valor |
|---|---|
| Nome completo           | Lucas Amaral Evangelista                                                  |
| RA                      | 22508120                                                                  |
| Curso                   | Ciência da Computação                                                     |
| Polo / Turma            | CEUB Asa Norte, turma UN 0726, noturno                                    |
| E-mail institucional    | lucasamarale@sempreceub.com                                               |
| Disciplina              | Bootcamp III, 75 horas, EAD                                               |
| Entrega                 | Fase 1, Especificação Técnica e Governança de Contexto (SDD e AI Harness) |
| Data de elaboração      | 21 de agosto de 2026                                                      |
| Versão da especificação | 1.0                                                                       |

### 1.2 Propósito do módulo TaskAnalyzer

O TaskAnalyzer é um módulo de análise de tarefas e produtividade. Ele recebe um conjunto de tarefas já registradas e devolve um retrato quantitativo de como esse conjunto foi executado, sem opinar sobre pessoas e sem inferir nada que os dados não sustentem.

O problema que ele resolve é conhecido de qualquer equipe: existe registro de tarefa em abundância e quase nenhuma leitura útil sobre ele. Saber quantas tarefas foram concluídas é fácil; saber quanto tempo elas realmente levaram, qual proporção estourou o prazo e se esse comportamento muda conforme a prioridade exige um cálculo consistente e sempre igual. Feito na mão, em planilha, esse cálculo varia conforme quem calcula.

O módulo entrega quatro respostas objetivas:

  - Tempo médio de conclusão, no conjunto geral e por prioridade, em minutos.

  - Taxa de atraso, isto é, o percentual de tarefas concluídas após o prazo acordado.

  - Quantidade de tarefas efetivamente consideradas, o que torna cada média auditável.

  - Indicadores segmentados por prioridade, que revelam se o atraso se concentra em alguma faixa.

O escopo é deliberadamente estreito. O TaskAnalyzer calcula e devolve métricas. Ele não armazena dados, não desenha gráficos, não envia notificação e não decide nada por ninguém: a decisão de gestão pertence a quem lê o resultado. Essa fronteira é o que permite testar o módulo de forma determinística e reaproveitá-lo em contextos diferentes.

### 1.3 Contrato executável de interface

A função pública do módulo tem a seguinte assinatura, que não pode ser alterada pelo assistente de inteligência artificial sem autorização registrada:

```python
def analisar_tarefas(tarefas: list[Tarefa]) -> MetricasProdutividade:
    """Calcula métricas de produtividade a partir de um conjunto de tarefas."""
```

Tarefa e MetricasProdutividade são dataclasses congeladas (frozen=True) definidas no próprio módulo, com os campos descritos nas tabelas 1.3.1 e 1.3.2. O uso de dataclass, e não de dicionário livre, é uma decisão de contrato: ela dá validação de tipo estática, torna a estrutura explícita para o assistente de inteligência artificial e impede a criação silenciosa de campos não previstos.

#### 1.3.1 Entradas

| Campo | Tipo | Obrigatório | Descrição e restrições |
|---|---|---|---|
| id_tarefa      | int             | Sim             | Identificador único da tarefa. Deve ser inteiro positivo e não repetido no conjunto.        |
| data_criacao   | datetime        | Sim             | Data e hora de abertura da tarefa, em UTC e ciente de fuso (timezone-aware).                |
| data_inicio    | `datetime \| None` | Não             | Data e hora do início da execução. Quando informada, não pode ser anterior a data_criacao. |
| data_conclusao | `datetime \| None` | Condicional     | Obrigatória quando status é "concluida". Não pode ser anterior a data_criacao.             |
| prazo           | datetime        | Sim             | Data e hora limite acordada para a conclusão da tarefa, em UTC.                             |
| prioridade      | str             | Sim             | Valores aceitos: "baixa", "media" ou "alta". Comparação sem distinção de maiúsculas.        |
| status          | str             | Sim             | Valores aceitos: "concluida", "pendente" ou "cancelada".                                    |

#### 1.3.2 Saídas

| Campo | Tipo | Descrição |
|---|---|---|
| tempo_medio_conclusao_min | float             | Tempo médio de conclusão das tarefas concluídas, em minutos, arredondado em duas casas decimais.                    |
| taxa_atraso_percentual     | float             | Percentual de tarefas concluídas após o prazo, de 0.0 a 100.0, arredondado em duas casas decimais.                  |
| quantidade_tarefas          | int               | Total de tarefas concluídas consideradas no cálculo.                                                                |
| indicadores_por_prioridade | dict[str, dict] | Mesmas três métricas acima, calculadas separadamente para cada prioridade que possua ao menos uma tarefa concluída. |

Cada chave de indicadores_por_prioridade é uma das prioridades presentes no conjunto, e o valor associado repete a mesma estrutura de três métricas, restrita às tarefas daquela prioridade.

#### 1.3.3 Regras de negócio e restrições

| ID | Regra |
|---|---|
| RN-01  | Somente tarefas com status "concluida" entram em qualquer cálculo. Tarefas pendentes e canceladas são ignoradas sem gerar erro.                                                                                        |
| RN-02  | O tempo de conclusão de uma tarefa é a diferença entre data_conclusao e data_criacao, expressa em minutos.                                                                                                           |
| RN-03  | Uma tarefa é considerada atrasada quando data_conclusao é estritamente posterior a prazo. Conclusão exatamente no prazo não é atraso.                                                                                 |
| RN-04  | Todas as datas são tratadas em UTC. Datas sem informação de fuso são rejeitadas como entrada inválida.                                                                                                                 |
| RN-05  | Toda métrica de tempo e de percentual é arredondada para duas casas decimais apenas na saída, nunca durante o cálculo intermediário.                                                                                   |
| RN-06  | As métricas são calculadas para o conjunto geral e, separadamente, por prioridade.                                                                                                                                     |
| RN-07  | Prioridade sem nenhuma tarefa concluída não aparece em indicadores_por_prioridade. A ausência da chave comunica ausência de dado, o que é mais honesto do que devolver zero.                                         |
| RN-08  | Nenhuma divisão é executada sem verificação prévia do denominador, conforme a regra RN-09.                                                                                                                             |
| RN-09  | Conjunto de entrada vazio, ou conjunto sem nenhuma tarefa concluída, não produz métrica: a função levanta SemTarefasConcluidasError. Devolver zero nesse caso seria indistinguível de um desempenho real igual a zero. |
| RN-10  | Qualquer violação de tipo, de enumeração ou de coerência entre datas interrompe a análise e levanta TarefaInvalidaError, identificando o id_tarefa e o campo responsável.                                             |
| RN-11  | A função é pura: não altera a lista recebida, não lê nem escreve arquivos, não acessa rede e não persiste estado.                                                                                                      |

#### 1.3.4 Exceções previstas

O módulo define uma hierarquia própria de exceções. Erro previsto é parte do contrato, e não acidente:

| Exceção | Herda de | Quando é levantada |
|---|---|---|
| TaskAnalyzerError         | Exception         | Classe base do módulo. Permite que o chamador capture qualquer erro previsto do TaskAnalyzer com um único except. |
| TarefaInvalidaError       | TaskAnalyzerError | Campo ausente, tipo incorreto, valor fora da enumeração, data sem fuso ou datas incoerentes entre si.             |
| SemTarefasConcluidasError | TaskAnalyzerError | Não há tarefa concluída no conjunto informado. É o caso que evita a divisão por zero.                             |

## 2. Especificação de cenários de aceite e Test Harness

Os cenários abaixo descrevem o comportamento esperado do sistema em linguagem estruturada Dado, Quando, Então. Eles são a tradução verificável do contrato da seção 1 e, na Fase 2, viram testes automatizados em pytest. Nenhum deles pode ser alterado ou removido pelo assistente de inteligência artificial.

Os cenários CA-01 e CA-02 são os dois exigidos pelo enunciado. Os demais foram acrescentados para cobrir fronteiras que costumam passar despercebidas e nas quais o código gerado por inteligência artificial erra com frequência: o limite exato do prazo, a diferença entre conjunto vazio e desempenho zero, e a garantia de que a função não altera a entrada.

### 2.1 Cenários de aceite

| CA-01 | Cálculo correto das métricas com prioridades diferentes (Sucesso) |
|---|---|
| **DADO**   | Um conjunto de seis tarefas válidas, sendo quatro concluídas (duas de prioridade alta, uma média e uma baixa), uma pendente e uma cancelada, com datas coerentes e duas delas concluídas após o prazo                                                                                                               |
| **QUANDO** | O analisador de tarefas for executado sobre esse conjunto                                                                                                                                                                                                                                                           |
| **ENTÃO**  | Deve retornar quantidade_tarefas igual a 4, tempo_medio_conclusao_min igual à média dos tempos das quatro concluídas, taxa_atraso_percentual igual a 50.0 e indicadores_por_prioridade com exatamente três chaves, cada uma trazendo as três métricas calculadas apenas sobre as tarefas daquela prioridade |

| CA-02 | Entrada com datas inválidas (Exceção) |
|---|---|
| **DADO**   | Um conjunto contendo uma tarefa concluída cuja data_conclusao é anterior à data_criacao                                     |
| **QUANDO** | O analisador de tarefas for executado                                                                                         |
| **ENTÃO**  | Deve levantar TarefaInvalidaError, sem calcular métrica alguma, com mensagem indicando o id_tarefa e o campo data_conclusao |

| CA-03 | Conjunto sem tarefas concluídas, risco de divisão por zero (Exceção) |
|---|---|
| **DADO**   | Um conjunto com três tarefas válidas, todas com status "pendente" ou "cancelada"                                    |
| **QUANDO** | O analisador de tarefas for executado                                                                               |
| **ENTÃO**  | Deve levantar SemTarefasConcluidasError antes de qualquer divisão, com mensagem clara de que não há base de cálculo |

| CA-04 | Lista de entrada vazia (Exceção) |
|---|---|
| **DADO**   | Uma lista de tarefas vazia                                                       |
| **QUANDO** | O analisador de tarefas for executado                                            |
| **ENTÃO**  | Deve levantar SemTarefasConcluidasError, com o mesmo tratamento do cenário CA-03 |

| CA-05 | Tarefas não concluídas são ignoradas sem erro (Sucesso) |
|---|---|
| **DADO**   | Um conjunto com duas tarefas concluídas e cinco tarefas pendentes ou canceladas, todas válidas                |
| **QUANDO** | O analisador de tarefas for executado                                                                         |
| **ENTÃO**  | Deve retornar quantidade_tarefas igual a 2, considerando somente as tarefas concluídas, sem levantar exceção |

| CA-06 | Conclusão exatamente no prazo não conta como atraso (Fronteira) |
|---|---|
| **DADO**   | Um conjunto com duas tarefas concluídas, uma com data_conclusao idêntica ao prazo e outra com um minuto de atraso  |
| **QUANDO** | O analisador de tarefas for executado                                                                               |
| **ENTÃO**  | Deve retornar taxa_atraso_percentual igual a 50.0, contabilizando apenas a tarefa estritamente posterior ao prazo |

| CA-07 | Valor fora da enumeração de prioridade (Exceção) |
|---|---|
| **DADO**   | Um conjunto contendo uma tarefa com prioridade "urgente", valor não previsto no contrato |
| **QUANDO** | O analisador de tarefas for executado                                                    |
| **ENTÃO**  | Deve levantar TarefaInvalidaError, informando o campo prioridade e os valores aceitos    |

| CA-08 | Imutabilidade da entrada (Contrato) |
|---|---|
| **DADO**   | Um conjunto válido de tarefas e uma cópia desse mesmo conjunto feita antes da execução                       |
| **QUANDO** | O analisador de tarefas for executado                                                                        |
| **ENTÃO**  | O conjunto original deve permanecer idêntico à cópia, comprovando que a função não altera os dados recebidos |

### 2.2 Planejamento do Test Harness

O Test Harness é o mecanismo que transforma os cenários acima em validação objetiva do código gerado. Ele será implementado em tests/test_harness.py com pytest, única dependência externa autorizada no projeto.

A conversão segue quatro passos:

  - Cada cenário de aceite vira exatamente uma função de teste, nomeada de forma a descrever o comportamento verificado, e não o número do cenário.

  - Os dados de entrada de cada cenário são construídos em fixtures do pytest, o que impede que um teste contamine o outro e deixa explícito o conjunto usado.

  - Os cenários de exceção usam pytest.raises com o argumento match, garantindo que não apenas o tipo da exceção esteja correto, mas também que a mensagem identifique a tarefa e o campo problemáticos.

  - Variações do mesmo comportamento, como diferentes valores inválidos de prioridade, usam pytest.mark.parametrize em vez de testes duplicados.

O mapeamento entre cenário e teste é o que garante rastreabilidade: todo requisito tem um teste, e todo teste aponta para um requisito.

| Cenário | Função de teste | Forma de validação |
|---|---|---|
| CA-01       | test_calcula_metricas_gerais_e_por_prioridade        | assert de igualdade sobre cada campo do dicionário de saída            |
| CA-02       | test_data_conclusao_anterior_a_criacao_levanta_erro | pytest.raises(TarefaInvalidaError) com match no id da tarefa           |
| CA-03       | test_sem_tarefas_concluidas_levanta_erro              | pytest.raises(SemTarefasConcluidasError)                               |
| CA-04       | test_lista_vazia_levanta_erro                          | pytest.raises(SemTarefasConcluidasError)                               |
| CA-05       | test_ignora_pendentes_e_canceladas                     | assert sobre quantidade_tarefas                                       |
| CA-06       | test_conclusao_no_prazo_nao_e_atraso                 | assert sobre taxa_atraso_percentual                                  |
| CA-07       | test_prioridade_invalida_levanta_erro                  | pytest.raises(TarefaInvalidaError) parametrizado com valores inválidos |
| CA-08       | test_nao_altera_lista_de_entrada                      | assert de igualdade contra copy.deepcopy do conjunto original          |

Critério de aceitação do harness: o comando abaixo deve terminar sem falha e sem teste ignorado antes de qualquer código ser considerado homologado.

```bash
pytest -v tests/test_harness.py
```

Enquanto os oito testes não passarem, o código gerado pela inteligência artificial não é aceito, independentemente de parecer correto na leitura.

## 3. Governança de contexto e regras para agentes de IA (CONTEXT_RULES)

Esta seção será versionada no repositório como CONTEXT_RULES.md e fornecida ao assistente de inteligência artificial junto de cada solicitação. Ela existe porque o modelo não tem memória do projeto: sem regras persistentes, ele preenche as lacunas com suposições plausíveis, e é exatamente aí que nascem a inconsistência e a alucinação.

### 3.1 Diretrizes arquiteturais obrigatórias

  - Python 3.11 ou superior como versão mínima obrigatória.

  - Type hints em todas as funções, métodos e parâmetros, incluindo o tipo de retorno.

  - Princípio da responsabilidade única (SRP) e código limpo segundo a PEP 8, com limite de 100 colunas por linha.

  - Documentação formal no padrão Google style docstrings para o módulo, as classes, as funções e os parâmetros.

  - Funções pequenas, coesas e com um único propósito, separando validação, cálculo e formatação da saída.

  - Tratamento de exceções específico, com mensagens claras que identifiquem a tarefa e o campo responsáveis pelo erro.

  - Logs estruturados com o módulo padrão logging, em nível INFO para o fluxo normal e WARNING para tarefas descartadas.

  - Nomes de variáveis e funções descritivos, em português, coerentes com os termos usados neste contrato.

  - Uso exclusivo da biblioteca padrão do Python no código de produção. Apenas o pytest é permitido no código de teste.

  - Estruturas de dados imutáveis sempre que possível, com dataclasses congeladas para representar a tarefa.

### 3.2 Proibições explícitas

As proibições são mais eficazes que as permissões, porque delimitam o espaço de resposta do modelo. Cada item abaixo é uma condição de rejeição do código gerado.

  - Não utilizar bibliotecas externas não autorizadas, o que inclui pandas, numpy e qualquer dependência de terceiros no código de produção.

  - Não alterar, remover ou adaptar os cenários de teste definidos nesta especificação.

  - Não modificar a estrutura de pastas definida na seção 4.

  - Não persistir dados em arquivos, em banco de dados ou em qualquer forma de estado global.

  - Não alterar a assinatura, o nome ou os parâmetros das funções públicas sem autorização registrada.

  - Não gerar código sem os testes correspondentes para cada nova funcionalidade.

  - Não inserir código duplicado ou desnecessário, nem funcionalidades que este contrato não pediu.

  - Não assumir comportamento não especificado. Diante de ambiguidade, perguntar antes de implementar.

  - Não retornar valores diferentes dos definidos no contrato de saída, nem em tipo nem em unidade.

  - Não comentar código em excesso, apenas onde a intenção não for evidente pela leitura.

  - Não acessar rede, sistema de arquivos, variáveis de ambiente ou relógio do sistema dentro da função de análise.

### 3.3 Regras de interação com a inteligência artificial

  - Fornecer sempre o contexto completo antes da solicitação, anexando esta especificação e o arquivo CONTEXT_RULES.md.

  - Validar se a IA compreendeu o contrato pedindo que ela reformule as regras com as próprias palavras antes de gerar código.

  - Solicitar explicação da decisão sempre que houver dúvida sobre a solução proposta.

  - Revisar criticamente todo o código gerado, linha por linha, sem aceitar sugestão por conveniência.

  - Rejeitar e registrar toda resposta que viole as proibições da seção 3.2, anotando o caso no relatório de governança da Fase 3.

  - Nunca colar segredo, credencial ou dado pessoal real no prompt.

  - Tratar a IA como executora e não como autora: a decisão técnica e a responsabilidade permanecem humanas.

## 4. Arquitetura do repositório e preparação para Git e GitHub

### 4.1 Árvore do repositório

A estrutura abaixo será criada no GitHub na Fase 2 e não pode ser alterada pelo assistente de inteligência artificial. Ela separa três coisas que costumam se misturar: o que foi especificado, o que valida, e o que foi gerado.

```text
sdd-task-analyzer/
├── README.md                     # Visão geral do projeto no GitHub
├── CONTEXT_RULES.md              # Regras persistentes fornecidas à IA (seção 3)
├── .gitignore                    # Arquivos e pastas ignorados pelo Git
├── requirements.txt              # Dependências autorizadas (apenas pytest)
├── specs/
│   └── task_analyzer_spec.md     # Especificação SDD derivada deste documento
├── tests/
│   └── test_harness.py           # Testes automatizados de validação (pytest)
└── src/
    └── task_analyzer.py          # Código gerado via IA e homologado
```

A separação entre specs, tests e src é o que materializa o SDD. A especificação nasce primeiro e é imutável durante a geração; o teste nasce em seguida e define o critério objetivo; o código é o último e é o único artefato descartável dos três, porque pode ser regenerado a partir dos outros dois.

### 4.2 Plano de homologação humana

Todo código gerado pela inteligência artificial passa por revisão crítica humana antes de ser aceito e versionado. A homologação segue a sequência abaixo, e nenhuma etapa pode ser pulada por pressa de prazo.

| Passo | Verificação | O que é feito |
|---|---|---|
| 1         | Execução completa dos testes automatizados | Rodar pytest -v e confirmar que os oito cenários de aceite passam, sem teste ignorado.                                                |
| 2         | Conformidade com o contrato de negócio     | Conferir campo a campo se as entradas, as saídas e as regras RN-01 a RN-11 foram respeitadas.                                         |
| 3         | Aderência às CONTEXT_RULES                | Verificar type hints, docstrings, limite de linha, ausência de biblioteca externa e cada proibição da seção 3.2.                      |
| 4         | Análise de qualidade e legibilidade        | Avaliar coesão das funções, clareza dos nomes, tratamento de erro e ausência de duplicação.                                           |
| 5         | Testes manuais complementares              | Exercitar casos de borda não cobertos automaticamente, como conjunto muito grande e datas em fusos distintos.                         |
| 6         | Aprovação e registro                       | Somente após as cinco verificações acima, aprovar o pull request, registrar no histórico o que foi alterado e então permitir o merge. |

Esse processo garante que a inteligência artificial seja uma ferramenta produtiva, mas que a decisão final e a responsabilidade técnica permaneçam humanas. Se o código passa nos testes e ainda assim não convence na leitura, ele é rejeitado: teste verde não é sinônimo de código correto, apenas de código que atende ao que foi testado.

### 4.3 Estratégia de versionamento

| Aspecto | Definição |
|---|---|
| Modelo de branches | Git Flow simplificado, com main estável, develop de integração e feature/\<numero-issue\>-\<slug\> para cada entrega.      |
| Commits            | Pequenos, atômicos e descritivos, no padrão Conventional Commits, por exemplo feat: calcula taxa de atraso por prioridade. |
| Pull Requests      | Obrigatórios para todo código gerado por IA, com a descrição indicando qual cenário de aceite o código atende.             |
| Revisão            | Nenhum merge ocorre sem a homologação humana descrita na seção 4.2 concluída e registrada.                                 |
| Tags               | Uma tag por entrega avaliativa, começando em v1.0.0 ao final da Fase 2.                                                    |
| Rastreabilidade    | Cada requisito desta especificação tem um teste associado, e cada teste tem um commit que o introduziu.                    |

## Considerações finais

Esta especificação é o contrato. Na Fase 2, o assistente de inteligência artificial atuará como executor sobre este documento, e não como autor da solução, e o Test Harness dirá objetivamente se o resultado atende ao que foi acordado aqui. O papel que assumo no projeto é o de arquiteto da especificação, curador do contexto e homologador crítico do que for gerado.

A qualidade do código da próxima fase será, em boa medida, consequência direta da precisão deste texto. Foi por isso que as ambiguidades foram fechadas agora: o comportamento no limite exato do prazo, a diferença entre conjunto vazio e desempenho zero, a unidade de cada métrica e o momento certo do arredondamento. Cada uma dessas decisões, se deixada em aberto, viraria uma suposição do modelo.
