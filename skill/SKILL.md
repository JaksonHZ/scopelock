---
name: scopelock
description: Previne overengineering, duplicação funcional e inchaço de código inspecionando a AST antes de criar novos utilitários.
---

# ScopeLock — Guardrail Anti-Overengineering para Agentes

Esta skill capacita o agente a verificar proativamente se uma função ou utilitário que ele planeja criar já existe na base de código, evitando duplicações desnecessárias.

## Quando Usar Esta Skill

Ative e utilize o ScopeLock sempre que:
1. Você estiver prestes a criar uma nova função utilitária (como formatação de strings, cálculos comuns, validações, manipuladores de data ou wrappers de API).
2. For salvar ou propor alterações em arquivos novos ou existentes.
3. Quiser validar se o repositório está limpo antes de concluir uma tarefa de codificação.

## Como Executar

### 1. Inspecionar um arquivo específico que você acabou de criar/alterar
Antes de dar a tarefa como concluída, rode:

```bash
python3 -m scopelock.cli . --file caminho/do/arquivo_alterado.py
```

### 2. Inspecionar o projeto inteiro
```bash
python3 -m scopelock.cli .
```

### 3. O que fazer ao encontrar duplicatas?
Se o ScopeLock alertar:
```
⚠️  Atenção: 1 potencial duplicação encontrada:
    ❌ Função:   'format_date' em novo_modulo.py
    💡 Já existe: 'format_timestamp' em utils/dates.py
    👉 Sugestão: Reaproveite a função de 'utils/dates.py' em vez de reimplementar.
```

**Ação obrigatória:**
- Remova a função duplicada que você criou.
- Importe a função existente: `from utils.dates import format_timestamp`.
- Adapte a chamada no seu código.
