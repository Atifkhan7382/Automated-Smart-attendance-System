import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { LogOut, Users, BookOpen, TrendingUp, BarChart3, Camera, Settings as SettingsIcon, Zap, ChevronLeft, ChevronRight } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import ThemeToggle from '../common/ThemeToggle';
import ClassManagement from './ClassManagement';
import ClassStudents from './ClassStudents';
import AttendanceMarking from '../AttendanceMarking';
import Settings from './Settings';
import Reports from './Reports';
import AutomatedAttendance from './AutomatedAttendance';
import { teacherAPI, statsAPI } from '../../services/api';

const TeacherDashboard = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [activeView, setActiveView] = useState('overview'); // overview, classes, students, attendance
    const [selectedClass, setSelectedClass] = useState(null);
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [stats, setStats] = useState({
        totalClasses: 0,
        totalStudents: 0,
        avgAttendance: 0
    });

    useEffect(() => {
        loadStats();
    }, []);

    const loadStats = async () => {
        try {
            const classes = await teacherAPI.getClasses();
            const totalClasses = classes.length;
            let totalStudents = 0;
            let totalAttendance = 0;

            for (const classItem of classes) {
                const students = await teacherAPI.getClassStudents(classItem.id);
                totalStudents += students.length;
                if (students.length > 0) {
                    totalAttendance += students.reduce((sum, s) => sum + s.attendance_percentage, 0) / students.length;
                }
            }

            setStats({
                totalClasses,
                totalStudents,
                avgAttendance: totalClasses > 0 ? totalAttendance / totalClasses : 0
            });
        } catch (err) {
            console.error('Failed to load stats:', err);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const handleViewStudents = (classItem) => {
        setSelectedClass(classItem);
        setActiveView('students');
    };

    const trendBase = Math.max(60, Math.min(95, Math.round(stats.avgAttendance || 75)));
    const attendanceTrend = [
        { label: 'Mon', rate: Math.max(55, trendBase - 6) },
        { label: 'Tue', rate: Math.max(58, trendBase - 3) },
        { label: 'Wed', rate: trendBase },
        { label: 'Thu', rate: Math.min(98, trendBase + 2) },
        { label: 'Fri', rate: Math.min(98, trendBase + 1) }
    ];

    const renderContent = () => {
        if (activeView === 'students' && selectedClass) {
            return (
                <ClassStudents
                    classId={selectedClass.id}
                    className={selectedClass.class_name}
                    onBack={() => {
                        setActiveView('classes');
                        setSelectedClass(null);
                        loadStats();
                    }}
                />
            );
        }

        if (activeView === 'classes') {
            return <ClassManagement onViewStudents={handleViewStudents} />;
        }

        if (activeView === 'attendance') {
            return <AttendanceMarking />;
        }

        if (activeView === 'settings') {
            return <Settings />;
        }

        if (activeView === 'reports') {
            return <Reports />;
        }

        if (activeView === 'automation') {
            return <AutomatedAttendance />;
        }

        // Overview
        return (
            <div className="space-y-6">
                <div>
                    <h2 className="page-title mb-2">
                        Welcome back, {user?.full_name}!
                    </h2>
                    <p className="page-subtitle">
                        Here's an overview of your classes and students
                    </p>
                </div>

                <div className="space-y-6">
                    {/* Stats Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="stat-card stat-card--navy">
                            <div className="flex items-center justify-between mb-4">
                                <div>
                                    <p className="text-sm font-medium text-white/80">Total Classes</p>
                                    <p className="text-3xl font-bold mt-1">{stats.totalClasses}</p>
                                </div>
                                <div className="bg-white/20 p-3 rounded-lg">
                                    <BookOpen className="w-8 h-8" />
                                </div>
                            </div>
                            <button
                                onClick={() => setActiveView('classes')}
                                className="text-sm text-white/80 hover:text-white transition-colors"
                            >
                                Manage classes →
                            </button>
                        </div>

                        <div className="stat-card stat-card--teal">
                            <div className="flex items-center justify-between mb-4">
                                <div>
                                    <p className="text-sm font-medium text-white/80">Total Students</p>
                                    <p className="text-3xl font-bold mt-1">{stats.totalStudents}</p>
                                </div>
                                <div className="bg-white/20 p-3 rounded-lg">
                                    <Users className="w-8 h-8" />
                                </div>
                            </div>
                            <p className="text-sm text-white/80">
                                Across all classes
                            </p>
                        </div>

                        <div className="stat-card stat-card--amber">
                            <div className="flex items-center justify-between mb-4">
                                <div>
                                    <p className="text-sm font-medium text-white/80">Avg. Attendance</p>
                                    <p className="text-3xl font-bold mt-1">{stats.avgAttendance.toFixed(1)}%</p>
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

                    <div className="panel">
                        <div className="panel-header flex items-center justify-between">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Overall Class Attendance Trend</h3>
                                <p className="text-sm text-gray-500 dark:text-gray-400">Daily attendance rate across all classes</p>
                            </div>
                            <div className="badge badge-info">{stats.avgAttendance.toFixed(1)}% avg</div>
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
                            onClick={() => setActiveView('classes')}
                            className={`nav-item ${activeView === 'classes' ? 'active' : ''}`}
                        >
                            <BookOpen className="w-5 h-5" />
                            <span className="sidebar-label">Classes</span>
                            <span className="nav-tooltip">Classes</span>
                        </button>
                        <button
                            onClick={() => setActiveView('attendance')}
                            className={`nav-item ${activeView === 'attendance' ? 'active' : ''}`}
                        >
                            <Camera className="w-5 h-5" />
                            <span className="sidebar-label">Manual Attendance</span>
                            <span className="nav-tooltip">Manual Attendance</span>
                        </button>
                        <button
                            onClick={() => setActiveView('reports')}
                            className={`nav-item ${activeView === 'reports' ? 'active' : ''}`}
                        >
                            <BarChart3 className="w-5 h-5" />
                            <span className="sidebar-label">Reports</span>
                            <span className="nav-tooltip">Reports</span>
                        </button>
                        <button
                            onClick={() => setActiveView('settings')}
                            className={`nav-item ${activeView === 'settings' ? 'active' : ''}`}
                        >
                            <SettingsIcon className="w-5 h-5" />
                            <span className="sidebar-label">Settings</span>
                            <span className="nav-tooltip">Settings</span>
                        </button>
                        <button
                            onClick={() => setActiveView('automation')}
                            className={`nav-item ${activeView === 'automation' ? 'active' : ''}`}
                        >
                            <Zap className="w-5 h-5" />
                            <span className="sidebar-label">Automation</span>
                            <span className="nav-tooltip">Automation</span>
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
                                        <h1 className="page-title">Teacher Dashboard</h1>
                                        <p className="page-subtitle">School attendance control center</p>
                                    </div>
                                    {activeView !== 'overview' && (
                                        <button
                                            onClick={() => {
                                                setActiveView('overview');
                                                setSelectedClass(null);
                                            }}
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

export default TeacherDashboard;