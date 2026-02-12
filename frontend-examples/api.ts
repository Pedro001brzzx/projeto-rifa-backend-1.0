// Configuração base da API
// Cole este arquivo em: src/services/api.ts

import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from 'axios';

// URL base da API - pode ser configurada via variável de ambiente
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Criar instância do axios com configurações padrão
const api: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000, // 10 segundos
});

// Interceptor de requisição - Adiciona token JWT automaticamente
api.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('token');
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error: AxiosError) => {
        return Promise.reject(error);
    }
);

// Interceptor de resposta - Trata erros globalmente
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error: AxiosError) => {
        // Token expirado ou inválido
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }

        // Acesso negado (não é admin)
        if (error.response?.status === 403) {
            console.error('Acesso negado:', error.response.data);
        }

        return Promise.reject(error);
    }
);

export default api;
