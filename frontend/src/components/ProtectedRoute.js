import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children, requiredRole }) => {
    const { user, loading, isAuthenticated } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">Loading...</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated()) {
        return <Navigate to="/login" replace />;
    }

    if (requiredRole && user?.role !== requiredRole) {
        // Redirect to appropriate dashboard based on actual role
        if (user?.role === 'teacher') {
            return <Navigate to="/teacher/dashboard" replace />;
        } else if (user?.role === 'student') {
            return <Navigate to="/student/dashboard" replace />;
        }
        return <Navigate to="/login" replace />;
    }

    return children;
};

export default ProtectedRoute;
