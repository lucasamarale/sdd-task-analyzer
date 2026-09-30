# CONTEXT_RULES

Regras de governança para qualquer assistente de inteligência artificial que gere ou altere código neste repositório.

Este arquivo é a seção 3 da especificação da Fase 1, transposta para o repositório e ajustada à versão 1.1 do contrato. **Ele é fornecido ao assistente junto com `specs/task_analyzer_spec.md` em toda solicitação.** O modelo não tem memória do projeto: sem estas regras, ele preenche as lacunas com suposições, e suposição em código vira defeito.

**Prioridade em caso de conflito:** a especificação vale mais que este arquivo, e este arquivo vale mais que qualquer instrução dada no prompt.

---

## 1. Diretrizes obrigatórias

1. **Python 3.11 ou superior.**
2. **Type hints em 100% das funções, métodos e parâmetros**, incluindo o tipo de retorno.
3. **PEP 8**, com limite de 100 colunas por linha.
4. **Docstrings no padrão Google** para o módulo, as classes e as funções públicas.
5. **Funções pequenas e com um único propósito**, separando validação, cálculo e montagem da saída.
6. **Tratamento de erro com exceção específica.** Toda violação do contrato de entrada levanta `TaskValidationError`, com mensagem que identifique o `id_tarefa` e o campo responsável. Nunca `Exception` genérica, nunca `assert` para validar entrada.
7. **Prevenção de divisão por zero.** Nenhuma divisão sem verificar antes o denominador. Denominador zero devolve `0.0`, conforme a RN-09.
8. **Log com o módulo padrão `logging`**, em nível INFO ao concluir a análise, com os totais. Nunca `print`.
9. **Somente a biblioteca padrão** no código de produção. O `pytest` é a única dependência externa, e apenas nos testes.
10. **Estruturas imutáveis sempre que possível**, com a tarefa representada por dataclass congelada.
11. **Nomes em português**, coerentes com os termos da especificação. Exceção: os nomes públicos fixados pelo enunciado da Fase 2, `analyze_tasks` e `TaskValidationError` (MUD-10).

## 2. Proibições

Cada item é condição de rejeição do código gerado.

1. **Não usar bibliotecas externas** no código de produção: nada de pandas, numpy ou qualquer dependência de terceiros.
2. **Não alterar, remover ou enfraquecer os testes** de `tests/test_harness.py` para fazer o código passar.
3. **Não modificar a estrutura de pastas** definida na seção 4.1 da especificação.
4. **Não persistir dados** em arquivo, banco ou estado global.
5. **Não alterar a assinatura, o nome ou os parâmetros das funções públicas** sem autorização registrada na especificação.
6. **Não retornar valores diferentes do contrato de saída**, nem em tipo, nem em unidade, nem em nome de campo. O tempo é em horas.
7. **Não arredondar valores intermediários.** Arredondamento só na montagem da saída (RN-05).
8. **Não levantar exceção para lista vazia ou sem tarefa concluída.** Esses casos devolvem `0.0` (RN-09).
9. **Não acessar rede, sistema de arquivos, variáveis de ambiente ou o relógio do sistema** dentro da análise.
10. **Não alterar a lista recebida**, nem reordenar, nem remover itens.
11. **Não inventar comportamento.** O que não está na especificação não entra no código. Diante de ambiguidade, perguntar antes de implementar.
12. **Não gerar código duplicado, nem comentário em excesso.** Comentário só onde a intenção não fica evidente pela leitura.

## 3. Regras de interação com a IA

1. **Contexto completo antes do pedido.** Anexar sempre a especificação e este arquivo.
2. **Confirmar a compreensão antes do código.** Pedir que o assistente reformule, com as próprias palavras, as regras de negócio e as proibições, e só então gerar.
3. **Pedir justificativa** sempre que houver dúvida sobre uma decisão da solução proposta.
4. **Revisar linha por linha.** Nenhuma sugestão é aceita por conveniência.
5. **Registrar toda violação** destas regras encontrada no código gerado, para o relatório de governança da Fase 3.
6. **Nunca colar segredo, credencial ou dado pessoal real** no prompt.
7. **A IA executa, não decide.** A decisão técnica e a responsabilidade permanecem humanas, e se materializam na homologação do Pull Request.
