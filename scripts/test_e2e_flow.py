"""
Teste E2E: Campanha + Usuário Admin + Fluxo de Compra
Simula o fluxo completo que o front-end executa:
  1. Login como admin
  2. Criar campanha (100.000 tickets, R$0.10)
  3. Criar novo usuário com is_admin=True
  4. Login do novo usuário
  5. Comprar rifas
  6. Admin aprova a compra (ou fluxo automático)
  7. Verificar bilhetes gerados
"""
import json
import sys
import os
import urllib.request
import urllib.error

BASE = "http://localhost:5000"

VERDE  = "\033[92m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
RESET  = "\033[0m"
NEGRITO = "\033[1m"

def ok(msg):   print(f"  {VERDE}✅ {msg}{RESET}")
def warn(msg): print(f"  {AMARELO}⚠️  {msg}{RESET}")
def err(msg):  print(f"  {VERMELHO}❌ {msg}{RESET}")
def titulo(msg): print(f"\n{NEGRITO}{'─'*60}\n  {msg}\n{'─'*60}{RESET}")

# ─────────────────────────────────────────────
def req(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
        except Exception:
            body = {"raw": e.reason}
        return e.code, body

# ─────────────────────────────────────────────
resultados = []

def checar(label, status, resp, esperado=200):
    passou = status == esperado
    resultados.append((label, passou))
    if passou:
        ok(f"{label} → HTTP {status}")
    else:
        err(f"{label} → HTTP {status} (esperado {esperado})")
        print(f"     Resposta: {json.dumps(resp, ensure_ascii=False, indent=2)[:400]}")
    return passou

# ══════════════════════════════════════════════
titulo("1. LOGIN ADMIN EXISTENTE")
status, resp = req("POST", "/api/auth/login", {
    "telefone": os.getenv("ADMIN_PHONE", "5583994099696"),
    "senha":    os.getenv("ADMIN_PASSWORD", "123456"),
})
checar("Login admin", status, resp)
admin_token = resp.get("access_token") or resp.get("token")
if not admin_token:
    err("Sem token — abortando")
    sys.exit(1)
ok(f"Token admin obtido (…{admin_token[-20:]})")

# ══════════════════════════════════════════════
titulo("2. CRIAR CAMPANHA (100.000 tickets, R$0,10)")
status, resp = req("POST", "/api/campanhas", {
    "titulo":        "Campanha Teste E2E",
    "descricao":     "Campanha criada pelo script de teste automatizado",
    "valor_titulo":  0.10,
    "total_titulos": 100000,
    "data_sorteio":  "2026-12-31T23:59:00",
}, token=admin_token)
passou = checar("Criar campanha", status, resp, esperado=201)
camp_obj = resp.get("campanha") or resp
campanha_id = camp_obj.get("id")
campanha_public_id = camp_obj.get("public_id")
if not passou or not campanha_id:
    err(f"Falha ao criar campanha. Resposta completa: {resp}")
    sys.exit(1)
ok(f"Campanha criada → id={campanha_id} | public_id={campanha_public_id}")

# ══════════════════════════════════════════════
titulo("3. CRIAR NOVO USUÁRIO ADMIN")
novo_tel   = "11999888777"
novo_senha = "Senha@123"
# Tenta registrar
status, resp = req("POST", "/api/auth/registro", {
    "nome":     "Testador Admin E2E",
    "telefone": novo_tel,
    "senha":    novo_senha,
    "email":    "testador_e2e@teste.com",
    "cpf":      "12345678901",
})
ja_existe = status == 400 and "já cadastrado" in str(resp)
if status in (200, 201):
    checar("Registrar usuário", status, resp, esperado=status)
    ok(f"Usuário {novo_tel} criado")
elif ja_existe:
    warn(f"Usuário {novo_tel} já existe — continuando")
    resultados.append(("Registrar usuário", True))
else:
    checar("Registrar usuário", status, resp, esperado=201)

# Promove a admin via script interno
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import create_app
from app.extensions import db
from app.models.usuario import Usuario

app = create_app()
with app.app_context():
    u = Usuario.query.filter_by(telefone=novo_tel).first()
    if u:
        u.is_admin = True
        db.session.commit()
        ok(f"Usuário {novo_tel} promovido a admin (is_admin=True)")
    else:
        err(f"Usuário {novo_tel} não encontrado no banco após registro")
        sys.exit(1)

# ══════════════════════════════════════════════
titulo("4. LOGIN DO NOVO USUÁRIO ADMIN")
status, resp = req("POST", "/api/auth/login", {
    "telefone": novo_tel,
    "senha":    novo_senha,
})
checar("Login novo admin", status, resp)
user_token = resp.get("access_token") or resp.get("token")
if not user_token:
    err("Sem token do novo usuário — abortando")
    sys.exit(1)
ok(f"Token novo admin (…{user_token[-20:]})")

# Verifica dados do perfil
status, resp = req("GET", "/api/auth/perfil", token=user_token)
checar("GET /api/auth/perfil", status, resp)
if status == 200:
    ok(f"  nome={resp.get('nome')} | is_admin={resp.get('is_admin')}")

# ══════════════════════════════════════════════
titulo("5. COMPRAR RIFAS (10 bilhetes)")
status, resp = req("POST", "/api/compras", {
    "campanha_id":        campanha_public_id,
    "quantidade_titulos": 10,
    "metodo_pagamento":   "pix",
}, token=user_token)
checar("Criar compra", status, resp, esperado=201)
compra_id = resp.get("id") or (resp.get("compra") or {}).get("id")
if not compra_id:
    # Tenta extrair de estrutura alternativa
    compra_id = resp.get("compra_id")
if compra_id:
    ok(f"Compra criada → id={compra_id}")
else:
    warn(f"ID de compra não encontrado na resposta: {list(resp.keys())}")

# ══════════════════════════════════════════════
titulo("6. APROVAR COMPRA (admin)")
if compra_id:
    status, resp = req("POST", f"/api/pagamentos/{compra_id}/aprovar", token=admin_token)
    checar("Aprovar pagamento", status, resp, esperado=status if status in (200, 201) else 200)
else:
    warn("Pulando aprovação — sem compra_id")

# ══════════════════════════════════════════════
titulo("7. VERIFICAR BILHETES GERADOS")
status, resp = req("GET", "/api/meus-titulos", token=user_token)
checar("Listar meus compras", status, resp)
if status == 200:
    compras_lista = resp.get("compras") or []
    total = resp.get("total", len(compras_lista))
    ok(f"Total compras encontradas: {total}")
    for c in compras_lista[:3]:
        titulos_c = c.get("titulos") or []
        print(f"    • public_id={str(c.get('public_id',''))[:8]}… | status={c.get('status_pagamento')} | qtd={c.get('quantidade_titulos')} | titulos={len(titulos_c)}")

# Detalhe do pagamento
if compra_id:
    status, resp = req("GET", f"/api/pagamentos/{compra_id}", token=user_token)
    if status == 200:
        checar("Detalhe pagamento", status, resp)
        ok(f"  status_pagamento={resp.get('status_pagamento')} | valor_total={resp.get('valor_total')}")
    else:
        warn(f"GET /api/pagamentos/{compra_id} retornou {status}")

# ══════════════════════════════════════════════
titulo("RESUMO DOS TESTES")
passou_count = sum(1 for _, p in resultados if p)
total_count  = len(resultados)
for label, passou in resultados:
    s = f"{VERDE}✅" if passou else f"{VERMELHO}❌"
    print(f"  {s}  {label}{RESET}")

print()
if passou_count == total_count:
    print(f"{VERDE}{NEGRITO}  Todos os {total_count} testes passaram.{RESET}")
else:
    print(f"{AMARELO}{NEGRITO}  {passou_count}/{total_count} testes passaram.{RESET}")
