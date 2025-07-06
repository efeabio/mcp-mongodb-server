# 🚀 FastMCP MongoDB Server

Um servidor FastMCP (Fast Model Context Protocol) completo que disponibiliza informações de um servidor MongoDB através do Model Context Protocol.

## 📋 Características

- **6 Tools FastMCP** implementadas e testadas
- **Connection pooling** otimizado para MongoDB
- **Logging estruturado** com structlog
- **Validação robusta** com Pydantic
- **Tratamento de erros** customizado
- **Testes unitários** com mocks
- **Documentação completa** em português

## 🛠️ Tools Disponíveis

### 1. `list_databases()`
Lista todos os databases disponíveis no MongoDB.

**Retorna:**
```json
{
  "databases": [
    {
      "name": "meu_database",
      "size_on_disk": 1048576,
      "collections": 5,
      "objects": 1000
    }
  ],
  "total_count": 1,
  "status": "success"
}
```

### 2. `get_database_info(database_name: str)`
Retorna informações detalhadas de um database MongoDB.

**Parâmetros:**
- `database_name`: Nome do database

**Retorna:**
```json
{
  "database": {
    "name": "meu_database",
    "size_on_disk": 1048576,
    "collections": 5,
    "objects": 1000,
    "avg_obj_size": 1024,
    "data_size": 1048576,
    "storage_size": 2097152,
    "indexes": 3,
    "index_size": 524288
  },
  "status": "success"
}
```

### 3. `list_collections(database_name: str)`
Lista todas as collections de um database MongoDB.

**Parâmetros:**
- `database_name`: Nome do database

**Retorna:**
```json
{
  "database_name": "meu_database",
  "collections": [
    {
      "name": "usuarios",
      "count": 500,
      "size": 524288,
      "storage_size": 1048576,
      "total_index_size": 262144
    }
  ],
  "total_count": 1,
  "status": "success"
}
```

### 4. `get_collection_info(database_name: str, collection_name: str)`
Retorna informações detalhadas de uma collection MongoDB.

**Parâmetros:**
- `database_name`: Nome do database
- `collection_name`: Nome da collection

**Retorna:**
```json
{
  "collection": {
    "name": "usuarios",
    "count": 500,
    "size": 524288,
    "avg_obj_size": 1024,
    "storage_size": 1048576,
    "total_index_size": 262144,
    "indexes": [
      {
        "name": "_id_",
        "key": [["_id", 1]]
      }
    ]
  },
  "database_name": "meu_database",
  "status": "success"
}
```

### 5. `get_server_status()`
Retorna status geral do servidor MongoDB.

**Retorna:**
```json
{
  "server_status": {
    "version": "7.0.0",
    "uptime": 86400,
    "connections": {
      "current": 10,
      "available": 90
    },
    "memory": {
      "resident": 1073741824,
      "virtual": 2147483648
    },
    "operations": {
      "insert": 1000,
      "query": 5000,
      "update": 500,
      "delete": 100
    },
    "network": {
      "bytesIn": 1048576,
      "bytesOut": 2097152,
      "numRequests": 10000
    }
  },
  "status": "success"
}
```

### 6. `get_system_stats()`
Retorna estatísticas do sistema.

**Retorna:**
```json
{
  "system_stats": {
    "databases_count": 5,
    "total_collections": 25,
    "total_objects": 10000,
    "total_size_bytes": 52428800,
    "total_size_mb": 50.0,
    "admin_stats": {
      "collections": 0,
      "objects": 0,
      "dataSize": 0
    }
  },
  "status": "success"
}
```

## 🏗️ Estrutura do Projeto

```
fastmcp-mongodb-server/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Ponto de entrada da aplicação
│   ├── server.py               # Servidor FastMCP principal
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configurações com Pydantic
│   ├── core/
│   │   ├── __init__.py
│   │   └── exceptions.py       # Exceções customizadas
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Modelos Pydantic
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database_service.py # Informações de databases
│   │   ├── collection_service.py # Informações de collections
│   │   └── stats_service.py    # Estatísticas do servidor
│   └── utils/
│       ├── __init__.py
│       ├── mongo_connector.py  # Conector MongoDB
│       └── logger.py           # Configuração de logging
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── unit/
│       ├── __init__.py
│       ├── test_server.py
│       └── test_services.py
├── .env.example
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── README.md
```

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone <repository-url>
cd fastmcp-mongodb-server
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 5. Execute o servidor
```bash
python -m src.main
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_USERNAME=
MONGODB_PASSWORD=
MONGODB_AUTH_SOURCE=admin

# FastMCP Server Configuration
FASTMCP_SERVER_NAME=mongodb-info-server
FASTMCP_SERVER_VERSION=1.0.0
FASTMCP_SERVER_DESCRIPTION=FastMCP Server for MongoDB information and statistics

# Logging
LOG_LEVEL=INFO

# Performance
CONNECTION_TIMEOUT=5000
QUERY_TIMEOUT=30000
MAX_CONNECTIONS=10
```

## 🧪 Testes

### Instalar dependências de desenvolvimento
```bash
pip install -r requirements-dev.txt
```

### Executar testes
```bash
pytest
```

### Executar testes com cobertura
```bash
pytest --cov=src --cov-report=html
```

### Executar linting
```bash
black src/
flake8 src/
mypy src/
isort src/
```

## 📊 Logging

O projeto usa logging estruturado com structlog. Os logs são formatados em JSON e incluem:

- Timestamp ISO
- Nível de log
- Nome do logger
- Contexto estruturado
- Mensagem

Exemplo de log:
```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "info",
  "logger": "src.server",
  "event": "Executando tool: list_databases",
  "status": "success"
}
```

## 🔒 Segurança

- **Validação de entrada**: Todos os parâmetros são validados com Pydantic
- **Sanitização**: Nomes de databases e collections são sanitizados
- **Limites**: Limites configuráveis para evitar sobrecarga
- **Timeouts**: Timeouts configuráveis para operações

## 🚨 Tratamento de Erros

O projeto implementa tratamento de erros robusto com exceções customizadas:

- `MongoDBConnectionError`: Erro de conexão com MongoDB
- `DatabaseNotFoundError`: Database não encontrado
- `CollectionNotFoundError`: Collection não encontrada
- `InvalidQueryError`: Query inválida
- `AuthenticationError`: Erro de autenticação
- `TimeoutError`: Erro de timeout
- `ConfigurationError`: Erro de configuração

## ⚡ Performance

- **Connection pooling**: Pool de conexões configurável
- **Operações assíncronas**: Todas as operações são assíncronas
- **ThreadPoolExecutor**: Execução de operações MongoDB em threads separadas
- **Caching**: Cache de configurações e loggers
- **Timeouts**: Timeouts configuráveis para evitar travamentos

## 📝 Documentação

Todas as funções são documentadas com docstrings no estilo Google, incluindo:

- Descrição da função
- Parâmetros (Args)
- Valor de retorno (Returns)
- Exceções (Raises)
- Exemplos de uso

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

Se você encontrar algum problema ou tiver dúvidas, por favor abra uma issue no repositório.

## 🔄 Changelog

### v1.0.0
- Implementação inicial do servidor FastMCP
- 6 tools FastMCP implementadas
- Sistema de logging estruturado
- Tratamento de erros robusto
- Testes unitários com mocks
- Documentação completa 