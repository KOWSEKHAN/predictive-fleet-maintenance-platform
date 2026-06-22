import React, { createContext, useState, useEffect } from 'react';
import { login, register } from '../services/auth';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const access = localStorage.getItem('access_token');
    const company = localStorage.getItem('company');
    const email = localStorage.getItem('email');
    if (access && company && email) {
      try {
        setUser({
          email,
          company: JSON.parse(company)
        });
      } catch (e) {
        console.error("Failed to restore auth state", e);
      }
    }
    setLoading(false);
  }, []);

  const loginUser = async (email, password) => {
    const data = await login(email, password);
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    localStorage.setItem('company', JSON.stringify(data.user.company));
    localStorage.setItem('email', data.user.email);
    setUser({
      email: data.user.email,
      company: data.user.company
    });
    return data;
  };

  const registerUser = async (companyName, email, password) => {
    const data = await register(companyName, email, password);
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    localStorage.setItem('company', JSON.stringify(data.user.company));
    localStorage.setItem('email', data.user.email);
    setUser({
      email: data.user.email,
      company: data.user.company
    });
    return data;
  };

  const logoutUser = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('company');
    localStorage.removeItem('email');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, isAuthenticated: !!user, loginUser, registerUser, logoutUser }}>
      {children}
    </AuthContext.Provider>
  );
};
