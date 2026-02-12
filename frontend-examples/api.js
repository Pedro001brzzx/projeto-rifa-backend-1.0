// Configuração base da API
// Cole este arquivo em: src/services/api.js

import axios from 'axios';

// URL base da API - pode ser configurada via variável de ambiente
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Criar instância do axios com configurações padrão
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000, // 10 segundos
});

// Interceptor de requisição - Adiciona token JWT automaticamente
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Interceptor de resposta - Trata erros globalmente
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // Token expirado ou inválido
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }

        // Acesso negado (não é admin)
        if (error.response?.status === 403) {
            console.error('Acesso negado:', error.response.data.erro);
        }

        return Promise.reject(error);
    }
);

export default api;
