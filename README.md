# FastMCP MongoDB Server

Servidor FastMCP para MongoDB que permite que agentes de IA interajam com bancos MongoDB de forma dinâmica e segura.

## Características

- **Conexão Dinâmica**: Não requer configuração prévia de variáveis de ambiente
- **Verificação de Conexão**: Todas as tools verificam se há conexão ativa antes de executar
- **Interface Intuitiva**: A IA pode configurar a conexão conforme necessário
- **Operações Completas**: Suporte a CRUD, índices, agregações e estatísticas
- **Tratamento de Erros**: Mensagens claras e sugestões de ação
- **Sistema de Decorators**: Registro automático de tools com injeção de dependências
- **Validação Robusta**: Uso de Pydantic para validação de dados
- **Logging Estruturado**: Sistema de logging avançado com structlog
- **Testes Completos**: Suíte de testes com mocks e cobertura de 58%
- **Scripts de Desenvolvimento**: Automação completa do ambiente de desenvolvimento

## Como Funciona

### 1. Configuração da Conexão

A IA deve primeiro configurar a conexão com MongoDB usando a tool `mongodb_configure_connection`:

```python
# Exemplo de uso pela IA
result = await mongodb_configure_connection(
    host="localhost",
    port=27017,
    username="usuario",
    password="senha",
    auth_source="admin"
)
```

### 2. Verificação Automática

Todas as outras tools verificam automaticamente se há uma conexão ativa. Se não houver, retornam uma mensagem clara indicando que é necessário configurar a conexão primeiro.

### 3. Operações Disponíveis

Após configurar a conexão, a IA pode usar todas as tools disponíveis:

- **Databases**: listar, criar, remover, obter informações
- **Collections**: listar, criar, remover, renomear, validar
- **Documentos**: inserir, buscar, atualizar, remover, listar
- **Índices**: criar, listar, remover
- **Estatísticas**: status do servidor, estatísticas do sistema

## Tools Disponíveis

### Tools de Conexão
- `mongodb_configure_connection`: Configura conexão com MongoDB
- `mongodb_test_connection`: Testa a conexão atual
- `mongodb_get_connection_status`: Obtém status da conexão
- `mongodb_disconnect`: Desconecta do MongoDB

### Tools de Databases
- `mongodb_list_databases`: Lista todos os databases
- `mongodb_create_database`: Cria um novo database
- `mongodb_drop_database`: Remove um database
- `mongodb_get_database_info`: Obtém informações de um database

### Tools de Collections
- `mongodb_list_collections`: Lista collections de um database
- `mongodb_create_collection`: Cria uma nova collection
- `mongodb_drop_collection`: Remove uma collection
- `mongodb_get_collection_info`: Obtém informações de uma collection
- `mongodb_validate_collection`: Valida integridade de uma collection
- `mongodb_count_documents`: Conta documentos em uma collection
- `mongodb_aggregate`: Executa pipeline de agregação

### Tools de Documentos
- `mongodb_list_documents`: Lista documentos de uma collection
- `mongodb_get_document`: Busca um documento específico
- `mongodb_insert_document`: Insere um novo documento
- `mongodb_update_document`: Atualiza um documento existente
- `mongodb_delete_document`: Remove um documento

### Tools de Índices
- `mongodb_list_indexes`: Lista índices de uma collection
- `mongodb_create_index`: Cria um novo índice
- `mongodb_drop_index`: Remove um índice

### Tools de Estatísticas
- `mongodb_get_server_status`: Obtém status do servidor MongoDB
- `mongodb_get_system_stats`: Obtém estatísticas do sistema

## Requisitos

- **Python**: 3.8 ou superior
- **MongoDB**: 4.0 ou superior (para uso das tools)
- **Sistema**: Linux, macOS ou Windows
- **Memória**: Mínimo 512MB RAM
- **Espaço**: Mínimo 100MB em disco

## Instalação

### Instalação Local

1. Clone o repositório
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Execute o servidor:
   ```bash
   python -m src.main
   ```

### Configuração no Cursor

Para usar o servidor MCP no Cursor, adicione a seguinte configuração ao seu arquivo de configuração:

```json
{
  "mcpServers": {
    "mongodb": {
      "command": "/caminho/para/seu/projeto/mongodb/start-mcp.sh"
    }
  }
}
```

**Exemplo para o projeto atual:**
```json
{
  "mcpServers": {
    "mongodb": {
      "command": "/home/fabio/Documentos/work/codes/ai/mcp/mongodb/start-mcp.sh"
    }
  }
}
```

**Nota:** Certifique-se de que o script `start-mcp.sh` tem permissões de execução:
```bash
chmod +x start-mcp.sh
```

### Instalação com Scripts de Desenvolvimento (Recomendado)

1. Clone o repositório
2. Execute o script de configuração:
   ```bash
   ./scripts/dev.sh up
   ```
3. O script criará automaticamente:
   - Ambiente virtual Python
   - Instalação de todas as dependências
4. Para executar o servidor:
   ```bash
   ./scripts/dev.sh run
   ```

### Scripts de Desenvolvimento

O projeto inclui scripts úteis para desenvolvimento:

```bash
# Usar o helper de desenvolvimento
./scripts/dev.sh up          # Configurar ambiente de desenvolvimento
./scripts/dev.sh test        # Executar testes
./scripts/dev.sh lint        # Verificar qualidade do código
./scripts/dev.sh format      # Formatar código automaticamente
./scripts/dev.sh run         # Executar servidor
./scripts/dev.sh debug       # Executar servidor em modo debug
./scripts/dev.sh clean       # Limpar ambiente completamente

# Usar comandos Make (alternativa)
make help                    # Mostrar todos os comandos disponíveis
make install-dev             # Instalar dependências de desenvolvimento
make test                    # Executar testes com cobertura
make lint                    # Verificar qualidade do código
make format                  # Formatar código automaticamente
make run                     # Executar servidor
make clean                   # Limpar arquivos temporários
```

## Uso pela IA

### Fluxo Típico

1. **Configurar Conexão**: A IA deve sempre começar configurando a conexão
2. **Verificar Status**: Testar se a conexão está funcionando
3. **Executar Operações**: Usar as tools conforme necessário
4. **Gerenciar Recursos**: Desconectar quando terminar

### Exemplo de Sessão

```python
# 1. Configurar conexão
connection_result = await mongodb_configure_connection(
    host="mongodb.example.com",
    port=27017,
    username="admin",
    password="secret123"
)

# 2. Verificar status
status = await mongodb_get_connection_status()

# 3. Listar databases
databases = await mongodb_list_databases()

# 4. Trabalhar com collections
collections = await mongodb_list_collections("meu_database")

# 5. Desconectar ao final
await mongodb_disconnect()
```

## Segurança

- **Sem Hardcoding**: Nenhuma credencial é armazenada em código
- **Conexão Dinâmica**: Cada sessão pode usar credenciais diferentes
- **Sanitização de Logs**: Credenciais são automaticamente mascaradas nos logs
- **Validação**: Todas as operações são validadas antes da execução
- **Isolamento**: Conexões são isoladas por sessão
- **Validação de Entrada**: Uso de Pydantic para validação robusta
- **Logging Seguro**: Sistema de logging que protege informações sensíveis

## Tratamento de Erros

O sistema fornece mensagens claras e sugestões de ação:

- **Sem Conexão**: Indica que é necessário configurar a conexão primeiro
- **Erros de Autenticação**: Sugere verificar credenciais
- **Operações Falhadas**: Explica o que deu errado e como corrigir

## Desenvolvimento

### Estrutura do Projeto

```
src/
├── tools/           # Tools MCP com sistema de decorators
│   ├── tools_connection.py    # Gerenciamento de conexões
│   ├── tools_databases.py     # Operações com databases
│   ├── tools_collections.py   # Operações com collections
│   ├── tools_documents.py     # Operações com documentos
│   ├── tools_indexes.py       # Operações com índices
│   ├── tools_stats.py         # Estatísticas do servidor
│   ├── decorators.py          # Sistema de decorators
│   └── dependencies.py        # Container de dependências
├── utils/           # Utilitários (conector, logger, segurança)
├── config/          # Configurações com Pydantic
├── core/            # Exceções e lógica central
├── models/          # Schemas Pydantic para validação
├── services/        # Camada de serviços
└── server.py        # Servidor principal
```

### Adicionando Novas Tools

1. Crie o arquivo em `src/tools/`
2. Use o decorator `@mongodb_tool` para registro automático
3. Implemente a função com tratamento de erros adequado
4. Use `DependencyContainer` para acessar dependências
5. A tool será registrada automaticamente no servidor

### Sistema de Decorators

O projeto usa um sistema avançado de decorators para:
- **Registro automático** de tools
- **Verificação de conexão** automática
- **Injeção de dependências** centralizada
- **Tratamento de erros** consistente

### Qualidade de Código

```bash
# Verificar qualidade
make lint

# Formatar código
make format

# Executar testes
make test

# Verificar cobertura
make coverage
```

### Testes

O projeto inclui uma suíte completa de testes:

```bash
# Executar todos os testes
make test

# Executar testes específicos
make test-unit          # Apenas testes unitários
make test-fast          # Testes sem cobertura

# Executar testes com script
./scripts/dev.sh test
```

**Cobertura de Testes:**
- **103 testes** executando com sucesso
- Testes unitários com mocks
- Fixtures para dados de teste
- Cobertura de código de 58%
- Relatórios HTML e XML

## Dependências

### Produção
- `mcp>=1.10.1`: Framework MCP base
- `fastmcp`: Biblioteca para criação de servidores MCP
- `pymongo>=4.5.0`: Driver MongoDB para Python
- `pydantic>=2.0.0`: Validação de dados
- `structlog>=23.0.0`: Logging estruturado

### Desenvolvimento
- `pytest>=7.0.0`: Framework de testes
- `pytest-asyncio>=0.21.0`: Suporte a testes assíncronos
- `pytest-cov>=4.0.0`: Cobertura de testes
- `black>=23.0.0`: Formatação de código
- `flake8>=6.0.0`: Linting
- `mypy>=1.0.0`: Verificação de tipos
- `isort>=5.12.0`: Ordenação de imports

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. **Fork o repositório**
2. **Crie uma branch** para sua feature
3. **Faça suas alterações** seguindo as diretrizes de código
4. **Execute os testes** e verificações de qualidade
5. **Crie um Pull Request**

### Diretrizes de Contribuição

- Use docstrings em português brasileiro
- Siga o padrão de código (Black, isort, flake8)
- Adicione testes para novas funcionalidades
- Atualize a documentação quando necessário

### Comandos Úteis para Contribuição

```bash
# Configurar ambiente
./scripts/dev.sh up

# Verificar qualidade
make lint

# Executar testes
make test

# Formatar código
make format
```

## Licença

MIT License

## Suporte

- **Issues**: Para bugs e features
- **Documentação**: Este README e código fonte
- **Testes**: Execute `make test` para verificar funcionamento
