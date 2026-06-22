const API_URL = 'http://localhost:8000/api';

export const login = async (email, password) => {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }
  return response.json();
};

export const register = async (companyName, email, password) => {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ company_name: companyName, email, password }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.email ? error.email[0] : 'Registration failed');
  }
  return response.json();
};
