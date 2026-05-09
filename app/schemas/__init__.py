from app.schemas.auth_schemas import (
    RegistroSchema,
    LoginSchema,
    ForgotSenhaSchema,
    ResetSenhaSchema,
    AtualizarPerfilSchema,
)
from app.schemas.campanha_schemas import (
    CriarCampanhaSchema,
    AtualizarCampanhaSchema,
    TitulosPremiadosSchema,
    GanhadorSchema,
)
from app.schemas.compra_schemas import CheckoutSchema
from app.schemas.conteudo_schemas import (
    ComunicadoSchema,
    AtualizarComunicadoSchema,
    ContatoSchema,
)

__all__ = [
    'RegistroSchema',
    'LoginSchema',
    'ForgotSenhaSchema',
    'ResetSenhaSchema',
    'AtualizarPerfilSchema',
    'CriarCampanhaSchema',
    'AtualizarCampanhaSchema',
    'TitulosPremiadosSchema',
    'GanhadorSchema',
    'CheckoutSchema',
    'ComunicadoSchema',
    'AtualizarComunicadoSchema',
    'ContatoSchema',
]
