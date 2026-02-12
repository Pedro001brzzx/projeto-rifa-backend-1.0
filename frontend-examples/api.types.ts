// Tipos e Interfaces da API
// Cole este arquivo em: src/types/api.types.ts

// ==================== USUÁRIO ====================
export interface Usuario {
    id: number;
    nome: string;
    telefone: string;
    email?: string;
    cpf?: string;
    cidade?: string;
    estado?: string;
    is_admin?: boolean;
    criado_em: string;
}

export interface RegistroData {
    nome: string;
    telefone: string;
    senha: string;
    email?: string;
    cpf?: string;
    cidade?: string;
    estado?: string;
}

export interface LoginData {
    telefone: string;
    senha: string;
}

export interface AuthResponse {
    mensagem: string;
    token: string;
    usuario: Usuario;
}

// ==================== CAMPANHA ====================
export interface Campanha {
    id: number;
    titulo: string;
    descricao?: string;
    slug: string;
    imagem_principal?: string;
    codigo?: string;
    tipo: 'regular' | 'especial';
    premio?: string;
    valor_titulo: number;
    total_titulos: number;
    titulos_vendidos: number;
    data_sorteio: string;
    status: 'ativo' | 'concluido' | 'cancelado';
    criado_em: string;
    percentual_vendido?: number;
    titulos_disponiveis?: number;
    ganhador?: {
        nome: string;
        cidade?: string;
        estado?: string;
    } | null;
}

export interface CampanhaListResponse {
    campanhas: Campanha[];
    total: number;
    paginas: number;
    pagina_atual: number;
}

export interface CampanhaParams {
    status?: 'ativo' | 'concluido' | 'cancelado';
    page?: number;
    per_page?: number;
}

export interface CriarCampanhaData {
    titulo: string;
    descricao?: string;
    slug: string;
    imagem_principal?: string;
    codigo?: string;
    tipo?: string;
    premio?: string;
    valor_titulo?: number;
    total_titulos?: number;
    data_sorteio: string;
    regulamento?: string;
}

// ==================== COMPRA E TÍTULOS ====================
export interface Titulo {
    id: number;
    numero: string;
    is_ganhador: boolean;
}

export interface Compra {
    id: number;
    campanha: Campanha;
    quantidade_titulos: number;
    valor_total: number;
    status_pagamento: 'pendente' | 'aprovado' | 'recusado';
    metodo_pagamento: 'pix' | 'cartao' | 'boleto';
    data_pagamento?: string;
    criado_em: string;
    titulos: Titulo[];
}

export interface CriarCompraData {
    campanha_id: number;
    quantidade_titulos: number;
    metodo_pagamento?: 'pix' | 'cartao' | 'boleto';
}

export interface CompraResponse {
    mensagem: string;
    compra: Compra;
}

export interface MeusTitulosResponse {
    compras: Compra[];
    total: number;
    paginas: number;
    pagina_atual: number;
}

// ==================== GANHADORES ====================
export interface Ganhador {
    id: number;
    titulo: string;
    slug: string;
    premio: string;
    data_sorteio: string;
    status: string;
    numero_sorteado: string;
    ganhador: {
        nome: string;
        cidade?: string;
        estado?: string;
    };
}

export interface GanhadoresResponse {
    ganhadores: Ganhador[];
    total: number;
    paginas: number;
}

// ==================== CONTEÚDO ====================
export interface Artigo {
    id: number;
    titulo: string;
    slug: string;
    conteudo: string;
    imagem?: string;
    autor: string;
    criado_em: string;
}

export interface Comunicado {
    id: number;
    titulo: string;
    conteudo: string;
    tipo: 'informativo' | 'alerta' | 'aviso';
    criado_em: string;
}

export interface ContatoData {
    nome: string;
    email: string;
    telefone?: string;
    assunto?: string;
    mensagem: string;
}

// ==================== RESPONSES GENÉRICAS ====================
export interface ApiError {
    erro: string;
    sugestao?: string;
}

export interface MessageResponse {
    mensagem: string;
}

export interface PaginationParams {
    page?: number;
    per_page?: number;
}
