// Serviço de Autenticação
// Cole este arquivo em: src/services/authService.js

import api from './api';

export const authService = {
    /**
     * Registra um novo usuário
     * @param {Object} dados - {nome, telefone, senha, email, cpf, cidade, estado}
     * @returns {Promise} Response com {mensagem, token, usuario}
     */
    registro: async (dados) => {
        const response = await api.post('/api/auth/registro', dados);
        // Salvar token no localStorage
        if (response.data.token) {
            localStorage.setItem('token', response.data.token);
        }
        return response;
    },

    /**
     * Realiza login do usuário
     * @param {string} telefone
     * @param {string} senha
     * @returns {Promise} Response com {mensagem, token, usuario}
     */
    login: async (telefone, senha) => {
        const response = await api.post('/api/auth/login', { telefone, senha });
        // Salvar token no localStorage
        if (response.data.token) {
            localStorage.setItem('token', response.data.token);
        }
        return response;
    },

    /**
     * Realiza logout do usuário
     * @returns {Promise}
     */
    logout: async () => {
        try {
            await api.post('/api/auth/logout');
        } finally {
            // Sempre remove o token, mesmo se a requisição falhar
            localStorage.removeItem('token');
        }
    },

    /**
     * Obtém perfil do usuário autenticado
     * @returns {Promise} Response com dados do usuário
     */
    obterPerfil: async () => {
        return await api.get('/api/auth/perfil');
    },

    /**
     * Atualiza perfil do usuário
     * @param {Object} dados - Campos a atualizar
     * @returns {Promise} Response com {mensagem, usuario}
     */
    atualizarPerfil: async (dados) => {
        return await api.put('/api/auth/perfil', dados);
    },

    /**
     * Inicia processo de recuperação de senha
     * @param {string} telefone
     * @returns {Promise}
     */
    recuperarSenha: async (telefone) => {
        return await api.post('/api/auth/recuperar-senha', { telefone });
    },

    /**
     * Verifica se usuário está autenticado
     * @returns {boolean}
     */
    isAuthenticated: () => {
        return !!localStorage.getItem('token');
    },

    /**
     * Obtém token do localStorage
     * @returns {string|null}
     */
    getToken: () => {
        return localStorage.getItem('token');
    },
};

export default authService;
