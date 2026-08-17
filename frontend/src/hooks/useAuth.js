import { useState, useEffect, useCallback } from 'react';
import { login as loginApi, getMe } from '../api/auth';

const TOKEN_KEY = 'policypilot_token';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadUser = useCallback(async (currentToken) => {
    try {
      if (currentToken) {
        const userData = await getMe(currentToken);
        setUser(userData);
        setToken(currentToken);
      } else {
        setUser(null);
        setToken(null);
      }
    } catch (error) {
      console.error('Failed to load user:', error);
      localStorage.removeItem(TOKEN_KEY);
      setUser(null);
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    loadUser(storedToken);
  }, [loadUser]);

  const login = async (email, name) => {
    setIsLoading(true);
    try {
      const data = await loginApi(email, name);
      localStorage.setItem(TOKEN_KEY, data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  };

  return {
    user,
    token,
    isLoading,
    login,
    logout,
  };
}
