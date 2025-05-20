# Importação de Projetos

Este documento descreve como utilizar o script de importação de projetos para o sistema GEPES Classifier.

## Pré-requisitos

- Python 3.8+
- PostgreSQL configurado e acessível
- Variáveis de ambiente configuradas no arquivo `.env`

## Preparação do Arquivo JSON

Prepare um arquivo JSON contendo a lista de projetos a serem importados. O arquivo deve seguir o formato do exemplo abaixo:

```json
[
  {
    "codigo_projeto": "PIBM-2504.0038",
    "unidade_embrapii": "SENAI ISI BIOMASSA",
    "data_contrato": 1745798400000,
    "data_inicio": 1745798400000,
    "data_termino": 1808870400000,
    "status": "Em andamento",
    "tipo_projeto": "Produto",
    "titulo": "RBNCHAR: Novo Biomaterial A Partir Da Neutralização Do Resíduo De Bauxita (RB) Via Pirólise Sinérgica Com Biomassa",
    "titulo_publico": "Novo Biomaterial A Partir Da Neutralização Do Resíduo De Bauxita (RB) Via Pirólise Sinérgica Com Biomassa",
    "objetivo": "Desenvolver provas de conceito com validações em escala de laboratório...",
    "descricao_publica": "Novo Biomaterial A Partir Da Neutralização Do Resíduo De Bauxita (RB) Via Pirólise Sinérgica Com Biomassa.",
    "valor_embrapii": 312823.0,
    "valor_empresa": 469281.0,
    "valor_unidade_embrapii": 156458.0,
    "codigo_negociacao": "NIBM-2504.00145"
    // ... outros campos
  },
  // ... outros projetos
]
```

### Campos Importantes

- `codigo_projeto`: Identificador único do projeto (obrigatório)
- `data_contrato`, `data_inicio`, `data_termino`: Timestamps em milissegundos
- `valor_embrapii`, `valor_empresa`, `valor_unidade_embrapii`: Valores numéricos

Um exemplo completo está disponível no arquivo `example_projects.json`.

## Executando a Importação

Para importar os projetos, execute o script `import_projects.py` passando o caminho do arquivo JSON como argumento:

```bash
python import_projects.py caminho/para/seu/arquivo.json
```

Por exemplo:

```bash
python import_projects.py example_projects.json
```

## Comportamento do Script

O script realiza as seguintes operações:

1. Lê o arquivo JSON fornecido
2. Para cada projeto no JSON:
   - Verifica se o projeto já existe no banco (usando `codigo_projeto`)
   - Se já existir, ignora e passa para o próximo
   - Se não existir, converte os campos de data e insere no banco
3. Exibe estatísticas da importação ao final do processo

### Observações

- O script apenas insere novos projetos, não atualiza projetos existentes
- Os campos relacionados a categorias (`Categoria` e `TecnologiaVerde`) não são preenchidos durante a importação, devendo ser configurados posteriormente através da interface do sistema
- Os campos de data são convertidos de timestamp (milissegundos) para objetos de data
- O valor total e os percentuais são calculados automaticamente

## Tratamento de Erros

O script registra e exibe erros encontrados durante o processo de importação. Cada erro é associado ao código do projeto correspondente, facilitando a identificação e correção de problemas.

## Exemplo de Saída

```
Iniciando importação de 2 projetos...
Projeto inserido: PIBM-2504.0038
Projeto inserido: PIAG-2504.0004

Estatísticas de importação:
Total de projetos processados: 2
Projetos inseridos: 2
Projetos ignorados (já existentes): 0
Erros: 0

Importação concluída!
```

## Solução de Problemas

Se encontrar erros durante a importação:

1. Verifique se o arquivo JSON está corretamente formatado
2. Confirme que o banco de dados está acessível e as credenciais estão corretas
3. Verifique se os campos obrigatórios estão presentes no JSON
4. Analise os erros específicos reportados pelo script
