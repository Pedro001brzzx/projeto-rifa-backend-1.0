from functools import wraps
from flask import request, jsonify, g
from marshmallow import ValidationError


def validate_body(schema_class):
    """
    Decorator que valida o corpo JSON da requisição contra um schema Marshmallow.
    Em caso de erro retorna 400 com campo-a-campo; caso contrário injeta
    os dados validados em g.validated_data para uso pela view function.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            raw = request.get_json(silent=True) or {}
            try:
                g.validated_data = schema_class().load(raw)
            except ValidationError as e:
                return jsonify({"erro": "Dados inválidos", "campos": e.messages}), 400
            return f(*args, **kwargs)
        return wrapper
    return decorator
