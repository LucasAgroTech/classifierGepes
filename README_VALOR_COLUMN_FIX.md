# Correção da Coluna 'valor' na Tabela 'categoria_listas'

## Problema

A coluna `valor` na tabela `categoria_listas` estava definida como VARCHAR(255) no banco de dados, o que limitava o tamanho dos valores a 255 caracteres. Isso causava o truncamento de algumas subclasses de tecnologias verdes, resultando em dados incompletos nos logs:

```
INFO:app.ai_integration:Subclasses disponíveis para 'Energia': ['Hidrogênio e células a combustível', ..., 'Recuperação de c']
INFO:app.ai_integration:Subclasses disponíveis para 'Poluição e Resíduos': [..., 'Descarte de resíduos', 'E']
INFO:app.ai_integration:Subclasses disponíveis para 'Produtos, Materiais e Processos': [..., 'Produtos qu']
INFO:app.ai_integration:Subclasses disponíveis para 'Transporte': [..., 'Transpor']
```

## Solução

Foram implementadas duas soluções para este problema:

### 1. Solução Temporária (Truncamento Inteligente)

Inicialmente, modificamos o script `add_tecverde_categories_sql.py` para truncar os valores no último separador (ponto e vírgula) antes do limite de 255 caracteres, garantindo que nenhuma subclasse fosse cortada no meio:

```python
# Encontrar o último separador (ponto e vírgula) antes do limite
subclasses_truncated = subclasses[:max_subclasses_length]
last_separator = subclasses_truncated.rfind(';')

if last_separator != -1:
    # Truncar no último separador para não cortar uma subclasse no meio
    subclasses_truncated = subclasses_truncated[:last_separator]
```

### 2. Solução Definitiva (Alteração do Tipo da Coluna)

A solução definitiva foi alterar o tipo da coluna `valor` de VARCHAR(255) para TEXT, permitindo que ela armazene textos de qualquer tamanho. Para isso, criamos:

1. Um script (`alter_valor_column.py`) que executa diretamente o SQL para alterar o tipo da coluna:
   ```sql
   ALTER TABLE gepes.categoria_listas 
   ALTER COLUMN valor TYPE TEXT
   ```
2. Modificamos o script `add_tecverde_categories_sql.py` para remover a lógica de truncamento, já que não é mais necessária.

## Como Aplicar a Solução

1. Execute o script de migração para alterar o tipo da coluna:

```bash
./alter_valor_column.py
```

2. Execute o script para adicionar as categorias de tecnologias verdes completas:

```bash
./add_tecverde_categories_sql.py
```

3. Verifique se as subclasses estão completas:

```bash
./list_tecverde_categories_sql.py
```

## Impacto

Após aplicar esta solução, todas as subclasses de tecnologias verdes serão armazenadas completamente no banco de dados, sem truncamento. Isso garante que a classificação de projetos seja feita com base em dados completos e precisos.
