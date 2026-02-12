// Serviço de Campanhas
// Cole este arquivo em: src/services/campanhaService.js

import api from './api';

export const campanhaService = {
    /**
     * Lista campanhas com filtros e paginação
     * @param {Object} params - {status, page, per_page}
     * @returns {Promise} Response com {campanhas, total, paginas, pagina_atual}
     */
    listar: async (params = {}) => {
        const defaultParams = {
            status: 'ativo',
            page: 1,
            per_page: 20,
            ...params,
        };
        return await api.get('/api/campanhas', { params: defaultParams });
    },

    /**
     * Obtém detalhes de uma campanha pelo slug
     * @param {string} slug - Slug da campanha
     * @returns {Promise} Response com dados da campanha
     */
    obterDetalhes: async (slug) => {
        return await api.get(`/api/campanhas/${slug}`);
    },

    /**
     * Cria uma nova campanha (admin only)
     * @param {Object} dados - Dados da campanha
     * @returns {Promise} Response com {mensagem, campanha}
     */
    criar: async (dados) => {
        return await api.post('/api/campanhas', dados);
    },

    /**
     * Deleta uma campanha (admin only)
     * @param {number} campanhaId - ID da campanha
     * @returns {Promise} Response com {mensagem}
     */
    deletar: async (campanhaId) => {
        return await api.delete(`/api/campanhas/${campanhaId}`);
    },

    /**
     * Filtra campanhas ativas
     * @returns {Promise} Response com campanhas ativas
     */
    listarAtivas: async () => {
        return await campanhaService.listar({ status: 'ativo' });
    },

    /**
     * Filtra campanhas concluídas
     * @returns {Promise} Response com campanhas concluídas
     */
    listarConcluidas: async () => {
        return await campanhaService.listar({ status: 'concluido' });
    },
};

export default campanhaService;
