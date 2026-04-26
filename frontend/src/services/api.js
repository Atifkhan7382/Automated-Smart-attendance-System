import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  registerTeacher: async (email, password, fullName) => {
    const response = await api.post('/auth/register/teacher', {
      email,
      password,
      full_name: fullName
    });
    return response.data;
  },

  registerStudent: async (email, password, fullName, studentId, inviteCode) => {
    const response = await api.post('/auth/register/student', {
      email,
      password,
      full_name: fullName,
      student_id: studentId,
      invite_code: inviteCode
    });
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  changePassword: async (currentPassword, newPassword) => {
    const response = await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  }
};

// Teacher API
export const teacherAPI = {
  // Class management
  getClasses: async () => {
    const response = await api.get('/teacher/classes');
    return response.data;
  },

  getClass: async (classId) => {
    const response = await api.get(`/teacher/classes/${classId}`);
    return response.data;
  },

  createClass: async (className, description) => {
    const response = await api.post('/teacher/classes', {
      class_name: className,
      description
    });
    return response.data;
  },

  updateClass: async (classId, className, description) => {
    const response = await api.put(`/teacher/classes/${classId}`, {
      class_name: className,
      description
    });
    return response.data;
  },

  deleteClass: async (classId) => {
    const response = await api.delete(`/teacher/classes/${classId}`);
    return response.data;
  },

  generateInviteLink: async (classId) => {
    const response = await api.post(`/teacher/classes/${classId}/invite`);
    return response.data;
  },

  getClassStudents: async (classId) => {
    const response = await api.get(`/teacher/classes/${classId}/students`);
    return response.data;
  },

  removeStudent: async (classId, studentId) => {
    const response = await api.delete(`/teacher/classes/${classId}/students/${studentId}`);
    return response.data;
  }
};

// Student API
export const studentAPI = {
  getProfile: async () => {
    const response = await api.get('/student/profile');
    return response.data;
  },

  updateProfile: async (fullName) => {
    const response = await api.put('/student/profile', { full_name: fullName });
    return response.data;
  },

  getClasses: async () => {
    const response = await api.get('/student/classes');
    return response.data;
  },

  getAttendance: async (classId, startDate, endDate) => {
    const params = {};
    if (classId) params.class_id = classId;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await api.get('/student/attendance', { params });
    return response.data;
  },

  uploadVideo: async (videoFile) => {
    const formData = new FormData();
    formData.append('file', videoFile);

    const response = await api.post('/student/video', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  deleteVideo: async () => {
    const response = await api.delete('/student/video');
    return response.data;
  },

  // Legacy student management (for backward compatibility)
  getStudents: async (className) => {
    const params = className ? { class_name: className } : {};
    const response = await api.get('/students/', { params });
    return response.data;
  },

  createStudent: async (studentData) => {
    const response = await api.post('/students/', studentData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  createStudentFromVideo: async (studentData) => {
    const response = await api.post('/students/video', studentData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  deleteStudent: async (studentId) => {
    const response = await api.delete(`/students/${studentId}`);
    return response.data;
  },
};

// Attendance API
export const attendanceAPI = {
  // Mark attendance with classroom image
  markAttendance: async (attendanceData) => {
    const response = await api.post('/attendance/mark', attendanceData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get attendance report
  getReport: async (params) => {
    const response = await api.get('/attendance/report', { params });
    return response.data;
  },

  // Export attendance data
  exportData: async (params) => {
    const response = await api.get('/attendance/export', { params });
    return response.data;
  },

  // Delete attendance record
  deleteAttendanceRecord: async (recordId) => {
    const response = await api.delete(`/attendance/${recordId}`);
    return response.data;
  },

  // Clear all attendance history
  clearAllHistory: async () => {
    const response = await api.delete('/attendance/clear-all');
    return response.data;
  },

  // Get session attendance report
  getSessionReport: async (attendanceId) => {
    const response = await api.get(`/attendance/session/${attendanceId}`);
    return response.data;
  },

  // Export session attendance to Excel
  exportSessionAttendance: async (attendanceId) => {
    const response = await api.get(`/attendance/session/${attendanceId}/export`);
    return response.data;
  },
};

// Statistics API
export const statsAPI = {
  // Get system statistics
  getStatistics: async () => {
    const response = await api.get('/stats');
    return response.data;
  },
};

// Model & System API
export const modelAPI = {
  // Get model status
  getModelStatus: async () => {
    const response = await api.get('/model/status');
    return response.data;
  },

  // Get GPU status
  getGPUStatus: async () => {
    const response = await api.get('/gpu-status');
    return response.data;
  },
};

// Automated Attendance API
export const automationAPI = {
  // Get automation settings
  getSettings: async () => {
    const response = await api.get('/automation/settings');
    return response.data;
  },

  // Update automation settings
  updateSettings: async (settings) => {
    const response = await api.post('/automation/settings', settings);
    return response.data;
  },

  // Get automation status
  getStatus: async () => {
    const response = await api.get('/automation/status');
    return response.data;
  },

  // Start automated attendance
  start: async (className, schedule) => {
    const response = await api.post('/automation/start', { class_name: className, schedule });
    return response.data;
  },

  // Stop automated attendance
  stop: async () => {
    const response = await api.post('/automation/stop');
    return response.data;
  },

  // Get automation logs
  getLogs: async (limit = 50) => {
    const response = await api.get('/automation/logs', { params: { limit } });
    return response.data;
  },
};

// Health check
export const healthAPI = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

// Legacy export for backward compatibility
export const getModelStatus = modelAPI.getModelStatus;

export default api;
