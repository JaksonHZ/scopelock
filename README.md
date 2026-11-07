# ScopeLock 🔒

> **Zero-dependency, AST-based anti-overengineering and code deduplication guardrail for AI coding agents.**

Agentes autônomos de código (Claude Code, Cursor, Aider, Copilot Workspace) têm um vício em comum: **eles adoram reinventar a roda**. Quando precisam de um utilitário (como `slugify`, `format_currency` ou normalização de datas), a maioria dos modelos simplesmente gera uma função nova do zero, inchando o repositório com código duplicado em vez de reaproveitar o que já existe em `helpers/` ou `utils/`.

O **ScopeLock** analisa a árvore sintática abstrata (AST) do projeto e atua como uma barreira antes de cada commit. Se o agente tentar reimplementar uma função funcionalmente similar ou com mesmo fluxo de instruções, o ScopeLock barra a alteração e indica qual utilitário existente deve ser importado.

---

## 🎯 Por que o ScopeLock existe?

1. **Combate a "Amnésia" dos Agentes:** Modelos de linguagem nem sempre têm a árvore completa de utilitários no contexto imediato.
2. **Zero Dependências Pesadas:** Feito com o módulo nativo `ast` do Python. Rápido, leve e roda em milissegundos.
3. **AST + Heurística Semântica:** Não compara apenas nomes de funções; avalia a lista de parâmetros, fluxo de instruções sintáticas e docstrings.

---

## 🚀 Como Usar

### 1. Varredura no Repositório

```bash
# Analisa todo o repositório atual
python3 -m scopelock.cli .

# Analisa com limiar de sensibilidade customizado (0.0 a 1.0)
python3 -m scopelock.cli . --threshold 0.70
```

### 2. Analisar Apenas Arquivos Alterados pelo Agente

```bash
python3 -m scopelock.cli . --file src/novo_modulo.py
```

### 3. Como Git Hook (Pre-commit)

Copie o hook de exemplo para o seu repositório:

```bash
cp examples/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

---

## 🧪 Demonstração

Suponha que seu projeto já tenha `existing_utils.py` com `slugify()`. O agente de IA então cria `agent_duplicated_code.py` com `slugify_text()`:

```bash
$ python3 -m scopelock.cli examples/

🔍 ScopeLock: Varredura de AST e Duplicação Funcional
📁 Diretório: /home/jakson/pessoal/scopelock/examples
📊 Funções analisadas no inventário: 4

⚠️  Atenção: 2 potencial(is) duplicação(ões) encontrada(s):

[1] 65% similaridade — Mesma lista de parâmetros + Mesmo fluxo AST + Docstrings com 100% semelhança
    ❌ Função:   'slugify' em existing_utils.py:6
    💡 Já existe: 'slugify_text' em agent_duplicated_code.py:6
    👉 Sugestão: Reaproveite a função existente em vez de reimplementar.
```

---

## 📄 Licença

MIT — sinta-se livre para usar, adaptar e integrar nos seus fluxos de agentes.
