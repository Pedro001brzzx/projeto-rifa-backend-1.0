"""
Controller de Pagamentos - VERSÃO CORRIGIDA
Integração funcional com AbacatePay API
"""

import requests
import os
import qrcode
import base64
import json
from io import BytesIO
from datetime import datetime, timedelta
from app.models import db, Compra


def gerar_qrcode_base64(payload_pix):
    """
    Gera uma imagem QR Code em base64 a partir de uma string (payload PIX).
    """
    if not payload_pix:
        return None
        
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payload_pix)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return img_str


def _aprovar_e_gerar_titulos(compra):
    """
    Aprova o pagamento e gera os títulos da compra.

    IMPORTANTE: Esta é a ÚNICA função que gera títulos!
    Títulos são gerados APENAS após confirmação do pagamento.

    Args:
        compra: Objeto Compra a ser aprovada

    Raises:
        Exception: Se não houver títulos disponíveis
    """
    from app.controllers.compra_controller import gerar_titulos, MAX_TITULOS_POSSIVEIS
    from app.models import Titulo

    # 1. Verificar se já tem títulos (evitar duplicação)
    titulos_count = Titulo.query.filter_by(compra_id=compra.id).count()
    if titulos_count > 0:
        print(f"⚠️ Compra #{compra.id} já possui {titulos_count} títulos! Pulando geração.")
        return

    # 2. Validar disponibilidade de títulos
    titulos_ja_vendidos = Titulo.query.filter(
        Titulo.campanha_id == compra.campanha_id
    ).count()

    # Validação 1: Limite físico do sistema
    if titulos_ja_vendidos + compra.quantidade_titulos > MAX_TITULOS_POSSIVEIS:
        disponiveis = MAX_TITULOS_POSSIVEIS - titulos_ja_vendidos
        raise Exception(
            f'Títulos esgotados! Apenas {disponiveis} título(s) disponível(is). '
            f'Limite máximo: {MAX_TITULOS_POSSIVEIS}'
        )

    # Validação 2: Limite da campanha
    if compra.campanha.titulos_vendidos + compra.quantidade_titulos > compra.campanha.total_titulos:
        disponiveis = compra.campanha.total_titulos - compra.campanha.titulos_vendidos
        raise Exception(
            f'Títulos esgotados para esta campanha! Apenas {disponiveis} título(s) disponível(is).'
        )

    # 3. GERAR TÍTULOS
    print(f"🎫 Gerando {compra.quantidade_titulos} títulos para compra #{compra.id}...")
    gerar_titulos(compra.id, compra.campanha_id, compra.quantidade_titulos)

    # 4. Incrementar contador da campanha
    compra.campanha.titulos_vendidos += compra.quantidade_titulos

    # 5. Atualizar status da compra
    compra.status_pagamento = 'aprovado'
    compra.data_pagamento = datetime.utcnow()

    db.session.commit()

    print(f"✅ Compra #{compra.id} aprovada! Títulos gerados e campanha atualizada.")


def criar_checkout(usuario_id, data):
    """
    Cria um checkout e inicia o processo de pagamento

    Args:
        usuario_id: ID do usuário autenticado
        data: Dicionário com dados do checkout

    Returns:
        tuple: (response dict, status code)
    """
    # Validar dados obrigatórios da requisição
    if 'campanha_id' not in data or 'quantidade_titulos' not in data:
        return {'erro': 'campanha_id e quantidade_titulos são obrigatórios'}, 400

    from app.models import Usuario
    usuario_obj = Usuario.query.get(usuario_id)

    if not usuario_obj:
        return {'erro': 'Usuário não encontrado'}, 404

    try:
        # Camada 0: Bloqueio de Perfil Incompleto (Fintech Rules)
        validar_perfil_completo(usuario_obj)

        # Criar compra (que já gera os títulos e reserva o ID)
        from app.controllers.compra_controller import criar_compra
        response_compra, status_compra = criar_compra(usuario_id, data)

        if status_compra != 201:
            return response_compra, status_compra

        compra_id = response_compra['compra']['id']
        compra_obj = Compra.query.get(compra_id)
        metodo_pagamento = data.get('metodo_pagamento', 'pix')

        # Preparar dados de pagamento baseado no método (AbacatePay)
        from app.models import Usuario
        usuario_obj = Usuario.query.get(usuario_id)
        
        # Chama o gateway (Camada Blindada)
        pagamento_data = _gerar_dados_pagamento(response_compra['compra'], metodo_pagamento, usuario_obj)

        # PERSISTÊNCIA: Salvar códigos PIX no banco para consultas futuras (Polling/Reload)
        if metodo_pagamento == 'pix' and pagamento_data:
            try:
                compra_obj.pix_copia_cola = pagamento_data.get('pix_code')
                compra_obj.pix_qr_code_base64 = pagamento_data.get('qr_code')
                db.session.commit()
                print(f"💾 [DB] Dados PIX salvos para Compra #{compra_id}")
            except Exception as e:
                db.session.rollback()
                print(f"⚠️ [WARNING] Erro ao salvar dados PIX no banco: {e}")

        return {
            'mensagem': 'Checkout criado com sucesso',
            'compra_id': compra_id,
            'status_pagamento': compra_obj.status_pagamento,
            'valor_total': float(compra_obj.valor_total),
            'metodo_pagamento': metodo_pagamento,
            'pagamento': pagamento_data,
            'compra': response_compra['compra']
        }, 201

    except ValueError as e:
        # Erros de validação (Perfil Incompleto, CPF, Telefone, Email) -> 400 Bad Request
        print(f"⚠️ [VALIDATION ERROR] Checkout bloqueado: {e}")
        return {'erro': str(e), 'categoria': 'perfil_incompleto'}, 400
    except Exception as e:
        # Erros inesperados ou do Gateway -> 500 Internal Server Error
        print(f"❌ [INTERNAL ERROR] Checkout falhou: {e}")
        import traceback
        traceback.print_exc()
        return {'erro': f'Erro interno ao processar pagamento: {str(e)}'}, 500


def validar_perfil_completo(usuario):
    """
    Verifica se o usuário possui todos os dados necessários para o gateway de pagamento.
    Lança ValueError se algum dado estiver faltando ou inválido.
    """
    from app.utils.helpers import somente_numeros, email_valido
    
    erros = []
    
    cpf_limpo = somente_numeros(usuario.cpf)
    if not cpf_limpo or len(cpf_limpo) != 11:
        erros.append("CPF obrigatório (11 dígitos)")
        
    if not email_valido(usuario.email):
        erros.append("E-mail válido obrigatório")
        
    tel_limpo = somente_numeros(usuario.telefone)
    if not tel_limpo or len(tel_limpo) < 10:
        erros.append("Telefone com DDD obrigatório")
        
    if not usuario.nome or len(usuario.nome.strip()) < 3:
        erros.append("Nome completo obrigatório")

    if erros:
        msg = "Complete seu perfil para realizar o pagamento: " + ", ".join(erros)
        raise ValueError(msg)

    return True


def _gerar_dados_pagamento(compra, metodo_pagamento, usuario=None):
    """
    Gera dados de pagamento PIX usando AbacatePay (API billing/create)
    
    CORREÇÃO: Usa API REST diretamente, sem SDK, para ter controle total

    Args:
        compra: Dicionário com dados da compra
        metodo_pagamento: Deve ser sempre 'pix'
        usuario: Objeto Usuario (opcional, mas recomendado para dados do cliente)
    
    Returns:
        dict: Dados do pagamento PIX para o cliente
    """
    import os

    # Sistema aceita apenas PIX
    if metodo_pagamento != 'pix':
        raise ValueError('Sistema aceita apenas pagamento via PIX')

    # Verificar se está configurado o AbacatePay
    api_key = os.getenv('ABACATEPAY_API_KEY')

    if not api_key or api_key == 'sua-api-key-aqui':
        # MODO DESENVOLVIMENTO: Retornar mock se não configurado
        print("⚠️ AVISO: AbacatePay não configurado. Usando dados MOCK.")
        return {
            'tipo': 'pix',
            'qr_code': f'00020126580014br.gov.bcb.pix0136{compra["id"]:032d}520400005303986540{compra["valor_total"]:.2f}5802BR5925Sistema Rifas6014SAO PAULO62070503***6304XXXX',
            'qr_code_base64': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
            'copia_cola': f'00020126580014br.gov.bcb.pix{compra["id"]}',
            'expira_em': (datetime.utcnow() + timedelta(minutes=10)).isoformat() + 'Z',
            'instrucoes': '⚠️ MODO DESENVOLVIMENTO - Configure ABACATEPAY_API_KEY no .env'
        }

    # PRODUÇÃO: Usar AbacatePay real (API REST direta)
    try:
        import requests
        
        # Valor em centavos (int)
        amount_cents = int(float(compra['valor_total']) * 100)
        
        # Usar API billing/create
        url = 'https://api.abacatepay.com/v1/billing/create'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Obter URLs do ambiente
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        backend_url = os.getenv('BACKEND_URL', 'http://localhost:5000')
        
        payload = {
            'frequency': 'ONE_TIME',
            'methods': ['PIX'],
            'products': [{
                'externalId': str(compra['id']),
                'name': 'Títulos de Rifa',
                'description': f"Compra de {compra['quantidade_titulos']} título(s)",
                'quantity': compra['quantidade_titulos'],
                'price': amount_cents
            }],
            'returnUrl': f'{frontend_url}/checkout/sucesso',
            'completionUrl': f'{backend_url}/api/pagamentos/webhook'
        }
        
        # Camada 2: Sanitização rigorosa (Nível Fintech)
        from app.utils.helpers import somente_numeros, email_valido
        import json

        # Camada 3: Validação Rigorosa (Zero Fallback)
        cpf_limpo = somente_numeros(usuario.cpf)
        tel_limpo = somente_numeros(usuario.telefone)
        email_clean = str(usuario.email or "").strip().lower()

        # Validações de Identidade e Segurança (Fintech Mode: Zero Fallback)
        if not cpf_limpo or len(cpf_limpo) != 11:
            raise ValueError("Identidade incompleta: CPF obrigatório (11 dígitos).")

        if not tel_limpo or len(tel_limpo) < 10:
            raise ValueError("Contato incompleto: Telefone com DDD obrigatório.")

        if not email_valido(email_clean):
            raise ValueError("Perfil incompleto: E-mail obrigatório para processar o pagamento.")

        # Payload Limpo e Blindado
        customer_data = {
            'name': str(usuario.nome)[:100],
            'email': email_clean,
            'cellphone': tel_limpo,
            'taxId': cpf_limpo
        }

        payload['customer'] = customer_data
        
        # Log de Segurança (Audit Trail Style)
        print(f"🏛️ [AUDIT] Iniciando checkout para Compra #{compra['id']} | Customer: {customer_data['email']} | taxId: {customer_data['taxId']}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # Tratamento profissional de resposta (Fine-grained Parsing)
        try:
            # Tenta converter para JSON, fallbacks para raw text se falhar
            resp_data = response.json()
            if not resp_data.get('success', True):
                error_msg = resp_data.get('error', 'Erro reportado pelo gateway')
                print(f"❌ [API ERROR] AbacatePay: {error_msg}")
                raise Exception(f'AbacatePay falhou: {error_msg}')
        except (ValueError, json.JSONDecodeError):
            if response.status_code != 200:
                 print(f"❌ [HTTP ERROR] {response.status_code}: {response.text[:200]}")
                 raise Exception(f'Erro na comunicação com gateway (HTTP {response.status_code})')
            # Se for 200 mas não for JSON (estranho), seguimos o fluxo mas logamos
            print("⚠️ [WARNING] AbacatePay retornou 200 mas o body não é JSON válido.")

        data = response.json()
        
        # AbacatePay Billing API: os dados principais ficam em 'data'
        billing_data = data.get('data', {})
        
        # Extração Ultra-Resiliente (Copia e Cola)
        # 1. Tentar estrutura pixQrCode (padrão documentado em algumas versões)
        # 2. Tentar estrutura pix.copyPaste (sugerida pelo usuário)
        # 3. Tentar qrcode/brcode direto no billing_data
        pix_payload = (
            billing_data.get('pixQrCode', {}).get('qrcode') or 
            billing_data.get('pixQrCode', {}).get('brcode') or
            billing_data.get('pix', {}).get('copyPaste') or
            billing_data.get('qrcode') or
            billing_data.get('brcode')
        )
        
        # Fallback Estratégico para Dev/Bills sem PIX imediato
        # Se a API retornou ID mas não o PIX (comum em faturamentos que geram URL),
        # usamos a URL ou o ID para gerar um código visível para teste, 
        # mas priorizamos o erro em produção se necessário.
        if not pix_payload:
            if billing_data.get('devMode') or os.getenv('FLASK_ENV') == 'development':
                print(f"⚠️ [DEV] API não retornou PIX. Gerando payload de teste para Bill {billing_data.get('id')}")
                pix_payload = f"00020126580014br.gov.bcb.pix0136{billing_data.get('id')}520400005303986"
            else:
                print(f"⚠️ [WARNING] Payload PIX não encontrado na resposta real: {data}")
                # Em produção, se não tiver PIX, o QR Code local falhará
                # Mas vamos tentar usar o 'url' como fallback para o QR Code se nada mais existir
                pix_payload = billing_data.get('url')

        if not pix_payload:
            raise Exception("Não foi possível extrair o código PIX da operadora.")

        # Camada 4: Geração do QR Code Local
        qr_code_base64 = gerar_qrcode_base64(pix_payload)
        
        # Retorno Blindado e Rico em dados para o Frontend
        return {
            'tipo': 'pix',
            'payment_url': billing_data.get('url'),  # URL da página de destino
            'payment_id': billing_data.get('id'),
            'pix_code': pix_payload,                 # Código Copia e Cola
            'qr_code': qr_code_base64,               # Imagem Base64 PNG
            'copia_cola': pix_payload,               # Legado (compatibilidade)
            'qr_code_base64': qr_code_base64,        # Legado (compatibilidade)
            'expira_em': billing_data.get('expiresAt') or (datetime.utcnow() + timedelta(minutes=10)).isoformat() + 'Z',
            'instrucoes': 'Escaneie o QR Code ou use o Copia e Cola no app do seu banco.'
        }

    except ImportError:
        raise Exception('Biblioteca requests não instalada. Execute: pip install requests')
    except ValueError as e:
        # Permitir que erros de validação subam sem serem encapsulados como erro de sistema
        raise e
    except requests.exceptions.Timeout:
        print("❌ Timeout ao conectar com AbacatePay")
        raise Exception('Timeout ao processar pagamento. Tente novamente.')
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão com AbacatePay: {str(e)}")
        raise Exception(f'Erro de conexão com gateway de pagamento')
    except Exception as e:
        print(f"❌ Erro ao criar PIX AbacatePay: {str(e)}")
        raise Exception(f'Erro ao processar pagamento: {str(e)}')


def _verificar_e_marcar_expiracao(compra):
    """
    Verifica se uma compra está expirada e atualiza o status automaticamente.
    Validação em tempo real - não depende do job de cleanup.

    IMPORTANTE: Compras pendentes NÃO TÊM títulos gerados, então não precisa deletá-los.

    Args:
        compra: Objeto Compra do banco de dados

    Returns:
        bool: True se a compra foi marcada como expirada, False caso contrário
    """
    # Apenas compras pendentes podem expirar
    if compra.status_pagamento != 'pendente':
        return False

    # Verificar se tem campo expira_em e se já expirou
    if hasattr(compra, 'expira_em') and compra.expira_em:
        now = datetime.utcnow()

        if compra.expira_em < now:
            # Compra expirada! Atualizar status
            print(f"⏱️ Compra #{compra.id} expirada - Marcando como 'expirado'")

            # ⚠️ NÃO precisa deletar títulos - compras pendentes não têm títulos!
            # Títulos são gerados APENAS após aprovação do pagamento

            # Marcar como expirada
            compra.status_pagamento = 'expirado'

            db.session.commit()

            print(f"✅ Compra #{compra.id} marcada como expirada (sem títulos para limpar)")
            return True

    return False


def consultar_pagamento(compra_id):
    """
    Consulta o status de um pagamento

    Args:
        compra_id: ID da compra

    Returns:
        tuple: (response dict, status code)
    """
    compra = Compra.query.get(compra_id)

    if not compra:
        return {'erro': 'Compra não encontrada'}, 404

    # VALIDAÇÃO EM TEMPO REAL: Verificar se a compra expirou
    _verificar_e_marcar_expiracao(compra)

    # Incluir dados da campanha
    campanha_data = {
        'id': compra.campanha.id,
        'titulo': compra.campanha.titulo,
        'slug': compra.campanha.slug,
        'imagem_principal': compra.campanha.imagem_principal,
        'valor_titulo': float(compra.campanha.valor_titulo),
        'total_titulos': compra.campanha.total_titulos
    } if compra.campanha else None

    # Objeto de pagamento enriquecido (necessário para o Frontend exibir QR Code no Polling)
    pagamento_info = None
    if compra.metodo_pagamento == 'pix' and (compra.pix_copia_cola or compra.pix_qr_code_base64):
        pagamento_info = {
            'tipo': 'pix',
            'pix_code': compra.pix_copia_cola,
            'qr_code': compra.pix_qr_code_base64,
            'copia_cola': compra.pix_copia_cola,        # Compatibilidade legado
            'qr_code_base64': compra.pix_qr_code_base64 # Compatibilidade legado
        }

    return {
        'compra_id': compra.id,
        'status_pagamento': compra.status_pagamento,
        'metodo_pagamento': compra.metodo_pagamento,
        'valor_total': float(compra.valor_total),
        'quantidade_titulos': compra.quantidade_titulos,
        'data_pagamento': (compra.data_pagamento.isoformat() + 'Z') if compra.data_pagamento else None,
        'criado_em': compra.criado_em.isoformat() + 'Z',
        'expira_em': (getattr(compra, 'expira_em').isoformat() + 'Z') if getattr(compra, 'expira_em', None) else None,
        'campanha': campanha_data,
        'pagamento': pagamento_info
    }, 200


def processar_webhook(data, gateway='abacatepay', raw_body=None, signature=None):
    """
    Processa webhook de confirmação de pagamento do AbacatePay

    Args:
        data: Dados recebidos do webhook
        gateway: Nome do gateway
        raw_body: Corpo bruto da requisição (bytes) para validação de assinatura
        signature: Assinatura recebida no header X-Webhook-Signature

    Returns:
        tuple: (response dict, status code)
    """
    import hmac
    import hashlib
    import os

    print(f"📩 Webhook recebido ({gateway}): {data}")

    # 1. Validação de Segurança (AbacatePay)
    if gateway == 'abacatepay':
        webhook_secret = os.getenv('ABACATEPAY_WEBHOOK_SECRET')

        # Se configurado secret, é OBRIGATÓRIO validar
        if webhook_secret:
            if not raw_body or not signature:
                print("⛔ Webhook rejeitado: Falta assinatura ou body")
                return {'erro': 'Assinatura obrigatória'}, 401

            # Recalcular HMAC
            expected_signature = hmac.new(
                webhook_secret.encode(),
                raw_body,  # Deve ser bytes
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                print(f"⛔ Assinatura inválida! Recebida: {signature}, Esperada: {expected_signature}")
                return {'erro': 'Assinatura inválida'}, 401

            print("✅ Assinatura do webhook validada com sucesso!")
        else:
            print("⚠️ AVISO: ABACATEPAY_WEBHOOK_SECRET não configurado. Aceitando webhook inseguro (DEV ONLY).")

    # 2. Processar Evento
    event_type = data.get('event')

    if event_type == 'billing.paid':
        # Extrair dados do pagamento
        webhook_data = data.get('data', {})
        billing_data = webhook_data.get('billing', {})
        
        # Obter compra_id dos produtos
        products = billing_data.get('products', [])
        
        if not products:
            print("⚠️ Nenhum produto encontrado no webhook")
            return {'erro': 'Produtos não encontrados'}, 400
        
        # ExternalId contém o ID da compra
        compra_id = products[0].get('externalId')
        
        if not compra_id:
            print("⚠️ Compra ID não encontrado no webhook")
            return {'erro': 'Compra ID não identificado'}, 400

        # Converter para int
        try:
            compra_id = int(compra_id)
        except:
            print(f"⚠️ Compra ID inválido: {compra_id}")
            return {'erro': 'Compra ID inválido'}, 400

        # 3. Aprovar Compra
        print(f"💰 Processando pagamento para Compra #{compra_id}")
        compra = Compra.query.get(compra_id)

        if not compra:
            print(f"❌ Compra #{compra_id} não encontrada no banco")
            return {'erro': 'Compra não encontrada'}, 404

        if compra.status_pagamento == 'aprovado':
            print(f"ℹ️ Compra #{compra_id} já aprovada anteriormente.")
            return {'mensagem': 'Já processado'}, 200

        # APROVAR E GERAR TÍTULOS
        try:
            _aprovar_e_gerar_titulos(compra)

            # Log de arrecadação
            print(f"💸 ARRECADAÇÃO REGISTRADA: Campanha {compra.campanha_id} +R$ {compra.valor_total}")

            return {'mensagem': 'Pagamento aprovado com sucesso'}, 200

        except Exception as e:
            print(f"❌ Erro ao aprovar compra #{compra_id}: {e}")
            return {'erro': f"Erro interno: {str(e)}"}, 500

    # Ignorar outros eventos por enquanto
    return {'mensagem': 'Evento ignorado'}, 200


def aprovar_pagamento_manual(compra_id, admin_user_id):
    """
    Aprova um pagamento manualmente (apenas admin)
    Útil para pagamentos offline ou testes

    Args:
        compra_id: ID da compra
        admin_user_id: ID do usuário admin

    Returns:
        tuple: (response dict, status code)
    """
    from app.models import Usuario

    # Verificar se é admin
    admin = Usuario.query.get(int(admin_user_id))
    if not admin or not admin.is_admin:
        return {'erro': 'Acesso negado'}, 403

    compra = Compra.query.get(compra_id)

    if not compra:
        return {'erro': 'Compra não encontrada'}, 404

    # VALIDAÇÃO: Prevenir aprovação de compra expirada
    if _verificar_e_marcar_expiracao(compra):
        return {
            'erro': 'Compra expirada - prazo de pagamento excedido',
            'compra_id': compra.id,
            'expira_em': compra.expira_em.isoformat() if compra.expira_em else None
        }, 400

    # Se já aprovado, retornar
    if compra.status_pagamento == 'aprovado':
        return {
            'mensagem': 'Pagamento já estava aprovado',
            'compra_id': compra.id
        }, 200

    # Aprovar e gerar títulos
    status_anterior = compra.status_pagamento

    try:
        # Esta função já faz TUDO:
        # - Gera títulos
        # - Incrementa contador da campanha
        # - Atualiza status para 'aprovado'
        # - Define data_pagamento
        _aprovar_e_gerar_titulos(compra)

        return {
            'mensagem': 'Pagamento aprovado manualmente',
            'compra_id': compra.id,
            'status_anterior': status_anterior,
            'status_atual': 'aprovado',
            'aprovado_por': admin.nome
        }, 200
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro na aprovação manual: {str(e)}")
        return {'erro': f'Erro ao gerar títulos: {str(e)}'}, 500
