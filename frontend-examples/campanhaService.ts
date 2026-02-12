// Serviço de Campanhas
// Cole este arquivo em: src/services/campanhaService.ts

import { AxiosResponse } from 'axios';
import api from './api';
import {
    Campanha,
    CampanhaListResponse,
    CampanhaParams,
    CriarCampanhaData,
    MessageResponse
} from '../types/api.types';

export const campanhaService = {
    /**
     * Lista campanhas com filtros e paginação
     * @param params - Parâmetros de filtro e paginação
     * @returns Promise com lista de campanhas
     */
    listar: async (params: CampanhaParams = {}): Promise<AxiosResponse<CampanhaListResponse>> => {
        const defaultParams: CampanhaParams = {
            status: 'ativo',
            page: 1,
            per_page: 20,
            ...params,
        };
        return await api.get<CampanhaListResponse>('/api/campanhas', { params: defaultParams });
    },

    /**
     * Obtém detalhes de uma campanha pelo slug
     * @param slug - Slug da campanha
     * @returns Promise com dados da campanha
     */
    obterDetalhes: async (slug: string): Promise<AxiosResponse<Campanha>> => {
        return await api.get<Campanha>(`/api/campanhas/${slug}`);
    },

    /**
     * Cria uma nova campanha (admin only)
     * @param dados - Dados da campanha
     * @returns Promise com campanha criada
     */
    criar: async (dados: CriarCampanhaData): Promise<AxiosResponse<{ mensagem: string; campanha: Campanha }>> => {
        return await api.post('/api/campanhas', dados);
    },

    /**
     * Deleta uma campanha (admin only)
     * @param campanhaId - ID da campanha
     * @returns Promise com mensagem de sucesso
     */
    deletar: async (campanhaId: number): Promise<AxiosResponse<MessageResponse>> => {
        return await api.delete<MessageResponse>(`/api/campanhas/${campanhaId}`);
    },

    /**
     * Filtra campanhas ativas
     * @returns Promise com campanhas ativas
     */
    listarAtivas: async (): Promise<AxiosResponse<CampanhaListResponse>> => {
        return await campanhaService.listar({ status: 'ativo' });
    },

    /**
     * Filtra campanhas concluídas
     * @returns Promise com campanhas concluídas
     */
    listarConcluidas: async (): Promise<AxiosResponse<CampanhaListResponse>> => {
        return await campanhaService.listar({ status: 'concluido' });
    },
};

export default campanhaService;
