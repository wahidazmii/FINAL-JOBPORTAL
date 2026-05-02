import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { getMe, login as apiLogin, register as apiRegister } from "../lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchMe = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) { setLoading(false); return; }
    try {
      const { data } = await getMe();
      setUser(data.user);
      setProfile(data.profile || null);
      setCompany(data.company || null);
    } catch {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchMe(); }, [fetchMe]);

  const login = async (email, password) => {
    const { data } = await apiLogin({ email, password });
    localStorage.setItem("token", data.token);
    localStorage.setItem("user", JSON.stringify(data.user));
    setUser(data.user);
    await fetchMe();
    return data.user;
  };

  const register = async (payload) => {
    const { data } = await apiRegister(payload);
    localStorage.setItem("token", data.token);
    localStorage.setItem("user", JSON.stringify(data.user));
    setUser(data.user);
    await fetchMe();
    return data.user;
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    setProfile(null);
    setCompany(null);
  };

  const refreshMe = () => fetchMe();

  return (
    <AuthContext.Provider value={{ user, profile, company, loading, login, register, logout, refreshMe }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
