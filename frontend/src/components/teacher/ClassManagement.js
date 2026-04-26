import React, { useState, useEffect } from 'react';
import { teacherAPI } from '../../services/api';
import { Plus, Users, Trash2, Link as LinkIcon, Copy, CheckCircle, AlertCircle, X } from 'lucide-react';

const ClassManagement = ({ onViewStudents }) => {
    const [classes, setClasses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [showInviteModal, setShowInviteModal] = useState(false);
    const [selectedClass, setSelectedClass] = useState(null);
    const [inviteLink, setInviteLink] = useState('');
    const [formData, setFormData] = useState({
        className: '',
        description: ''
    });

    useEffect(() => {
        loadClasses();
    }, []);

    const loadClasses = async () => {
        try {
            setLoading(true);
            const data = await teacherAPI.getClasses();
            setClasses(data);
            setError('');
        } catch (err) {
            setError('Failed to load classes');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateClass = async (e) => {
        e.preventDefault();
        try {
            await teacherAPI.createClass(formData.className, formData.description);
            setShowCreateModal(false);
            setFormData({ className: '', description: '' });
            loadClasses();
        } catch (err) {
            setError('Failed to create class');
            console.error(err);
        }
    };

    const handleDeleteClass = async (classId) => {
        if (!window.confirm('Are you sure you want to delete this class? This will remove all students from the class.')) {
            return;
        }

        try {
            await teacherAPI.deleteClass(classId);
            loadClasses();
        } catch (err) {
            setError('Failed to delete class');
            console.error(err);
        }
    };

    const generateInviteLink = async (classId, className) => {
        try {
            const response = await teacherAPI.generateInviteCode(classId);
            const inviteCode = response.invite_code;
            const inviteUrl = `${window.location.origin}/register/student?code=${inviteCode}`;

            setInviteLink({
                code: inviteCode,
                url: inviteUrl,
                className: className
            });
            setShowInviteModal(true);
        } catch (error) {
            console.error('Error generating invite:', error);
            alert('Failed to generate invite link');
        }
    };

    const copyInviteCode = (code) => {
        navigator.clipboard.writeText(code).then(() => {
            alert(`Invite code "${code}" copied to clipboard!`);
        }).catch(err => {
            console.error('Failed to copy:', err);
            alert('Failed to copy invite code');
        });
    };

    const copyInviteLink = () => {
        navigator.clipboard.writeText(inviteLink.url);
        alert('Invite link copied to clipboard!');
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
            <div className="flex flex-wrap justify-between items-center gap-3">
                <div>
                    <h2 className="page-title">Class Management</h2>
                    <p className="page-subtitle mt-1">Create and manage your classes</p>
                </div>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="btn btn-primary"
                >
                    <Plus className="w-5 h-5" />
                    <span>Create Class</span>
                </button>
            </div>

            {/* Error Message */}
            {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
                </div>
            )}

            {/* Classes Grid */}
            {classes.length === 0 ? (
                <div className="panel panel-body text-center py-12">
                    <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium mb-2">No classes yet</h3>
                    <p className="page-subtitle mb-4">Create your first class to get started</p>
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="btn btn-primary"
                    >
                        <Plus className="w-5 h-5" />
                        <span>Create Class</span>
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {classes.map((cls) => (
                        <div key={cls.id} className="panel panel-body hover:shadow-xl transition-shadow">
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex-1">
                                    <h3 className="text-xl font-bold mb-2">
                                        {cls.class_name}
                                    </h3>
                                    <p className="text-sm page-subtitle">
                                        Created {new Date(cls.created_at).toLocaleDateString()}
                                    </p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="badge badge-info">
                                        {cls.student_count || 0} students
                                    </span>
                                </div>
                            </div>

                            {/* Invite Code Section */}
                            <div className="mb-4 p-4 rounded-lg border border-emerald-200 dark:border-emerald-700 bg-emerald-50 dark:bg-emerald-900/20">
                                <div className="flex items-center justify-between">
                                    <div className="flex-1">
                                        <p className="text-xs font-semibold text-emerald-700 dark:text-emerald-300 uppercase tracking-wide mb-1">
                                            Invite Code
                                        </p>
                                        <p className="text-2xl font-mono font-bold text-emerald-900 dark:text-emerald-200 tracking-wider">
                                            {cls.invite_code}
                                        </p>
                                    </div>
                                    <button
                                        onClick={() => copyInviteCode(cls.invite_code)}
                                        className="btn btn-secondary"
                                        title="Copy invite code"
                                    >
                                        <Copy className="w-4 h-4" />
                                        Copy
                                    </button>
                                </div>
                                <p className="text-xs text-emerald-700 dark:text-emerald-300 mt-2">
                                    Share this code with students to join this class
                                </p>
                            </div>

                            <div className="flex gap-2">
                                <button
                                    onClick={() => onViewStudents && onViewStudents(cls)}
                                    className="btn btn-primary flex-1"
                                >
                                    <Users className="w-4 h-4" />
                                    View Students
                                </button>
                                <button
                                    onClick={() => handleDeleteClass(cls.id)}
                                    className="btn btn-danger px-4"
                                    title="Delete class"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Create Class Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="panel panel-body max-w-md w-full">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-xl font-semibold">Create New Class</h3>
                            <button
                                onClick={() => setShowCreateModal(false)}
                                className="text-gray-400 hover:text-gray-600"
                            >
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        <form onSubmit={handleCreateClass} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Class Name *
                                </label>
                                <input
                                    type="text"
                                    required
                                    value={formData.className}
                                    onChange={(e) => setFormData({ ...formData, className: e.target.value })}
                                    className="form-input"
                                    placeholder="e.g., Computer Science 101"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Description (Optional)
                                </label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    rows={3}
                                    className="form-textarea"
                                    placeholder="Brief description of the class"
                                />
                            </div>

                            <div className="flex space-x-3 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowCreateModal(false)}
                                    className="btn btn-secondary flex-1"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="btn btn-primary flex-1"
                                >
                                    Create Class
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Invite Link Modal */}
            {showInviteModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="panel panel-body max-w-lg w-full">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-xl font-semibold">Invite Students</h3>
                            <button
                                onClick={() => setShowInviteModal(false)}
                                className="text-gray-400 hover:text-gray-600"
                            >
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        <div className="mb-4">
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                                Share this link with students to join <strong>{selectedClass?.class_name}</strong>
                            </p>
                            <div className="flex items-center space-x-2">
                                <input
                                    type="text"
                                    readOnly
                                    value={inviteLink}
                                    className="form-input text-sm"
                                />
                                <button
                                    onClick={copyInviteLink}
                                    className="btn btn-primary"
                                >
                                    <LinkIcon className="w-4 h-4" />
                                    <span>Copy</span>
                                </button>
                            </div>
                        </div>

                        <div className="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <CheckCircle className="w-5 h-5 text-emerald-600 dark:text-emerald-400 flex-shrink-0 mt-0.5" />
                                <div className="text-sm text-emerald-800 dark:text-emerald-200">
                                    <p className="font-medium mb-1">Invite link generated successfully!</p>
                                    <p>This link will expire in 7 days. Students can use it to register and join your class.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ClassManagement;
