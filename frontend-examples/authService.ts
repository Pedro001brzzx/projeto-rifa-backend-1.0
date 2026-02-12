// Serviço de Autenticação
// Cole este arquivo em: src/services/authService.ts

import { AxiosResponse } from 'axios';
import api from './api';
import {
    RegistroData,
    LoginData,
    AuthResponse,
    Usuario,
    MessageResponse
} from '../types/api.types';

export const authService = {
    /**
     * Registra um novo usuário
     * @param dados - Dados do registro
     * @returns Promise com resposta de autenticação
     */
    registro: async (dados: RegistroData): Promise<AxiosResponse<AuthResponse>> => {
        const response = await api.post<AuthResponse>('/api/auth/registro', dados);
        // Salvar token no localStorage
        if (response.data.token) {
            localStorage.setItem('token', response.data.token);
        }
        return response;
    },

    /**
     * Realiza login do usuário
     * @param telefone - Telefone do usuário
     * @param senha - Senha do usuário
     * @returns Promise com resposta de autenticação
     */
    login: async (telefone: string, senha: string): Promise<AxiosResponse<AuthResponse>> => {
        const loginData: LoginData = { telefone, senha };
        const response = await api.post<AuthResponse>('/api/auth/login', loginData);
        // Salvar token no localStorage
        if (response.data.token) {
            localStorage.setItem('token', response.data.token);
        }
        return response;
    },

    /**
     * Realiza logout do usuário
     * @returns Promise void
     */
    logout: async (): Promise<void> => {
        try {
            await api.post<MessageResponse>('/api/auth/logout');
        } finally {
            // Sempre remove o token, mesmo se a requisição falhar
            localStorage.removeItem('token');
        }
    },

    /**
     * Obtém perfil do usuário autenticado
     * @returns Promise com dados do usuário
     */
    obterPerfil: async (): Promise<AxiosResponse<Usuario>> => {
        return await api.get<Usuario>('/api/auth/perfil');
    },

    /**
     * Atualiza perfil do usuário
     * @param dados - Campos a atualizar
     * @returns Promise com resposta contendo usuário atualizado
     */
    atualizarPerfil: async (dados: Partial<Usuario>): Promise<AxiosResponse<{ mensagem: string; usuario: Usuario }>> => {
        return await api.put('/api/auth/perfil', dados);
    },

    /**
     * Inicia processo de recuperação de senha
     * @param telefone - Telefone do usuário
     * @returns Promise com mensagem de resposta
     */
    recuperarSenha: async (telefone: string): Promise<AxiosResponse<MessageResponse>> => {
        return await api.post<MessageResponse>('/api/auth/recuperar-senha', { telefone });
    },

    /**
     * Verifica se usuário está autenticado
     * @returns boolean indicando se está autenticado
     */
    isAuthenticated: (): boolean => {
        return !!localStorage.getItem('token');
    },

    /**
     * Obtém token do localStorage
     * @returns Token JWT ou null
     */
    getToken: (): string | null => {
        return localStorage.getItem('token');
    },
};

export default authService;
