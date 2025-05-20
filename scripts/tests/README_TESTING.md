# Instruções para Teste e Depuração da Integração com IA

Este documento contém instruções para testar e depurar a integração com a API OpenAI para classificação de projetos.

## Pré-requisitos

1. Certifique-se de que o ambiente virtual está ativado
2. Tenha uma chave de API válida da OpenAI
3. Configure a chave da API no arquivo `.env` ou nas configurações do sistema

```
OPENAI_API_KEY=sua_chave_api_aqui
```

## Scripts Disponíveis

### 1. Adicionar Categorias de Exemplo

Se você não tiver categorias no banco de dados, pode adicionar algumas categorias de exemplo para teste:

```bash
python add_sample_categories.py
```

Este script adiciona categorias de exemplo ao banco de dados, incluindo macroáreas, segmentos e domínios, seguindo a estrutura hierárquica necessária.

### 2. Depurar as Categorias

Para verificar se as categorias estão sendo obtidas corretamente do banco de dados e se a estrutura hierárquica está sendo mantida:

```bash
python debug_categories.py
```

Este script mostra:
- As listas de categorias por tipo
- A estrutura hierárquica (macroárea > segmento > domínio)
- Os dados de AIA formatados para o prompt
- As classes e subclasses de tecnologias verdes
- O total de categorias no banco de dados

### 3. Testar a Integração com a API OpenAI

Para testar a integração completa com a API OpenAI:

```bash
python test_ai_integration.py
```

Este script:
- Cria um projeto de exemplo
- Chama o método `suggest_categories` para obter sugestões da IA
- Imprime o resultado completo e as categorias sugeridas

## Fluxo de Teste Recomendado

1. Execute `add_sample_categories.py` para adicionar categorias de exemplo ao banco de dados (se necessário)
2. Execute `debug_categories.py` para verificar se as categorias estão sendo obtidas corretamente
3. Execute `test_ai_integration.py` para testar a integração completa com a API OpenAI

## Depuração de Problemas Comuns

### Não há categorias no banco de dados

Se o script `debug_categories.py` mostrar que não há categorias no banco de dados, execute o script `add_sample_categories.py` para adicionar categorias de exemplo.

### Erro na chamada da API OpenAI

Verifique se a chave da API está configurada corretamente no arquivo `.env` ou nas configurações do sistema.

### Estrutura hierárquica incorreta

Verifique se as categorias no banco de dados seguem o formato correto:
- Macroáreas: valor simples (ex: "Tecnologia da Informação")
- Segmentos: formato "Macroárea|Segmento" (ex: "Tecnologia da Informação|Inteligência Artificial")
- Domínios: formato "Macroárea|Segmento|Domínio" (ex: "Tecnologia da Informação|Inteligência Artificial|Machine Learning")

### Resposta da IA em formato incorreto

Se a resposta da IA não estiver no formato JSON esperado, verifique o método `_parse_ai_response` em `app/ai_integration.py`. Este método tenta extrair o JSON da resposta da IA e retorna um objeto de erro se não conseguir.

## Modificações no Código

Se você precisar fazer modificações no código:

1. Edite o arquivo `app/ai_integration.py`
2. Execute os scripts de teste para verificar se as modificações funcionam corretamente
3. Se necessário, ajuste os prompts para melhorar a qualidade das sugestões da IA

## Logs e Depuração Avançada

Para depuração avançada, você pode adicionar logs ao código:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Adicione logs onde necessário
logger.debug("Valor da variável: %s", valor)
```

Isso ajudará a identificar onde os problemas estão ocorrendo.
