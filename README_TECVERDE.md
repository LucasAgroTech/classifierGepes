# Tecnologias Verdes - Documentação

Este documento descreve a implementação da funcionalidade de consulta dinâmica de classes e subclasses de tecnologias verdes a partir do banco de dados, substituindo as listas hardcoded anteriores.

## Arquivos Criados/Modificados

1. **app/ai_integration.py**
   - Modificados os métodos `_get_tecverde_classes()` e `_get_tecverde_subclasses()` para consultar o banco de dados.

2. **app/helpers.py**
   - Adicionadas funções auxiliares para gerenciar categorias de tecnologias verdes:
     - `add_tecverde_categories()`: Adiciona categorias padrão ao banco de dados.
     - `get_tecverde_categories()`: Retorna as categorias do banco de dados.

3. **Scripts de Utilidade**
   - `add_tecverde_categories.py`: Adiciona categorias padrão ao banco de dados usando SQLAlchemy.
   - `add_tecverde_categories_sql.py`: Adiciona categorias padrão ao banco de dados usando SQL direto.
   - `list_tecverde_categories.py`: Lista as categorias existentes no banco de dados usando SQLAlchemy.
   - `list_tecverde_categories_sql.py`: Lista as categorias existentes no banco de dados usando SQL direto.

## Formato dos Dados no Banco

### Classes de Tecnologias Verdes
- **tipo**: 'tecverde_classe'
- **valor**: 'Nome da Classe'
- **ativo**: True

### Subclasses de Tecnologias Verdes
- **tipo**: 'tecverde_subclasse'
- **valor**: 'Nome da Classe|Subclasse1; Subclasse2; Subclasse3'
- **ativo**: True

## Categorias Implementadas

### Classes
- Transporte
- Energia
- Poluição e Resíduos
- Água
- Agricultura e Silvicultura
- Produtos, Materiais e Processos
- Construção e Edificações

### Subclasses (exemplos)
- **Transporte**: Soluções de transporte baseadas em TIC, Veículos elétricos / híbridos, Transporte marítimo / hidroviário, etc.
- **Energia**: Hidrogênio e células a combustível, Eficiência energética, Armazenamento de energia, Solar, Eólica, etc.
- **Poluição e Resíduos**: Reciclagem e reutilização, Tratamento de resíduos sólidos, Captura e armazenamento de carbono, etc.
- **Água**: Saneamento, Proteção costeira, Controle de enchentes, Tratamento de água, etc.
- **Agricultura e Silvicultura**: Estufas e ambientes internos, Gestão do uso da terra, Produção florestal, etc.
- **Produtos, Materiais e Processos**: Materiais aprimorados, Produtos biodegradáveis, etc.
- **Construção e Edificações**: Material de construção, Iluminação, Isolamento térmico, etc.

## Como Configurar

Para configurar o sistema com as categorias de tecnologias verdes, execute:

```bash
python add_tecverde_categories_sql.py
```

Este script irá:
1. Remover categorias existentes (se houver).
2. Adicionar as novas categorias de tecnologias verdes ao banco de dados.

## Como Verificar as Categorias

Para listar as categorias de tecnologias verdes no banco de dados, execute:

```bash
python list_tecverde_categories_sql.py
```

## Como Adicionar Novas Categorias

Para adicionar novas categorias ou atualizar as existentes, você pode:

1. Modificar os dicionários `tecverde_classes` e `tecverde_subclasses` em `add_tecverde_categories_sql.py` e executar o script.
2. Adicionar diretamente no banco de dados usando SQL:
   ```sql
   INSERT INTO gepes.categoria_listas (tipo, valor, ativo) 
   VALUES ('tecverde_classe', 'Nova Classe', true);
   
   INSERT INTO gepes.categoria_listas (tipo, valor, ativo) 
   VALUES ('tecverde_subclasse', 'Nova Classe|Subclasse1; Subclasse2', true);
   ```

## Limitações e Considerações

1. **Limite de Caracteres**: O campo `valor` na tabela `categoria_listas` tem um limite de 255 caracteres. Para subclasses com muitos valores, o script trunca automaticamente o valor para caber nesse limite.

2. **Sem Coluna de Descrição**: A implementação atual não utiliza uma coluna separada para descrições. As descrições são mantidas em memória no código.

## Benefícios da Nova Implementação

1. **Flexibilidade**: As categorias podem ser atualizadas sem modificar o código.
2. **Manutenção**: Centraliza a gestão das categorias no banco de dados.
3. **Consistência**: Garante que as mesmas categorias sejam usadas em todo o sistema.
4. **Extensibilidade**: Facilita a adição de novas categorias ou a modificação das existentes.
