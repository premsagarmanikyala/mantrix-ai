import { useState, useEffect } from "react";
import axios from "axios";

interface User {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: localStorage.getItem("token"),
    isLoading: true,
    isAuthenticated: false,
  });

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      // Set axios default header
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;

      // Verify token and get user info
      axios
        .get("/api/auth/me")
        .then((response) => {
          setAuthState({
            user: response.data,
            token,
            isLoading: false,
            isAuthenticated: true,
          });
        })
        .catch(() => {
          // Token is invalid
          localStorage.removeItem("token");
          delete axios.defaults.headers.common["Authorization"];
          setAuthState({
            user: null,
            token: null,
            isLoading: false,
            isAuthenticated: false,
          });
        });
    } else {
      setAuthState((prev) => ({ ...prev, isLoading: false }));
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await axios.post("/api/auth/login", { email, password });
      const { access_token, user } = response.data;

      localStorage.setItem("token", access_token);
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;

      setAuthState({
        user,
        token: access_token,
        isLoading: false,
        isAuthenticated: true,
      });

      return true;
    } catch (error) {
      console.error("Login failed:", error);
      return false;
    }
  };

  const signup = async (email: string, password: string) => {
    try {
      const response = await axios.post("/api/auth/signup", {
        email,
        password,
      });
      const { access_token, user } = response.data;

      localStorage.setItem("token", access_token);
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;

      setAuthState({
        user,
        token: access_token,
        isLoading: false,
        isAuthenticated: true,
      });

      return true;
    } catch (error) {
      console.error("Signup failed:", error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    delete axios.defaults.headers.common["Authorization"];
    setAuthState({
      user: null,
      token: null,
      isLoading: false,
      isAuthenticated: false,
    });
  };

  return {
    ...authState,
    login,
    signup,
    logout,
  };
};
