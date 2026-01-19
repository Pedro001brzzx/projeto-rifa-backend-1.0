# Guia de Manutenção - Sistema de Rifas Gêmeos Brasil

**Versão:** 1.2  
**Última Atualização:** 2026-01-19

---

## 📋 Índice

- [Scripts de Administração](#scripts-de-administração)
- [Gerenciamento de Usuários](#gerenciamento-de-usuários)
- [Gerenciamento de Campanhas](#gerenciamento-de-campanhas)
- [Gerenciamento de Pagamentos](#gerenciamento-de-pagamentos)
- [Banco de Dados](#banco-de-dados)
- [Troubleshooting](#troubleshooting)
- [Backup e Recuperação](#backup-e-recuperação)
- [Monitoramento](#monitoramento)
- [Logs](#logs)

---

## 🛠️ Scripts de Administração

### Scripts Disponíveis

O sistema inclui vários scripts utilitários para manutenção e administração:

| Script | Descrição | Comando |
|--------|-----------|---------|
| `make_admin.py` | Torna um usuário administrador | `python make_admin.py` |
| `remove_admin.py` | Remove privilégios de admin | `python remove_admin.py` |
| `reset_senha.py` | Reseta senha de usuário | `python reset_senha.py` |
| `adicionar_campanhas.py` | Adiciona campanhas de exemplo | `python adicionar_campanhas.py` |
| `diagnostico.py` | Diagnóstico do sistema | `python diagnostico.py` |

### Uso dos Scripts

#### 1. Tornar Usuário Admin

```powershell
python make_admin.py
```

**Fluxo:**
1. Exibe lista de usuários
2. Solicita telefone do usuário
3. Concede privilégios de administrador
4. Confirma alteração

**Exemplo de Output:**
```
👑 CRIADOR DE ADMIN
==================================================
Digite o telefone do usuário: 5583994099696
✅ SUCESSO! Pedro Henrique agora é administrador!
```

#### 2. Remover Privilégios Admin

```powershell
python remove_admin.py
```

**Quando usar:**
- Revogar acesso administrativo temporário
- Auditorias de segurança
- Mudanças de equipe

#### 3. Resetar Senha (Desenvolvimento)

```powershell
python reset_senha.py
```

**Quando usar:**
- Ambiente de desenvolvimento/teste
- Usuário esqueceu a senha (temporariamente)
- Acesso de emergência ao sistema

> ⚠️ **Produção:** Em ambiente de produção, use o endpoint de recuperação de senha via SMS.

---

## 👥 Gerenciamento de Usuários

### Verificar Status de Admin

**Via API:**
```bash
curl -X GET http://localhost:5000/api/auth/perfil \
  -H "Authorization: Bearer {token}"
```

Verificar campo `is_admin` na resposta.

**Via Banco de Dados:**
```sql
SELECT id, nome, telefone, email, is_admin, criado_em 
FROM usuarios 
WHERE is_admin = 1;
```

### Listar Todos os Usuários

**Via API (Admin):**
```bash
curl -X GET "http://localhost:5000/api/admin/usuarios?page=1&per_page=50" \
  -H "Authorization: Bearer {admin_token}"
```

**Via Python:**
```python
from app import create_app
from app.models import Usuario

app = create_app()
with app.app_context():
    usuarios = Usuario.query.all()
    for u in usuarios:
        print(f"{u.id} | {u.nome} | {u.telefone} | Admin: {u.is_admin}")
```

### Desativar Usuário

```python
from app import create_app
from app.models import db, Usuario

app = create_app()
with app.app_context():
    usuario = Usuario.query.filter_by(telefone='11999999999').first()
    usuario.ativo = False
    db.session.commit()
    print(f"✅ Usuário {usuario.nome} desativado")
```

---

## 🎯 Gerenciamento de Campanhas

### Adicionar Campanhas de Teste

```powershell
python adicionar_campanhas.py
```

Cria 5 campanhas de exemplo com:
- Títulos variados
- Imagens do Unsplash
- Valores e datas pré-configurados

### Verificar Campanhas Ativas

**Via API:**
```bash
curl "http://localhost:5000/api/campanhas?status=ativo"
```

**Via SQL:**
```sql
SELECT id, titulo, status, data_sorteio, titulos_vendidos, total_titulos
FROM campanhas
WHERE status = 'ativo'
ORDER BY data_sorteio ASC;
```

### Alterar Status de Campanha

**Via API (Admin):**
```bash
curl -X PUT http://localhost:5000/api/campanhas/1 \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "concluido"}'
```

**Via Python:**
```python
from app import create_app
from app.models import db, Campanha

app = create_app()
with app.app_context():
    campanha = Campanha.query.get(1)
    campanha.status = 'concluido'
    db.session.commit()
```

### Deletar Campanha (Sem Compras)

```bash
curl -X DELETE http://localhost:5000/api/campanhas/5 \
  -H "Authorization: Bearer {admin_token}"
```

> ⚠️ **Importante:** Só é possível deletar campanhas sem compras associadas. Para campanhas com vendas, altere o status para `cancelado`.

---

## 💳 Gerenciamento de Pagamentos

> **Novo:** Sistema de checkout e processamento de pagamentos

### Aprovar Pagamento Manualmente

**Via Script Python:**
```python
from app import create_app
from app.models import db, Compra
from datetime import datetime

app = create_app()
with app.app_context():
    compra_id = 1
    compra = Compra.query.get(compra_id)
    
    if compra:
        compra.status_pagamento = 'aprovado'
        compra.data_pagamento = datetime.utcnow()
        compra.campanha.titulos_vendidos += compra.quantidade_titulos
        db.session.commit()
        print(f"✅ Pagamento #{compra_id} aprovado com sucesso!")
    else:
        print(f"❌ Compra #{compra_id} não encontrada")
```

**Via API (Admin):**
```bash
curl -X POST http://localhost:5000/api/pagamentos/1/aprovar \
  -H "Authorization: Bearer {admin_token}"
```

### Script de Aprovação em Lote

Crie um arquivo `aprovar_pagamentos_lote.py` para aprovar múltiplos pagamentos:

```python
from app import create_app
from app.models import db, Compra
from datetime import datetime

app = create_app()

def aprovar_pendentes():
    with app.app_context():
        pendentes = Compra.query.filter_by(status_pagamento='pendente').all()
        
        print(f"\n📋 Encontradas {len(pendentes)} compras pendentes\n")
        
        for compra in pendentes:
            print(f"Compra #{compra.id}:")
            print(f"  - Usuário: {compra.usuario.nome}")
            print(f"  - Campanha: {compra.campanha.titulo}")
            print(f"  - Títulos: {compra.quantidade_titulos}")
            print(f"  - Valor: R$ {compra.valor_total:.2f}")
            print(f"  - Método: {compra.metodo_pagamento}")
            
            resposta = input("  Aprovar? (s/n): ").lower()
            
            if resposta == 's':
                compra.status_pagamento = 'aprovado'
                compra.data_pagamento = datetime.utcnow()
                compra.campanha.titulos_vendidos += compra.quantidade_titulos
                db.session.commit()
                print("  ✅ Aprovado!\n")
            else:
                print("  ⏭️  Pulado\n")

if __name__ == '__main__':
    aprovar_pendentes()
```

**Uso:**
```powershell
python aprovar_pagamentos_lote.py
```

### Simular Webhook de Gateway

**Para testar o webhook localmente:**

```bash
# Simular pagamento aprovado
curl -X POST "http://localhost:5000/api/pagamentos/webhook?gateway=mercadopago" \
  -H "Content-Type: application/json" \
  -d '{"compra_id": 1, "status": "aprovado"}'

# Simular pagamento cancelado
curl -X POST "http://localhost:5000/api/pagamentos/webhook?gateway=pix" \
  -H "Content-Type: application/json" \
  -d '{"compra_id": 2, "status": "cancelado"}'
```

### Consultar Status de Pagamento

**Via API:**
```bash
curl -X GET http://localhost:5000/api/pagamentos/1 \
  -H "Authorization: Bearer {token}"
```

**Via SQL:**
```sql
SELECT 
    c.id,
    u.nome AS usuario,
    ca.titulo AS campanha,
    c.quantidade_titulos,
    c.valor_total,
    c.status_pagamento,
    c.metodo_pagamento,
    c.data_pagamento,
    c.criado_em
FROM compras c
INNER JOIN usuarios u ON c.usuario_id = u.id
INNER JOIN campanhas ca ON c.campanha_id = ca.id
WHERE c.status_pagamento = 'pendente'
ORDER BY c.criado_em DESC;
```

### Ver Estatísticas de Pagamento

```python
from app import create_app
from app.models import Compra
from sqlalchemy import func

app = create_app()
with app.app_context():
    stats = Compra.query.with_entities(
        Compra.status_pagamento,
        func.count(Compra.id).label('total'),
        func.sum(Compra.valor_total).label('valor')
    ).group_by(Compra.status_pagamento).all()
    
    print("\n📊 Estatísticas de Pagamento:\n")
    for status, total, valor in stats:
        print(f"{status.upper():12} | {total:4} compras | R$ {valor:10.2f}")
```

### Integração com Gateways (Produção)

> ⚠️ **Importante:** O sistema atual usa dados mockados. Para produção, integre com um gateway real.

**Gateways Recomendados:**

1. **Mercado Pago**
   - SDK: `mercadopago`
   - Documentação: https://www.mercadopago.com.br/developers
   - Suporta: PIX, Cartão, Boleto

2. **Asaas**
   - API REST
   - Documentação: https://docs.asaas.com
   - Ótimo para PIX e boleto

3. **PagSeguro**
   - SDK: `pagseguro-python`
   - Documentação: https://dev.pagseguro.uol.com.br

**Passos para Integração:**

1. Instalar SDK do gateway:
   ```bash
   pip install mercadopago
   ```

2. Configurar credenciais em `.env`:
   ```
   GATEWAY_API_KEY=seu_token_aqui
   GATEWAY_PUBLIC_KEY=sua_public_key_aqui
   ```

3. Modificar função `_gerar_dados_pagamento` em `pagamento_controller.py`:
   ```python
   import mercadopago
   
   def _gerar_dados_pagamento(compra, metodo_pagamento):
       if metodo_pagamento == 'pix':
           sdk = mercadopago.SDK(os.getenv('GATEWAY_API_KEY'))
           
           payment_data = {
               "transaction_amount": float(compra['valor_total']),
               "description": f"Compra #{compra['id']}",
               "payment_method_id": "pix",
               "payer": {
                   "email": "usuario@email.com"
               }
           }
           
           result = sdk.payment().create(payment_data)
           payment = result["response"]
           
           return {
               "tipo": "pix",
               "qr_code": payment["point_of_interaction"]["transaction_data"]["qr_code"],
               "qr_code_base64": payment["point_of_interaction"]["transaction_data"]["qr_code_base64"],
               # ... demais campos
           }
   ```

4. Validar webhook em `pagamento_routes.py`:
   ```python
   @pagamento_bp.route('/pagamentos/webhook', methods=['POST'])
   def processar_webhook():
       # Validar assinatura do Mercado Pago
       x_signature = request.headers.get('x-signature')
       x_request_id = request.headers.get('x-request-id')
       
       # Validar conforme documentação do gateway
       if not validar_assinatura(x_signature, request.data):
           return jsonify({'erro': 'Assinatura inválida'}), 401
       
       # ... resto do código
   ```

---

## 💾 Banco de Dados

### Localização

```
c:\Projetos\Projeto-rifa\instance\sistema.db
```

### Backup Manual

**Windows (PowerShell):**
```powershell
# Criar backup com timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "instance\sistema.db" "backups\sistema_$timestamp.db"
```

**SQL Dump (via sqlite3):**
```bash
sqlite3 instance/sistema.db .dump > backup.sql
```

### Restaurar Backup

```powershell
# Parar servidor primeiro
Copy-Item "backups\sistema_20260111_120000.db" "instance\sistema.db"
# Reiniciar servidor
```

### Verificar Integridade

```bash
sqlite3 instance/sistema.db "PRAGMA integrity_check;"
```

### Estatísticas do Banco

```python
from app import create_app
from app.models import db, Usuario, Campanha, Compra, Titulo

app = create_app()
with app.app_context():
    print(f"Total Usuários: {Usuario.query.count()}")
    print(f"Total Campanhas: {Campanha.query.count()}")
    print(f"Total Compras: {Compra.query.count()}")
    print(f"Total Títulos: {Titulo.query.count()}")
```

### Limpar Dados de Teste

> ⚠️ **CUIDADO:** Esta operação é irreversível!

```python
from app import create_app
from app.models import db, Titulo, Compra, Campanha

app = create_app()
with app.app_context():
    # Deletar apenas compras pendentes
    compras_pendentes = Compra.query.filter_by(status_pagamento='pendente').all()
    for c in compras_pendentes:
        Titulo.query.filter_by(compra_id=c.id).delete()
        db.session.delete(c)
    db.session.commit()
    print(f"✅ {len(compras_pendentes)} compras pendentes removidas")
```

---

## 🔧 Troubleshooting

### Erro: "SQLAlchemy LegacyAPIWarning"

**Problema:** Aviso sobre uso de API legado.

**Solução:** Já corrigido nos scripts. Se aparecer em código personalizado, substitua:
```python
# Antigo
Usuario.query.get(id)

# Novo
db.session.get(Usuario, id)
```

### Erro 401 no Login

**Possíveis Causas:**
1. Senha incorreta
2. Usuário não existe
3. Formato do telefone (com/sem DDI)

**Solução:**
```powershell
# Resetar senha do usuário para teste
python reset_senha.py
```

### Erro 500 ao Criar Campanha

**Verificar:**
1. Todos os campos obrigatórios enviados
2. Slug único (não duplicado)
3. Formato de datas ISO 8601

**Debug:**
- Verificar logs do servidor
- Usar endpoint com try-catch (já implementado)
- A mensagem de erro deve mostrar o problema específico

### CORS Error no Frontend

**Verificar:**
1. Frontend rodando em `localhost:5173` ou `localhost:3000`
2. CORS configurado em `app/__init__.py`

**Adicionar Nova Origem:**
```python
# app/__init__.py
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://novo-dominio.com"  # Adicionar aqui
        ],
        ...
    }
})
```

### Servidor Não Inicia

**Verificar:**
1. Virtual environment ativado
2. Dependências instaladas (`pip install -r requirements.txt`)
3. Porta 5000 disponível

```powershell
# Verificar porta em uso
netstat -ano | findstr :5000

# Matar processo se necessário
taskkill /PID {PID} /F
```

---

## 💾 Backup e Recuperação

### Estratégia de Backup

**Recomendado (Produção):**
- Backup diário automático
- Retenção de 30 dias
- Backup antes de deploy/migração

### Script de Backup Automático

```python
# backup_automatico.py
import shutil
import os
from datetime import datetime

def fazer_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    origem = "instance/sistema.db"
    destino = f"backups/sistema_{timestamp}.db"
    
    os.makedirs("backups", exist_ok=True)
    shutil.copy2(origem, destino)
    print(f"✅ Backup criado: {destino}")
    
    # Limpar backups antigos (manter últimos 30)
    backups = sorted(os.listdir("backups"), reverse=True)
    for old_backup in backups[30:]:
        os.remove(f"backups/{old_backup}")
        print(f"🗑️  Backup antigo removido: {old_backup}")

if __name__ == '__main__':
    fazer_backup()
```

**Agendar (Windows Task Scheduler):**
```powershell
# Executar diariamente às 3h da manhã
schtasks /create /tn "Backup Rifas" /tr "C:\Projetos\Projeto-rifa\venv\Scripts\python.exe C:\Projetos\Projeto-rifa\backup_automatico.py" /sc daily /st 03:00
```

---

## 📊 Monitoramento

### Métricas Importantes

**Dashboard Admin:**
```bash
curl -X GET http://localhost:5000/api/admin/dashboard \
  -H "Authorization: Bearer {admin_token}"
```

Retorna:
- Total de usuários
- Total de campanhas
- Campanhas ativas
- Receita total
- Últimas vendas

### Alertas Recomendados

**Configurar monitoramento para:**
1. Servidor offline por mais de 5 minutos
2. Erro 500 acima de 10/hora
3. Tempo de resposta > 2 segundos
4. Disco com menos de 10% livre
5. Memória > 80% de uso

### Health Check

**Endpoint de Status:**
```bash
curl http://localhost:5000/
```

Deve retornar:
```json
{
  "mensagem": "API Gêmeos Brasil",
  "versao": "1.0",
  "endpoints": {...}
}
```

---

## 📝 Logs

### Localização dos Logs

**Windows:**
```
c:\Projetos\Projeto-rifa\logs\
```

### Visualizar Logs em Tempo Real

```powershell
Get-Content logs\app.log -Wait -Tail 50
```

### Logs de Erro

```python
# Adicionar em app.py para logging
import logging

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Rotação de Logs

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10_000_000,  # 10MB
    backupCount=5
)
```

---

## 🚨 Procedimentos de Emergência

### Sistema Fora do Ar

1. **Verificar servidor:**
   ```powershell
   netstat -ano | findstr :5000
   ```

2. **Reiniciar servidor:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   python app.py
   ```

3. **Verificar logs:**
   ```powershell
   Get-Content logs\app.log -Tail 100
   ```

### Banco Corrompido

1. **Verificar integridade:**
   ```bash
   sqlite3 instance/sistema.db "PRAGMA integrity_check;"
   ```

2. **Restaurar do backup:**
   ```powershell
   Copy-Item backups\sistema_YYYYMMDD_HHMMSS.db instance\sistema.db
   ```

3. **Reconstruir índices:**
   ```bash
   sqlite3 instance/sistema.db "REINDEX;"
   ```

### Perda de Acesso Admin

```python
# Criar admin de emergência
from app import create_app
from app.models import db, Usuario

app = create_app()
with app.app_context():
    # Buscar primeiro usuário ou criar novo
    admin = Usuario.query.first()
    if not admin:
        admin = Usuario(
            nome="Admin Emergencial",
            telefone="99999999999",
            is_admin=True
        )
        admin.set_senha("admin123")
        db.session.add(admin)
    else:
        admin.is_admin = True
        admin.set_senha("novaSenha123")
    
    db.session.commit()
    print(f"✅ Admin: {admin.telefone} / Senha: novaSenha123")
```

---

## 📞 Suporte Técnico

**Contato:**
- Email: dev@gemeosbrasil.com
- Documentação: [API_DOCUMENTATION.md](file:///c:/Projetos/Projeto-rifa/API_DOCUMENTATION.md)
- README: [README.md](file:///c:/Projetos/Projeto-rifa/README.md)

**Recursos:**
- Scripts utilitários: `c:\Projetos\Projeto-rifa\*.py`
- Documentação Postman: [POSTMAN_GUIDE.md](file:///c:/Projetos/Projeto-rifa/POSTMAN_GUIDE.md)

---

**Última Revisão:** 2026-01-19  
**Mantenedor:** Equipe Técnica Gêmeos Brasil
