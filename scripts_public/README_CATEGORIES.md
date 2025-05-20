# Importação de Categorias

Este documento descreve como utilizar o script `import_categories.py` para importar categorias a partir de um arquivo JSON.

## Estrutura do JSON

O arquivo JSON deve conter uma lista de objetos com a seguinte estrutura:

```json
[
  {
    "N": 45,
    "Macroárea": "Agro e Alimentos",
    "Segmento": "Agricultura",
    "Domínios Afeitos": "Fertilizantes e nutrição vegetal; Controle biológico de pragas; Controle químico de pragas; ..."
  },
  ...
]
```

Onde:
- `N`: Número identificador (não utilizado na importação)
- `Macroárea`: Nome da macroárea
- `Segmento`: Nome do segmento dentro da macroárea
- `Domínios Afeitos`: Lista de domínios separados por ponto e vírgula (;)

## Hierarquia das Categorias

O script mantém a hierarquia entre as categorias:
1. Macroárea: Nível mais alto
2. Segmento: Pertence a uma macroárea
3. Domínio: Pertence a um segmento

## Como Executar o Script

1. Certifique-se de que o ambiente virtual está ativado e as dependências estão instaladas
2. Execute o script:
   ```
   python3 import_categories.py
   ```
3. Quando solicitado, informe o caminho para o arquivo JSON contendo as categorias
4. O script irá:
   - Limpar as categorias existentes na tabela `categoria_listas`
   - Importar as novas categorias do arquivo JSON
   - Exibir um relatório do processo

## Formato dos Dados no Banco

As categorias são armazenadas na tabela `categoria_listas` com os seguintes campos:
- `tipo`: Tipo da categoria ('macroárea', 'segmento' ou 'dominio')
- `valor`: Valor da categoria, com a seguinte estrutura:
  - Para macroáreas: `"Nome da Macroárea"`
  - Para segmentos: `"Nome da Macroárea|Nome do Segmento"`
  - Para domínios: `"Nome da Macroárea|Nome do Segmento|Nome do Domínio"`
- `ativo`: Indica se a categoria está ativa (sempre `true` para novas importações)

## Exemplo

Arquivo JSON:
```json
[
  {
    "Macroárea": "Energia renovável",
    "Segmento": "Energia solar fotovoltaica",
    "Domínios Afeitos": "Painéis bifaciais; Inversores e sistemas de controle"
  }
]
```

Registros criados na tabela `categoria_listas`:
1. `tipo='macroárea', valor='Energia renovável', ativo=true`
2. `tipo='segmento', valor='Energia renovável|Energia solar fotovoltaica', ativo=true`
3. `tipo='dominio', valor='Energia renovável|Energia solar fotovoltaica|Painéis bifaciais', ativo=true`
4. `tipo='dominio', valor='Energia renovável|Energia solar fotovoltaica|Inversores e sistemas de controle', ativo=true`

## Observações

- O script limpa todos os dados existentes na tabela `categoria_listas` antes de importar os novos dados
- Domínios duplicados são ignorados
- O script trata erros de banco de dados e exibe mensagens informativas durante o processo
