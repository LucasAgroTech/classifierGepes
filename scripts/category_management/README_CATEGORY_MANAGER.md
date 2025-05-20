# Gerenciamento de Categorias - GEPES Classifier

Este módulo implementa funcionalidades avançadas para o gerenciamento hierárquico completo de categorias no sistema GEPES Classifier, incluindo a adição, edição e exclusão de macroáreas, segmentos, domínios, classes e subclasses de tecnologias verdes.

## Estrutura de Dados e Hierarquia

O sistema mantém a seguinte estrutura hierárquica no modelo `CategoriaLista`:

- **Macroárea**: armazenada como `tipo='macroárea'`, `valor='Nome da Macroárea'`
- **Segmento**: armazenada como `tipo='segmento'`, `valor='Macroárea|Segmento'`
- **Domínio**: armazenada como `tipo='dominio'`, `valor='Macroárea|Segmento|Domínio'`
- **Tecnologia Verde - Classe**: armazenada como `tipo='tecverde_classe'`, `valor='Nome da Classe'`
- **Tecnologia Verde - Subclasse**: armazenada como `tipo='tecverde_subclasse'`, `valor='Classe|Subclasse'`

## Funcionalidades Implementadas

### 1. Visualização Hierárquica

A interface de usuário apresenta as categorias em uma estrutura hierárquica intuitiva:

- Macroáreas são exibidas como itens de acordeão
- Segmentos são exibidos como cards dentro de cada macroárea
- Domínios são exibidos como "bolhas" dentro de cada segmento
- Classes de tecnologia verde são exibidas como itens de acordeão em uma aba separada
- Subclasses são exibidas como "bolhas" dentro de cada classe

### 2. Adição de Categorias

- Adição de novas macroáreas
- Adição de segmentos vinculados a uma macroárea específica
- Adição de domínios vinculados a um segmento específico
- Adição de classes de tecnologia verde
- Adição de subclasses vinculadas a uma classe específica

### 3. Edição de Categorias

- Edição de macroáreas com atualização em cascata de todos os segmentos e domínios relacionados
- Edição de segmentos com atualização em cascata de todos os domínios relacionados
- Edição de domínios
- Edição de classes de tecnologia verde com atualização em cascata de todas as subclasses relacionadas
- Edição de subclasses

### 4. Exclusão de Categorias

- Exclusão (desativação) de macroáreas com desativação em cascata de todos os segmentos e domínios relacionados
- Exclusão (desativação) de segmentos com desativação em cascata de todos os domínios relacionados
- Exclusão (desativação) de domínios
- Exclusão (desativação) de classes de tecnologia verde com desativação em cascata de todas as subclasses relacionadas
- Exclusão (desativação) de subclasses

## Arquitetura

### Rotas

- `GET /categories/manage`: Exibe a página de gerenciamento hierárquico de categorias
- `POST /categories/add`: Adiciona uma nova categoria respeitando a hierarquia
- `PUT /categories/edit/<int:id>`: Edita uma categoria existente
- `DELETE /categories/delete/<int:id>`: Exclui (desativa) uma categoria e suas dependências

### Funções Auxiliares

- `construir_hierarquia()`: Constrói a estrutura hierárquica para exibição na UI
- `construir_hierarquia_tecverde()`: Constrói a estrutura hierárquica para Tecnologias Verdes
- `atualizar_hierarquia_macroárea()`: Atualiza o valor da macroárea em todos os segmentos e domínios relacionados
- `atualizar_hierarquia_segmento()`: Atualiza o valor do segmento em todos os domínios relacionados
- `atualizar_hierarquia_tecverde_classe()`: Atualiza o valor da classe em todas as subclasses relacionadas
- `desativar_hierarquia_macroárea()`: Desativa todos os segmentos e domínios relacionados a uma macroárea
- `desativar_hierarquia_segmento()`: Desativa todos os domínios relacionados a um segmento
- `desativar_hierarquia_tecverde_classe()`: Desativa todas as subclasses relacionadas a uma classe

## Interface de Usuário

A interface de usuário foi projetada para ser intuitiva e fácil de usar:

- Abas para separar categorias de projetos e tecnologias verdes
- Acordeões para organizar macroáreas e classes
- Cards para exibir segmentos
- Bolhas para exibir domínios e subclasses
- Modais para adicionar e editar categorias
- Confirmação para exclusão de categorias

## Considerações de Implementação

- **Estrutura Hierárquica**: O sistema mantém a estrutura hierárquica usando o formato de valores concatenados com pipe (`|`) no banco de dados (ex: "Macroarea|Segmento|Dominio"), enquanto fornece uma interface visual intuitiva.
- **Transações e Integridade Referencial**: Todas as operações críticas estão dentro de blocos try-except com rollback em caso de erro para manter a integridade do banco de dados.
- **Cascata de Operações**: A exclusão de itens de nível superior (ex: macroárea) desativa automaticamente todos os itens filhos (segmentos e domínios relacionados).
- **Prevenção de Duplicatas**: O sistema verifica a existência prévia de categorias para evitar duplicações.
- **UX Aprimorada**: Interface com abas para separar categorias normais e tecnologias verdes, modais para adição/edição, confirmações para exclusão com avisos sobre efeitos em cascata.

## Testes

O arquivo `test_all_category_functions.py` contém testes unitários para verificar o funcionamento correto das funcionalidades de gerenciamento de categorias:

- Teste da estrutura hierárquica
- Teste da adição de categorias
- Teste da edição de categorias com atualização em cascata
- Teste da exclusão de categorias com desativação em cascata

## Estratégias de Depuração e Solução de Problemas

- Logs detalhados usando `logger.info()` e `logger.error()` para rastrear o fluxo de execução
- Verificações de consistência no banco de dados para identificar categorias que não seguem o formato hierárquico correto
- Tratamento de exceções com mensagens claras para facilitar a identificação de problemas
