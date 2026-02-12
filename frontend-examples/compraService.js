// Serviço de Compras
// Cole este arquivo em: src/services/compraService.js

import api from './api';

export const compraService = {
    /**
     * Cria uma nova compra de títulos
     * @param {Object} dados - {campanha_id, quantidade_titulos, metodo_pagamento}
     * @returns {Promise} Response com {mensagem, compra}
     */
    criarCompra: async (dados) => {
        return await api.post('/api/compras', dados);
    },

    /**
     * Lista títulos do usuário autenticado
     * @param {Object} params - {page, per_page}
     * @returns {Promise} Response com {compras, total, paginas, pagina_atual}
     */
    meusTitulos: async (params = {}) => {
        const defaultParams = {
            page: 1,
            per_page: 20,
            ...params,
        };
        return await api.get('/api/meus-titulos', { params: defaultParams });
    },

    /**
     * Deleta uma compra (admin only)
     * @param {number} compraId - ID da compra
     * @returns {Promise} Response com {mensagem, titulos_deletados}
     */
    deletar: async (compraId) => {
        return await api.delete(`/api/compras/${compraId}`);
    },
};

export default compraService;
