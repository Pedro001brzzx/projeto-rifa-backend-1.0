// Context de Autenticação
// Cole este arquivo em: src/contexts/AuthContext.tsx

import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { authService } from '../services/authService';
import { Usuario, RegistroData } from '../types/api.types';

interface AuthContextType {
    user: Usuario | null;
    loading: boolean;
    authenticated: boolean;
    login: (telefone: string, senha: string) => Promise<any>;
    register: (dados: RegistroData) => Promise<any>;
    logout: () => Promise<void>;
    updateProfile: (dados: Partial<Usuario>) => Promise<any>;
    isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<Usuario | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [authenticated, setAuthenticated] = useState<boolean>(false);

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
                    await authService.logout();
                }
            }

            setLoading(false);
        };

        loadUserProfile();
    }, []);

    const login = async (telefone: string, senha: string) => {
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

    const register = async (dados: RegistroData) => {
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

    const updateProfile = async (dados: Partial<Usuario>) => {
        try {
            const response = await authService.atualizarPerfil(dados);
            setUser(response.data.usuario);
            return response.data;
        } catch (error) {
            throw error;
        }
    };

    const value: AuthContextType = {
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
