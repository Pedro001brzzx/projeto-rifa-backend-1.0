// Serviço de Compras
// Cole este arquivo em: src/services/compraService.ts

import { AxiosResponse } from 'axios';
import api from './api';
import {
    CriarCompraData,
    CompraResponse,
    MeusTitulosResponse,
    PaginationParams,
    MessageResponse
} from '../types/api.types';

export const compraService = {
    /**
     * Cria uma nova compra de títulos
     * @param dados - Dados da compra
     * @returns Promise com compra criada
     */
    criarCompra: async (dados: CriarCompraData): Promise<AxiosResponse<CompraResponse>> => {
        return await api.post<CompraResponse>('/api/compras', dados);
    },

    /**
     * Lista títulos do usuário autenticado
     * @param params - Parâmetros de paginação
     * @returns Promise com lista de títulos
     */
    meusTitulos: async (params: PaginationParams = {}): Promise<AxiosResponse<MeusTitulosResponse>> => {
        const defaultParams: PaginationParams = {
            page: 1,
            per_page: 20,
            ...params,
        };
        return await api.get<MeusTitulosResponse>('/api/meus-titulos', { params: defaultParams });
    },

    /**
     * Deleta uma compra (admin only)
     * @param compraId - ID da compra
     * @returns Promise com mensagem e quantidade de títulos deletados
     */
    deletar: async (compraId: number): Promise<AxiosResponse<MessageResponse & { titulos_deletados: number }>> => {
        return await api.delete(`/api/compras/${compraId}`);
    },
};

export default compraService;
