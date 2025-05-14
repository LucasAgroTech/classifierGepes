# GEPES Classifier

Sistema de classificação de projetos com integração de IA para sugestão de categorias.

## Requisitos

- Python 3.8+
- PostgreSQL
- Chave de API OpenAI (para funcionalidades de IA)

## Configuração Inicial

### 1. Configurar o Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows:
venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

Edite o arquivo `.env` com suas configurações:

```
# Configurações básicas
SECRET_KEY=sua-chave-secreta-aqui
FLASK_ENV=development

# Configuração do banco de dados PostgreSQL
DATABASE_URL=postgresql://username:password@host:port/database_name

# Configuração da API OpenAI
OPENAI_API_KEY=sua-chave-api-openai-aqui

# Configurações para o Heroku
WEB_CONCURRENCY=1
```

### 4. Configurar o Banco de Dados

Você pode configurar o banco de dados usando o script `setup_database.py`:

```bash
python setup_database.py
```

Este script oferece as seguintes opções:

1. Criar esquema e tabelas
2. Criar usuário administrador
3. Executar ambos (1 e 2)

#### Opção 1: Criar Esquema e Tabelas

Esta opção:
- Conecta ao banco de dados usando a URL fornecida no arquivo `.env`
- Cria o esquema `gepes` se não existir
- Cria todas as tabelas definidas nos modelos

#### Opção 2: Criar Usuário Administrador

Esta opção:
- Solicita informações para criar um usuário administrador (email, nome, senha)
- Valida as informações fornecidas
- Cria o usuário no banco de dados

#### Opção 3: Executar Ambos

Esta opção executa as opções 1 e 2 em sequência.

### 5. Executar a Aplicação

```bash
python run.py
```

A aplicação será executada em `http://localhost:5001`.

## Estrutura do Projeto

- `app/`: Diretório principal da aplicação
  - `__init__.py`: Configuração da aplicação Flask
  - `models.py`: Definição dos modelos de dados
  - `routes.py`: Rotas principais da aplicação
  - `routes_ai_ratings.py`: Rotas para avaliação de sugestões da IA
  - `forms.py`: Definição de formulários
  - `ai_integration.py`: Integração com a API OpenAI
  - `static/`: Arquivos estáticos (CSS, JS, imagens)
  - `templates/`: Templates HTML
- `config.py`: Configurações da aplicação
- `run.py`: Script para executar a aplicação
- `requirements.txt`: Dependências do projeto
- `Procfile`: Configuração para deploy no Heroku
- `create_tables.py`: Script para criar esquema e tabelas
- `create_admin_user.py`: Script para criar usuário administrador
- `setup_database.py`: Script para configuração completa do banco de dados

## Scripts de Configuração

### create_tables.py

Este script cria o esquema `gepes` e todas as tabelas definidas nos modelos. Pode ser executado diretamente:

```bash
python create_tables.py
```

### create_admin_user.py

Este script cria um usuário administrador no banco de dados. Pode ser executado diretamente:

```bash
python create_admin_user.py
```

### setup_database.py

Este script combina as funcionalidades dos dois scripts anteriores, oferecendo um menu interativo para configuração do banco de dados:

```bash
python setup_database.py
```

## Funcionalidades

- Autenticação de usuários
- Listagem de projetos
- Categorização de projetos
- Sugestão de categorias usando IA (OpenAI)
- Avaliação de sugestões da IA
- Visualização de logs
- Gerenciamento de listas de categorias

## Observações Importantes

1. **Chave da API OpenAI**: Para utilizar a funcionalidade de sugestão de categorias por IA, você precisa configurar uma chave válida da API OpenAI no arquivo `.env`.

2. **Banco de Dados**: O aplicativo espera um banco de dados PostgreSQL com um schema chamado 'gepes'. Os scripts de configuração criam este esquema automaticamente.

3. **Usuários**: Use o script `create_admin_user.py` ou a opção correspondente no `setup_database.py` para criar o primeiro usuário administrador.
