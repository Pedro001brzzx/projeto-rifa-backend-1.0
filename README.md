# Projeto Rifa - Sistema de Campanhas/Sorteios

Backend Flask refatorado usando padrão **MVC** (Model-View-Controller) para o sistema de campanhas e sorteios Gêmeos Brasil.

## 📁 Estrutura do Projeto

```
Projeto-rifa/
├── app/
│   ├── __init__.py              # Factory da aplicação Flask
│   ├── config.py                # Configurações centralizadas
│   │
│   ├── models/                  # Camada Model (Banco de Dados)
│   │   ├── __init__.py          # Inicialização do SQLAlchemy
│   │   ├── usuario.py           # Modelo de Usuário
│   │   ├── campanha.py          # Modelo de Campanha
│   │   ├── compra.py            # Modelo de Compra
│   │   ├── titulo.py            # Modelo de Título
│   │   ├── artigo.py            # Modelo de Artigo
│   │   ├── comunicado.py        # Modelo de Comunicado
│   │   └── contato.py           # Modelo de Contato
│   │
│   ├── controllers/             # Camada Controller (Lógica de Negócio)
│   │   ├── __init__.py
│   │   ├── auth_controller.py       # Lógica de autenticação
│   │   ├── campanha_controller.py   # Lógica de campanhas
│   │   ├── compra_controller.py     # Lógica de compras
│   │   ├── ganhador_controller.py   # Lógica de ganhadores
│   │   └── conteudo_controller.py   # Lógica de conteúdo
│   │
│   └── routes/                  # Camada View (Rotas/Endpoints)
│       ├── __init__.py
│       ├── auth_routes.py           # Rotas de autenticação
│       ├── campanha_routes.py       # Rotas de campanhas
│       ├── compra_routes.py         # Rotas de compras
│       ├── ganhador_routes.py       # Rotas de ganhadores
│       └── conteudo_routes.py       # Rotas de conteúdo
│
├── app.py                       # Ponto de entrada da aplicação
├── init.py                      # Arquivo antigo (backup)
└── README.md                    # Este arquivo
```

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
pip install flask flask-sqlalchemy flask-bcrypt flask-jwt-extended flask-cors
```

### 2. Configurar Variáveis de Ambiente (Opcional)

```bash
# Windows PowerShell
$env:DATABASE_URL = "postgresql://usuario:senha@localhost/gemeos_brasil"
$env:SECRET_KEY = "sua-chave-secreta"
$env:JWT_SECRET_KEY = "sua-chave-jwt"
$env:FLASK_ENV = "development"
```

### 3. Executar a Aplicação

```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

## 📋 Endpoints da API

### Autenticação (`/api/auth`)
- `POST /api/auth/registro` - Registrar novo usuário
- `POST /api/auth/login` - Login de usuário
- `POST /api/auth/recuperar-senha` - Recuperação de senha
- `GET /api/auth/perfil` - Obter perfil (autenticado)
- `PUT /api/auth/perfil` - Atualizar perfil (autenticado)

### Campanhas (`/api/campanhas`)
- `GET /api/campanhas` - Listar campanhas
- `GET /api/campanhas/<slug>` - Detalhes de campanha
- `POST /api/campanhas` - Criar campanha (admin)

### Compras (`/api/compras`)
- `POST /api/compras` - Criar compra (autenticado)
- `GET /api/meus-titulos` - Listar títulos (autenticado)

### Ganhadores (`/api/ganhadores`)
- `GET /api/ganhadores` - Listar ganhadores

### Conteúdo
- `GET /api/artigos` - Listar artigos
- `GET /api/artigos/<slug>` - Detalhes de artigo
- `GET /api/comunicados` - Listar comunicados
- `POST /api/contato` - Enviar contato

## 🏗️ Arquitetura MVC

### **Model** (Modelos)
Responsável pela estrutura de dados e interação com o banco de dados PostgreSQL. Cada modelo representa uma tabela e contém métodos de serialização (`to_dict()`).

### **View** (Rotas/Blueprints)
Define os endpoints da API usando Flask Blueprints. Recebe requisições HTTP, valida dados básicos e encaminha para os controllers.

### **Controller** (Controladores)
Contém a lógica de negócio da aplicação. Processa dados, interage com os modelos, aplica regras de negócio e retorna respostas formatadas.

## 🔧 Tecnologias Utilizadas

- **Flask** - Framework web
- **SQLAlchemy** - ORM para banco de dados
- **PostgreSQL** - Banco de dados
- **Flask-JWT-Extended** - Autenticação JWT
- **Flask-Bcrypt** - Criptografia de senhas
- **Flask-CORS** - Suporte a CORS

## 📝 Benefícios da Refatoração

✅ **Separação de responsabilidades** - Código mais organizado e manutenível  
✅ **Facilita testes** - Controllers e models podem ser testados independentemente  
✅ **Escalabilidade** - Fácil adicionar novos recursos  
✅ **Reutilização** - Lógica de negócio separada das rotas  
✅ **Leitura** - Arquivos menores e mais focados  

## 📌 Próximos Passos

- [ ] Implementar testes unitários
- [ ] Adicionar validação de dados (marshmallow/pydantic)
- [ ] Implementar logging
- [ ] Adicionar documentação Swagger/OpenAPI
- [ ] Configurar migrations com Alembic
