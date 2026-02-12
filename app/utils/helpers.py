import re

def somente_numeros(valor):
    """
    Remove todos os caracteres não numéricos de uma string.
    Retorna None se o resultado for vazio ou se o valor for nulo.
    """
    if not valor:
        return None
    numeros = re.sub(r'\D', '', str(valor))
    return numeros if numeros else None

def email_valido(email):
    """
    Valida o formato básico de um e-mail.
    """
    if not email:
        return False
    # Regex simples mas eficaz para formato de e-mail
    pattern = r'^[^@]+@[^@]+\.[^@]+$'
    return re.match(pattern, str(email)) is not None
