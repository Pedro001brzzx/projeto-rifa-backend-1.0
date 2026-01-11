# Guia de Instalação e Configuração

## 🚀 Início Rápido (Desenvolvimento Local)

### 1. Clonar o Repositório

```bash
cd c:\Projetos\Projeto-rifa
```

### 2. Criar Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual (Windows PowerShell)
venv\Scripts\Activate.ps1

# Ativar ambiente virtual (Windows CMD)
venv\Scripts\activate.bat

# Ativar ambiente virtual (Linux/Mac)
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install flask flask-sqlalchemy flask-bcrypt flask-jwt-extended flask-cors
```

### 4. Executar a Aplicação

```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

> ✅ **Por padrão, a aplicação usa SQLite** que não requer instalação de banco de dados!

---

## 📊 Banco de Dados

### Opção 1: SQLite (Recomendado para Desenvolvimento)

**Vantagens:**
- ✅ Sem instalação necessária
- ✅ Arquivo único (`gemeos_brasil.db`)
- ✅ Perfeito para desenvolvimento e testes

**Configuração:**

Já está configurado por padrão! Basta executar `python app.py`.

O arquivo `gemeos_brasil.db` será criado automaticamente na raiz do projeto.

---

### Opção 2: PostgreSQL (Recomendado para Produção)

**Instalação do PostgreSQL:**

#### Windows

1. Baixar PostgreSQL: https://www.postgresql.org/download/windows/
2. Executar o instalador
3. Anotar a senha que escolher para o usuário `postgres`
4. Manter a porta padrão: `5432`

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### Mac

```bash
brew install postgresql
brew services start postgresql
```

**Criar Banco de Dados:**

```bash
# Conectar ao PostgreSQL
psql -U postgres

# Criar banco de dados
CREATE DATABASE gemeos_brasil;

# Criar usuário (opcional)
CREATE USER gemeos_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE gemeos_brasil TO gemeos_user;

# Sair
\q
```

**Configurar String de Conexão:**

Crie um arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/gemeos_brasil
FLASK_ENV=development
```

Ou no Windows PowerShell:

```powershell
$env:DATABASE_URL = "postgresql://postgres:sua_senha@localhost:5432/gemeos_brasil"
```

**Instalar psycopg2:**

```bash
pip install psycopg2-binary
```

---

## 🔧 Configuração Avançada

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```env
# Ambiente
FLASK_ENV=development

# Banco de Dados
DATABASE_URL=sqlite:///gemeos_brasil.db

# Chaves (gere chaves únicas para produção!)
SECRET_KEY=sua-chave-secreta-muito-segura
JWT_SECRET_KEY=sua-chave-jwt-muito-segura
```

### Carregar .env Automaticamente

```bash
pip install python-dotenv
```

Adicione ao início do `app.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 🧪 Testando a Instalação

### 1. Verificar se o Servidor Está Rodando

```bash
curl http://localhost:5000/
```

Resposta esperada:

```json
{
  "mensagem": "API Gêmeos Brasil",
  "versao": "1.0",
  "endpoints": {
    "auth": "/api/auth",
    "campanhas": "/api/campanhas",
    ...
  }
}
```

### 2. Testar Registro de Usuário

```bash
curl -X POST http://localhost:5000/api/auth/registro \
  -H "Content-Type: application/json" \
  -d "{\"nome\":\"Teste\",\"telefone\":\"11999999999\",\"senha\":\"senha123\"}"
```

### 3. Testar Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"telefone\":\"11999999999\",\"senha\":\"senha123\"}"
```

---

## 🐛 Solução de Problemas

### Erro: "UnicodeDecodeError" com PostgreSQL

**Problema:** Caracteres especiais na string de conexão

**Solução 1:** Use SQLite para desenvolvimento:

```python
# app/config.py já está configurado para usar SQLite por padrão
```

**Solução 2:** Configure PostgreSQL corretamente:

```env
# Use encode da URL se tiver caracteres especiais
DATABASE_URL=postgresql://usuario:senha@localhost:5432/gemeos_brasil
```

### Erro: "ModuleNotFoundError: No module named 'psycopg2'"

**Solução:**

```bash
pip install psycopg2-binary
```

### Erro: "Unable to connect to database"

**Verificar:**

1. PostgreSQL está rodando?
   ```bash
   # Windows
   Get-Service -Name postgresql*
   
   # Linux
   sudo systemctl status postgresql
   ```

2. Credenciais corretas no DATABASE_URL?

3. Banco de dados existe?
   ```bash
   psql -U postgres -c "\l"
   ```

### Erro: "Port 5000 already in use"

**Solução:** Altere a porta no `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Use outra porta
```

---

## 📦 Dependências Completas

### Instalação via requirements.txt

Crie `requirements.txt`:

```
flask==3.0.0
flask-sqlalchemy==3.1.1
flask-bcrypt==1.0.1
flask-jwt-extended==4.6.0
flask-cors==4.0.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9  # Apenas se usar PostgreSQL
```

Instalar:

```bash
pip install -r requirements.txt
```

---

## 🔒 Segurança para Produção

### Gerar Chaves Secretas

```python
import secrets
print(secrets.token_hex(32))  # Para SECRET_KEY
print(secrets.token_hex(32))  # Para JWT_SECRET_KEY
```

### Configurar .gitignore

```
# .gitignore
venv/
*.db
.env
__pycache__/
*.pyc
```

### Usar HTTPS em Produção

```python
# Adicione ao app/__init__.py
if not app.debug:
    from flask_talisman import Talisman
    Talisman(app)
```

---

## 🚀 Deploy em Produção

### Opção 1: Heroku

```bash
# Criar Procfile
echo "web: gunicorn app:app" > Procfile

# Instalar gunicorn
pip install gunicorn

# Deploy
heroku create
git push heroku main
heroku addons:create heroku-postgresql
```

### Opção 2: VPS (Linux)

```bash
# Instalar nginx e supervisor
sudo apt install nginx supervisor

# Configurar gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique a documentação: [README.md](file:///c:/Projetos/Projeto-rifa/README.md)
2. Revise os logs de erro
3. Verifique a configuração do banco de dados

---

**Última atualização:** 2026-01-03  
**Versão:** 1.0
