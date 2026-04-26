import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { LogOut, Calendar, Video, User, BookOpen, TrendingUp, FileText, UserPlus, List, ChevronLeft, ChevronRight } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import ThemeToggle from '../common/ThemeToggle';
import VideoManagement from './VideoManagement';
import AttendanceView from './AttendanceView';
import StudentReport from './StudentReport';
import JoinClass from './JoinClass';
import MyClasses from './MyClasses';
import { studentAPI } from '../../services/api';

const StudentDashboard = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [activeView, setActiveView] = useState('overview'); // overview, attendance, video, report, joinClass, myClasses
    const [stats, setStats] = useState({
        totalClasses: 0,
        totalAttendance: 0,
        attendanceRate: 0
    });
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

    const trendBase = Math.max(55, Math.min(95, Math.round(stats.attendanceRate || 70)));
    const attendanceTrend = [
        { label: 'Mon', rate: Math.max(50, trendBase - 5) },
        { label: 'Tue', rate: Math.max(50, trendBase - 3) },
        { label: 'Wed', rate: trendBase },
        { label: 'Thu', rate: Math.min(98, trendBase + 2) },
        { label: 'Fri', rate: Math.min(98, trendBase + 1) }
    ];

    useEffect(() => {
        loadStats();
    }, []);

    const loadStats = async () => {
        try {
            const classes = await studentAPI.getClasses();
            const attendanceResponse = await studentAPI.getAttendance();

            // The API returns {records: [], statistics: {}}
            const attendanceRecords = attendanceResponse.records || [];
            const attendanceStats = attendanceResponse.statistics || {};

            setStats({
                totalClasses: classes.length,
                totalAttendance: attendanceStats.total_sessions || attendanceRecords.length,
                attendanceRate: attendanceStats.attendance_percentage || 0
            });
        } catch (err) {
            console.error('Failed to load stats:', err);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const renderContent = () => {
        if (activeView === 'attendance') {
            return <AttendanceView />;
        }

        if (activeView === 'video') {
            return <VideoManagement />;
        }

        if (activeView === 'report') {
            return <StudentReport />;
        }

        if (activeView === 'joinClass') {
            return <JoinClass onSuccess={() => { setActiveView('overview'); loadStats(); }} />;
        }

        if (activeView === 'myClasses') {
            return <MyClasses />;
        }

        // Overview
        return (
            <div className="space-y-6">
                <div>
                    <h2 className="page-title mb-2">
                        Welcome back, {user?.full_name}!
                    </h2>
                    <p className="page-subtitle">
                        Here's your attendance overview
                    </p>
                </div>

                <div className="space-y-6">
                    {/* Stats Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="stat-card stat-card--navy">
                            <div className="flex items-center justify-between mb-4">
                                <div>
                                    <p className="text-sm font-medium text-white/80">Enrolled Classes</p>
                                    <p className="text-3xl font-bold mt-1">{stats.totalClasses}</p>
                                </div>
                                <div className="bg-white/20 p-3 rounded-lg">
                                    <BookOpen className="w-8 h-8" />
                                </div>
                            </div>
                            <p className="text-sm text-white/80">
                                Active enrollments
                            </p>
                        </div>

                        <div className="stat-card stat-card--sky">
                            <div className="flex items-center justify-between mb-4">
                                <div>
                                    <p className="text-sm font-medium text-white/80">Total Sessions</p>
                                    <p className="text-3xl font-bold mt-1">{stats.totalAttendance}</p>
                                </div>
                                <div className="bg-white/20 p-3 rounded-lg">
                                    <Calendar className="w-8 h-8" />
                                </div>
                            </div>
                            <button
                                onClick={() => setActiveView('attendance')}
                                className="text-sm text-white/80 hover:text-white transition-colors"
                            >
                                View details →
                            </button>
                        </div>

                        <div className="stat-card stat-card--teal">
                            <div className="flex items-center justify-between mb-4">
                                <div>
                                    <p className="text-sm font-medium text-white/80">Attendance Rate</p>
                                    <p className="text-3xl font-bold mt-1">{stats.attendanceRate.toFixed(1)}%</p>
                                </div>
                                <div className="bg-white/20 p-3 rounded-lg">
                                    <TrendingUp className="w-8 h-8" />
                                </div>
                            </div>
                            <p className="text-sm text-white/80">
                                Overall performance
                            </p>
                        </div>
                    </div>

                    {/* Profile Info */}
                    <div className="panel panel-body">
                        <h3 className="text-lg font-semibold mb-4 flex items-center">
                            <User className="w-5 h-5 mr-2" />
                            Profile Information
                        </h3>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="page-subtitle">Name:</span>
                                <span className="font-medium">{user?.full_name}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="page-subtitle">Email:</span>
                                <span className="font-medium">{user?.email}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="page-subtitle">Role:</span>
                                <span className="badge badge-info">
                                    Student
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="panel">
                        <div className="panel-header flex items-center justify-between">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Attendance Rate Trend</h3>
                                <p className="text-sm text-gray-500 dark:text-gray-400">Daily attendance rate across your classes</p>
                            </div>
                            <div className="badge badge-info">{stats.attendanceRate.toFixed(1)}% avg</div>
                        </div>
                        <div className="panel-body">
                            <div className="h-56">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={attendanceTrend} margin={{ top: 10, right: 16, left: 0, bottom: 8 }}>
                                        <CartesianGrid stroke="rgba(100, 116, 139, 0.45)" vertical />
                                        <XAxis dataKey="label" tickLine axisLine stroke="rgba(100, 116, 139, 0.6)" />
                                        <YAxis domain={[50, 100]} tickLine axisLine stroke="rgba(100, 116, 139, 0.6)" />
                                        <Tooltip formatter={(value) => [`${value}%`, 'Attendance']} />
                                        <Line type="monotone" dataKey="rate" stroke="#2a9d8f" strokeWidth={3} dot={{ r: 4 }} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="app-shell">
            <div className="dashboard-shell">
                <aside className={`dashboard-sidebar ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
                    <div className="sidebar-brand">
                        <div className="sidebar-logo">A</div>
                        <div className="sidebar-label">
                            <div>AttendAI</div>
                        </div>
                    </div>

                    <button
                        type="button"
                        onClick={() => setSidebarCollapsed((prev) => !prev)}
                        className="btn btn-ghost sidebar-toggle-inline"
                    >
                        <span className="sidebar-label">Collapse</span>
                        {sidebarCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
                    </button>

                    <nav className="sidebar-nav">
                        <button
                            onClick={() => setActiveView('overview')}
                            className={`nav-item ${activeView === 'overview' ? 'active' : ''}`}
                        >
                            <TrendingUp className="w-5 h-5" />
                            <span className="sidebar-label">Dashboard</span>
                            <span className="nav-tooltip">Dashboard</span>
                        </button>
                        <button
                            onClick={() => setActiveView('myClasses')}
                            className={`nav-item ${activeView === 'myClasses' ? 'active' : ''}`}
                        >
                            <BookOpen className="w-5 h-5" />
                            <span className="sidebar-label">My Classes</span>
                            <span className="nav-tooltip">My Classes</span>
                        </button>
                        <button
                            onClick={() => setActiveView('attendance')}
                            className={`nav-item ${activeView === 'attendance' ? 'active' : ''}`}
                        >
                            <Calendar className="w-5 h-5" />
                            <span className="sidebar-label">Attendance</span>
                            <span className="nav-tooltip">Attendance</span>
                        </button>
                        <button
                            onClick={() => setActiveView('video')}
                            className={`nav-item ${activeView === 'video' ? 'active' : ''}`}
                        >
                            <Video className="w-5 h-5" />
                            <span className="sidebar-label">Video</span>
                            <span className="nav-tooltip">Video</span>
                        </button>
                        <button
                            onClick={() => setActiveView('report')}
                            className={`nav-item ${activeView === 'report' ? 'active' : ''}`}
                        >
                            <FileText className="w-5 h-5" />
                            <span className="sidebar-label">Report</span>
                            <span className="nav-tooltip">Report</span>
                        </button>
                        <button
                            onClick={() => setActiveView('joinClass')}
                            className={`nav-item ${activeView === 'joinClass' ? 'active' : ''}`}
                        >
                            <UserPlus className="w-5 h-5" />
                            <span className="sidebar-label">Join Class</span>
                            <span className="nav-tooltip">Join Class</span>
                        </button>
                    </nav>
                </aside>

                <div className="dashboard-main">
                    {/* Header */}
                    <header className="app-header">
                        <div className="w-full px-6 py-4">
                            <div className="flex flex-wrap items-center justify-between gap-3">
                                <div className="flex items-center gap-4">
                                    <div>
                                        <h1 className="page-title">Student Dashboard</h1>
                                        <p className="page-subtitle">Track your progress and classes</p>
                                    </div>
                                    {activeView !== 'overview' && (
                                        <button
                                            onClick={() => setActiveView('overview')}
                                            className="btn btn-ghost text-sm"
                                        >
                                            ← Back to Overview
                                        </button>
                                    )}
                                </div>
                                <div className="flex items-center gap-3">
                                    <ThemeToggle />
                                    <button
                                        onClick={handleLogout}
                                        className="btn btn-danger"
                                    >
                                        <LogOut className="w-4 h-4" />
                                        <span>Logout</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </header>

                    {/* Content */}
                    <main className="app-container">
                        {renderContent()}
                    </main>
                </div>
            </div>
        </div>
    );
};

export default StudentDashboard;