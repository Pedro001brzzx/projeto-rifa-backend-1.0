from marshmallow import Schema, fields, validate, RAISE


class CriarCampanhaSchema(Schema):
    class Meta:
        unknown = RAISE

    titulo = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    descricao = fields.Str(load_default=None, allow_none=True)
    slug = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=255))
    imagem_principal = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=500))
    codigo = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=50))
    tipo = fields.Str(load_default='regular', validate=validate.Length(max=50))
    premio = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=200))
    valor_titulo = fields.Decimal(load_default=None, allow_none=True, places=2)
    total_titulos = fields.Int(load_default=None, allow_none=True, validate=validate.Range(min=1))
    min_quantidade_compra = fields.Int(load_default=1, validate=validate.Range(min=1))
    max_quantidade_compra = fields.Int(load_default=None, allow_none=True, validate=validate.Range(min=1))
    regulamento = fields.Str(load_default=None, allow_none=True)
    data_sorteio = fields.Str(load_default=None, allow_none=True)
    data_fim = fields.Str(load_default=None, allow_none=True)


class AtualizarCampanhaSchema(Schema):
    """Todos os campos opcionais; ausentes não são incluídos no dict resultante."""
    class Meta:
        unknown = RAISE

    titulo = fields.Str(validate=validate.Length(min=1, max=200))
    descricao = fields.Str(allow_none=True)
    slug = fields.Str(allow_none=True, validate=validate.Length(max=255))
    imagem_principal = fields.Str(allow_none=True, validate=validate.Length(max=500))
    codigo = fields.Str(allow_none=True, validate=validate.Length(max=50))
    tipo = fields.Str(validate=validate.Length(max=50))
    premio = fields.Str(allow_none=True, validate=validate.Length(max=200))
    valor_titulo = fields.Decimal(allow_none=True, places=2)
    total_titulos = fields.Int(allow_none=True, validate=validate.Range(min=1))
    min_quantidade_compra = fields.Int(validate=validate.Range(min=1))
    max_quantidade_compra = fields.Int(allow_none=True, validate=validate.Range(min=1))
    regulamento = fields.Str(allow_none=True)
    data_sorteio = fields.Str(allow_none=True)
    data_fim = fields.Str(allow_none=True)
    status = fields.Str(validate=validate.OneOf(['ativo', 'pausado', 'concluido', 'cancelado']))


class TitulosPremiadosSchema(Schema):
    class Meta:
        unknown = RAISE

    numero_titulo = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    valor_premio = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))


class GanhadorSchema(Schema):
    class Meta:
        unknown = RAISE

    compra_id = fields.Int(required=True, validate=validate.Range(min=1))
    titulo_id = fields.Int(load_default=None, allow_none=True, validate=validate.Range(min=1))
    metodo = fields.Str(load_default='manual', validate=validate.OneOf(['manual', 'automatico']))
