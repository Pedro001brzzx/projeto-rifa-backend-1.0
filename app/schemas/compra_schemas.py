from marshmallow import Schema, fields, validate, RAISE


class CheckoutSchema(Schema):
    class Meta:
        unknown = RAISE

    campanha_id = fields.Str(required=True)
    quantidade_titulos = fields.Int(required=True, validate=validate.Range(min=1))
    metodo_pagamento = fields.Str(load_default='pix')
