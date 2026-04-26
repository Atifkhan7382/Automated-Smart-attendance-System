import React, { useState, useEffect } from 'react';
import { BookOpen, UserMinus, AlertCircle, RefreshCw } from 'lucide-react';
import axios from 'axios';

const MyClasses = () => {
    const [classes, setClasses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        loadClasses();
    }, []);

    const loadClasses = async () => {
        try {
            setLoading(true);
            const response = await axios.get('http://localhost:8000/api/student/classes');
            setClasses(response.data);
            setError('');
            setLoading(false);
        } catch (err) {
            console.error('Error loading classes:', err);
            setError('Failed to load classes');
            setLoading(false);
        }
    };

    const handleLeaveClass = async (classId, className) => {
        if (!window.confirm(`Are you sure you want to leave "${className}"? Your attendance records will be preserved.`)) {
            return;
        }

        try {
            await axios.delete(`http://localhost:8000/api/student/leave-class/${classId}`);
            alert(`Successfully left ${className}`);
            loadClasses(); // Refresh the list
        } catch (err) {
            console.error('Error leaving class:', err);
            alert(err.response?.data?.detail || 'Failed to leave class');
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            </div>
        );
    }

    return (
        <div className="w-full">
            <div className="panel panel-body">
            <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <BookOpen className="w-6 h-6 text-emerald-600" />
                        <h2 className="page-title">My Classes</h2>
                    </div>
                    <button
                        onClick={loadClasses}
                        className="btn btn-secondary"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Refresh
                    </button>
                </div>

                {error && (
                    <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-2">
                        <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
                        <p className="text-red-800 dark:text-red-200">{error}</p>
                    </div>
                )}

                <div className="mb-3">
                    <p className="page-subtitle">
                        You are enrolled in <span className="font-bold text-emerald-600 dark:text-emerald-400">{classes.length}</span> {classes.length === 1 ? 'class' : 'classes'}
                    </p>
                </div>

                {classes.length === 0 ? (
                    <div className="text-center py-10 panel panel-muted rounded-lg">
                        <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                        <p className="text-gray-500 dark:text-gray-400 mb-2">You haven't joined any classes yet</p>
                        <p className="text-sm text-gray-400 dark:text-gray-500">Use the "Join Class" button to enroll in a class</p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {classes.map((cls) => (
                            <div
                                key={cls.id}
                                className="panel panel-body border-0 hover:shadow-xl transition-shadow"
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <h3 className="text-xl font-bold mb-2">
                                            {cls.class_name}
                                        </h3>
                                        <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                                            <p>
                                                <span className="font-medium">Enrolled:</span>{' '}
                                                {new Date(cls.enrolled_at).toLocaleDateString('en-US', {
                                                    year: 'numeric',
                                                    month: 'long',
                                                    day: 'numeric'
                                                })}
                                            </p>
                                            {cls.teacher_name && (
                                                <p>
                                                    <span className="font-medium">Teacher:</span> {cls.teacher_name}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => handleLeaveClass(cls.id, cls.class_name)}
                                        className="btn btn-danger"
                                        title="Leave this class"
                                    >
                                        <UserMinus className="w-4 h-4" />
                                        Leave
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Info Box */}
                <div className="mt-4 p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
                    <h3 className="font-semibold text-emerald-900 dark:text-emerald-300 mb-2">Note</h3>
                    <ul className="text-sm text-emerald-800 dark:text-emerald-400 space-y-1">
                        <li>• Leaving a class will remove you from the enrollment list</li>
                        <li>• Your past attendance records will be preserved</li>
                        <li>• You can rejoin the class anytime using the invite code</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default MyClasses;
