// Context de Autenticação
// Cole este arquivo em: src/contexts/AuthContext.jsx

import React, { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [authenticated, setAuthenticated] = useState(false);

    // Carregar perfil do usuário ao iniciar
    useEffect(() => {
        const loadUserProfile = async () => {
            const token = authService.getToken();

            if (token) {
                try {
                    const response = await authService.obterPerfil();
                    setUser(response.data);
                    setAuthenticated(true);
                } catch (error) {
                    console.error('Erro ao carregar perfil:', error);
                    authService.logout();
                }
            }

            setLoading(false);
        };

        loadUserProfile();
    }, []);

    const login = async (telefone, senha) => {
        try {
            const response = await authService.login(telefone, senha);
            setUser(response.data.usuario);
            setAuthenticated(true);
            return response.data;
        } catch (error) {
            setAuthenticated(false);
            throw error;
        }
    };

    const register = async (dados) => {
        try {
            const response = await authService.registro(dados);
            setUser(response.data.usuario);
            setAuthenticated(true);
            return response.data;
        } catch (error) {
            setAuthenticated(false);
            throw error;
        }
    };

    const logout = async () => {
        try {
            await authService.logout();
        } finally {
            setUser(null);
            setAuthenticated(false);
        }
    };

    const updateProfile = async (dados) => {
        try {
            const response = await authService.atualizarPerfil(dados);
            setUser(response.data.usuario);
            return response.data;
        } catch (error) {
            throw error;
        }
    };

    const value = {
        user,
        loading,
        authenticated,
        login,
        register,
        logout,
        updateProfile,
        isAdmin: user?.is_admin || false,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
