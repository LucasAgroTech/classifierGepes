# Migração da Tabela Projetos

Este documento contém instruções para atualizar o modelo `Projeto` e migrar os dados para o novo formato em produção.

## Visão Geral

O processo de migração consiste em:

1. Atualizar o modelo `Projeto` em `app/models.py` para incluir todos os campos do formato JSON
2. Resetar a tabela `projetos` no banco de dados
3. Importar os dados do JSON para a tabela

## Arquivos Criados

- `reset_projetos_table.py`: Script para resetar a tabela `projetos` com o novo esquema
- `import_json_data.py`: Script para importar dados de um arquivo JSON para a tabela `projetos`
- `migrate_production.py`: Script que combina os dois anteriores para facilitar a migração em produção

## Pré-requisitos

- Arquivo `.env` configurado com a URL do banco de dados
- Arquivo JSON com os dados dos projetos no formato especificado

## Instruções para Migração em Produção

### Opção 1: Usando o script de migração completo

1. Faça backup do banco de dados atual (recomendado)
2. Execute o script de migração:

```bash
python migrate_production.py
```

3. Siga as instruções na tela:
   - Confirme que deseja continuar com a operação
   - Forneça o caminho para o arquivo JSON com os dados dos projetos

### Opção 2: Executando os scripts separadamente

Se preferir executar os scripts separadamente, siga estas etapas:

1. Faça backup do banco de dados atual (recomendado)
2. Resete a tabela `projetos`:

```bash
python reset_projetos_table.py
```

3. Importe os dados do JSON:

```bash
python import_json_data.py
```

4. Quando solicitado, forneça o caminho para o arquivo JSON com os dados dos projetos

## Formato do JSON

O arquivo JSON deve conter um array de objetos com a seguinte estrutura:

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
    "parceria_programa": "EMBRAPII CG",
    "call": "Contrato de Gestão 2",
    "cooperacao_internacional": null,
    "modalidade_financiamento": "EMBRAPII",
    "uso_recurso_obrigatorio": "Não",
    "tecnologia_habilitadora": "Não definido",
    "missoes_cndi": "Não definido",
    "area_aplicacao": "Não definido",
    "projeto": "Nome do projeto",
    "trl_inicial": "3. Estabelecimento de função crítica de forma analítica, experimental e/ou prova de conceito",
    "trl_final": "4. Validação funcional dos componentes em ambiente de laboratório",
    "valor_embrapii": 312823.0,
    "valor_empresa": 469281.0,
    "valor_unidade_embrapii": 156458.0,
    "titulo": "Título do projeto",
    "titulo_publico": "Título público do projeto",
    "objetivo": "Objetivo do projeto",
    "descricao_publica": "Descrição pública do projeto",
    "data_avaliacao": null,
    "nota_avaliacao": null,
    "observacoes": null,
    "tags": null,
    "data_extracao_dados": 1745922641609,
    "brasil_mais_produtivo": "Não definido",
    "valor_sebrae": 0.0,
    "codigo_negociacao": "NIBM-2504.00145",
    "macroentregas": 3,
    "pct_aceites": 0.0,
    "_fonte_recurso": "CG",
    "_sebrae": "Não",
    "_valor_total": 938562.0,
    "_perc_valor_embrapii": 0.3333003041,
    "_perc_valor_empresa": 0.5,
    "_perc_valor_sebrae": 0.0,
    "_perc_valor_unidade_embrapii": 0.1666996959,
    "_perc_valor_empresa_sebrae": 0.5,
    "_aia_n1_macroarea": null,
    "_aia_n2_segmento": null,
    "_aia_n3_dominio_afeito": null,
    "_aia_n3_dominio_outro": null
  },
  // ... mais projetos
]
```

## Observações Importantes

- **Backup**: Sempre faça backup do banco de dados antes de executar a migração
- **Timestamps**: Os campos de data no JSON estão em formato de timestamp em milissegundos
- **Campos Nulos**: Campos com valor `null` no JSON serão importados como `NULL` no banco de dados
- **Campos Internos**: Os campos internos do sistema (como `tecverde_se_aplica`, `ai_rating_aia`, etc.) serão mantidos, mas seus valores serão resetados

## Solução de Problemas

Se encontrar problemas durante a migração:

1. Verifique se o arquivo `.env` está configurado corretamente
2. Certifique-se de que o arquivo JSON está no formato correto
3. Verifique os logs de erro para identificar o problema específico
4. Restaure o backup do banco de dados se necessário
