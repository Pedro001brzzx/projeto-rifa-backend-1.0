from marshmallow import Schema, fields, validate, RAISE


class ComunicadoSchema(Schema):
    class Meta:
        unknown = RAISE

    titulo = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    conteudo = fields.Str(required=True)
    tipo = fields.Str(load_default='informativo', validate=validate.Length(max=50))
    ativo = fields.Bool(load_default=True)


class AtualizarComunicadoSchema(Schema):
    """Todos os campos opcionais; ausentes não são incluídos no dict resultante."""
    class Meta:
        unknown = RAISE

    titulo = fields.Str(validate=validate.Length(min=1, max=200))
    conteudo = fields.Str()
    tipo = fields.Str(validate=validate.Length(max=50))
    ativo = fields.Bool()


class ContatoSchema(Schema):
    class Meta:
        unknown = RAISE

    nome = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    mensagem = fields.Str(required=True)
    telefone = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=20))
    assunto = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=200))
