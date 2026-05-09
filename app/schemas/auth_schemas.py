from marshmallow import Schema, fields, validate, validates, ValidationError, RAISE


class RegistroSchema(Schema):
    class Meta:
        unknown = RAISE

    nome = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    telefone = fields.Str(required=True)
    cpf = fields.Str(required=True)
    senha = fields.Str(required=True, validate=validate.Length(min=6))
    cidade = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=100))
    estado = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=2))

    @validates('telefone')
    def validate_telefone(self, value):
        digits = ''.join(c for c in str(value) if c.isdigit())
        if len(digits) < 10:
            raise ValidationError('Telefone inválido (mínimo 10 dígitos).')

    @validates('cpf')
    def validate_cpf(self, value):
        digits = ''.join(c for c in str(value) if c.isdigit())
        if len(digits) != 11:
            raise ValidationError('CPF deve conter exatamente 11 dígitos.')


class LoginSchema(Schema):
    class Meta:
        unknown = RAISE

    telefone = fields.Str(required=True)
    senha = fields.Str(required=True)


class ForgotSenhaSchema(Schema):
    class Meta:
        unknown = RAISE

    email = fields.Email(required=True)


class ResetSenhaSchema(Schema):
    class Meta:
        unknown = RAISE

    token = fields.Str(required=True)
    senha = fields.Str(required=True, validate=validate.Length(min=6))


class AtualizarPerfilSchema(Schema):
    class Meta:
        unknown = RAISE

    nome = fields.Str(validate=validate.Length(min=1, max=100))
    email = fields.Email(validate=validate.Length(max=120))
    endereco = fields.Str(validate=validate.Length(max=255))
    cidade = fields.Str(validate=validate.Length(max=100))
    estado = fields.Str(validate=validate.Length(max=2))
    cep = fields.Str(validate=validate.Length(max=10))
