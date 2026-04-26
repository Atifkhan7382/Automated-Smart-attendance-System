import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    // Configure axios defaults
    useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            // Fetch user info
            fetchUserInfo();
        } else {
            setLoading(false);
        }
    }, [token]);

    const fetchUserInfo = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/auth/me`);
            setUser(response.data);
        } catch (error) {
            console.error('Failed to fetch user info:', error);
            // Token might be invalid, clear it
            logout();
        } finally {
            setLoading(false);
        }
    };

    const login = async (email, password) => {
        try {
            const response = await axios.post(`${API_BASE_URL}/auth/login`, {
                email,
                password
            });

            const { access_token, user: userData } = response.data;

            // Store token
            localStorage.setItem('token', access_token);
            setToken(access_token);
            setUser(userData);

            // Set axios default header
            axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

            return { success: true, user: userData };
        } catch (error) {
            const message = error.response?.data?.detail || 'Login failed';
            return { success: false, error: message };
        }
    };

    const registerTeacher = async (email, password, fullName) => {
        try {
            const response = await axios.post(`${API_BASE_URL}/auth/register/teacher`, {
                email,
                password,
                full_name: fullName
            });

            return { success: true, user: response.data };
        } catch (error) {
            const message = error.response?.data?.detail || 'Registration failed';
            return { success: false, error: message };
        }
    };

    const registerStudent = async (email, password, fullName, studentId, inviteCode) => {
        try {
            const response = await axios.post(`${API_BASE_URL}/auth/register/student`, {
                email,
                password,
                full_name: fullName,
                student_id: studentId,
                invite_code: inviteCode
            });

            return { success: true, user: response.data };
        } catch (error) {
            const message = error.response?.data?.detail || 'Registration failed';
            return { success: false, error: message };
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
        delete axios.defaults.headers.common['Authorization'];
    };

    const isAuthenticated = () => {
        return !!token && !!user;
    };

    const isTeacher = () => {
        return user?.role === 'teacher';
    };

    const isStudent = () => {
        return user?.role === 'student';
    };

    const value = {
        user,
        token,
        loading,
        login,
        logout,
        registerTeacher,
        registerStudent,
        isAuthenticated,
        isTeacher,
        isStudent
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export default AuthContext;
