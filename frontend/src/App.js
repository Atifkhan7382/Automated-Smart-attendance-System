import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './components/auth/Login';
import TeacherRegister from './components/auth/TeacherRegister';
import StudentRegister from './components/auth/StudentRegister';
import TeacherDashboard from './components/teacher/TeacherDashboard';
import StudentDashboard from './components/student/StudentDashboard';

function AppRoutes() {
  const { isAuthenticated, isTeacher, isStudent } = useAuth();

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={
        isAuthenticated() ? (
          isTeacher() ? <Navigate to="/teacher/dashboard" /> : <Navigate to="/student/dashboard" />
        ) : (
          <Login />
        )
      } />
      <Route path="/register/teacher" element={<TeacherRegister />} />
      <Route path="/register/student" element={<StudentRegister />} />

      {/* Teacher Routes */}
      <Route path="/teacher/dashboard" element={
        <ProtectedRoute requiredRole="teacher">
          <TeacherDashboard />
        </ProtectedRoute>
      } />

      {/* Student Routes */}
      <Route path="/student/dashboard" element={
        <ProtectedRoute requiredRole="student">
          <StudentDashboard />
        </ProtectedRoute>
      } />

      {/* Default Route */}
      <Route path="/" element={
        isAuthenticated() ? (
          isTeacher() ? <Navigate to="/teacher/dashboard" /> : <Navigate to="/student/dashboard" />
        ) : (
          <Navigate to="/login" />
        )
      } />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;