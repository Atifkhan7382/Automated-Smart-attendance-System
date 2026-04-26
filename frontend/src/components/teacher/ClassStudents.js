import React, { useState, useEffect } from 'react';
import { teacherAPI } from '../../services/api';
import { Users, Mail, Calendar, TrendingUp, Trash2, AlertCircle, ArrowLeft } from 'lucide-react';

const ClassStudents = ({ classId, className, onBack }) => {
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        loadStudents();
    }, [classId]);

    const loadStudents = async () => {
        try {
            setLoading(true);
            const data = await teacherAPI.getClassStudents(classId);
            setStudents(data);
            setError('');
        } catch (err) {
            setError('Failed to load students');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleRemoveStudent = async (studentId) => {
        if (!window.confirm('Are you sure you want to remove this student from the class?')) {
            return;
        }

        try {
            await teacherAPI.removeStudent(classId, studentId);
            loadStudents();
        } catch (err) {
            setError('Failed to remove student');
            console.error(err);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center space-x-4">
                <button
                    onClick={onBack}
                    className="btn btn-ghost px-3"
                >
                    <ArrowLeft className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                </button>
                <div>
                    <h2 className="page-title">{className}</h2>
                    <p className="page-subtitle mt-1">
                        {students.length} {students.length === 1 ? 'student' : 'students'} enrolled
                    </p>
                </div>
            </div>

            {/* Error Message */}
            {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
                </div>
            )}

            {/* Students List */}
            {students.length === 0 ? (
                <div className="panel panel-body text-center py-12">
                    <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium mb-2">No students yet</h3>
                    <p className="page-subtitle">
                        Share the invite link to add students to this class
                    </p>
                </div>
            ) : (
                <div className="table-wrap">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="table-head">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Student
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Email
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Enrolled
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Attendance
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                                {students.map((student) => (
                                    <tr key={student.student_id} className="table-row">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <div className="flex-shrink-0 h-10 w-10 bg-emerald-100 dark:bg-emerald-900/20 rounded-full flex items-center justify-center">
                                                    <span className="text-emerald-600 dark:text-emerald-400 font-medium">
                                                        {student.student_name.charAt(0).toUpperCase()}
                                                    </span>
                                                </div>
                                                <div className="ml-4">
                                                    <div className="text-sm font-medium">
                                                        {student.student_name}
                                                    </div>
                                                    <div className="text-sm text-gray-500 dark:text-gray-400">
                                                        {student.student_number || 'N/A'}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                                                <Mail className="w-4 h-4 mr-2" />
                                                {student.student_email}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                                                <Calendar className="w-4 h-4 mr-2" />
                                                {new Date(student.enrolled_at).toLocaleDateString()}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <TrendingUp className="w-4 h-4 mr-2 text-green-600 dark:text-green-400" />
                                                <span className={`text-sm font-medium ${student.attendance_percentage >= 75
                                                        ? 'text-green-600 dark:text-green-400'
                                                        : student.attendance_percentage >= 50
                                                            ? 'text-yellow-600 dark:text-yellow-400'
                                                            : 'text-red-600 dark:text-red-400'
                                                    }`}>
                                                    {student.attendance_percentage.toFixed(1)}%
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <button
                                                onClick={() => handleRemoveStudent(student.student_id)}
                                                className="text-red-600 hover:text-red-800 inline-flex items-center space-x-1"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                                <span>Remove</span>
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Summary Stats */}
            {students.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="panel panel-body">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-emerald-700 dark:text-emerald-300 font-medium">Total Students</p>
                                <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-300 mt-1">{students.length}</p>
                            </div>
                            <Users className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
                        </div>
                    </div>

                    <div className="panel panel-body">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-emerald-700 dark:text-emerald-300 font-medium">Avg. Attendance</p>
                                <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-300 mt-1">
                                    {students.length > 0
                                        ? (students.reduce((sum, s) => sum + s.attendance_percentage, 0) / students.length).toFixed(1)
                                        : 0}%
                                </p>
                            </div>
                            <TrendingUp className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
                        </div>
                    </div>

                    <div className="panel panel-body">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-emerald-700 dark:text-emerald-300 font-medium">Active Students</p>
                                <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-300 mt-1">
                                    {students.filter(s => s.attendance_percentage > 0).length}
                                </p>
                            </div>
                            <Users className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ClassStudents;
