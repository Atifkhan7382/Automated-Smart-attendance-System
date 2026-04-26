import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { UserPlus, Mail, Lock, User, AlertCircle, CheckCircle, Camera, Hash } from 'lucide-react';

const StudentRegister = () => {
    const [searchParams] = useSearchParams();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        fullName: '',
        studentId: '',
        inviteCode: searchParams.get('invite') || ''
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false);

    const { registerStudent } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Validation
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters long');
            return;
        }

        // Invite code is now optional - students can register independently

        setLoading(true);

        const result = await registerStudent(
            formData.email,
            formData.password,
            formData.fullName,
            formData.studentId,
            formData.inviteCode
        );

        if (result.success) {
            setSuccess(true);
            setTimeout(() => {
                navigate('/login');
            }, 2000);
        } else {
            setError(result.error);
        }

        setLoading(false);
    };

    return (
        <div className="auth-shell">
            <div className="max-w-md w-full">
                {/* Logo and Title */}
                <div className="text-center mb-8">
                    <div className="auth-brand mb-4">
                        <Camera className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                        Student Registration
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400">
                        Create your account and join classes later
                    </p>
                </div>

                {/* Registration Form */}
                <div className="auth-card">
                    {success ? (
                        <div className="text-center py-8">
                            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full mb-4">
                                <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                                Registration Successful!
                            </h3>
                            <p className="text-gray-600 dark:text-gray-400 mb-4">
                                You can now login and upload your face recognition video
                            </p>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className="space-y-5">
                            {/* Error Message */}
                            {error && (
                                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start space-x-3">
                                    <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                                    <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
                                </div>
                            )}

                            {/* Invite Code */}
                            <div>
                                <label htmlFor="inviteCode" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Invite Code <span className="text-gray-500 text-xs">(Optional)</span>
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Hash className="h-5 w-5 text-gray-400" />
                                    </div>
                                    <input
                                        id="inviteCode"
                                        name="inviteCode"
                                        type="text"
                                        // Not required anymore
                                        value={formData.inviteCode}
                                        onChange={handleChange}
                                        className="form-input pl-10"
                                        placeholder="Enter invite code (optional) or leave blank to join classes later"
                                    />
                                </div>
                            </div>

                            {/* Student ID */}
                            <div>
                                <label htmlFor="studentId" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Student ID
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Hash className="h-5 w-5 text-gray-400" />
                                    </div>
                                    <input
                                        id="studentId"
                                        name="studentId"
                                        type="text"
                                        required
                                        value={formData.studentId}
                                        onChange={handleChange}
                                        className="form-input pl-10"
                                        placeholder="STU12345"
                                    />
                                </div>
                            </div>

                            {/* Full Name */}
                            <div>
                                <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Full Name
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <User className="h-5 w-5 text-gray-400" />
                                    </div>
                                    <input
                                        id="fullName"
                                        name="fullName"
                                        type="text"
                                        required
                                        value={formData.fullName}
                                        onChange={handleChange}
                                        className="form-input pl-10"
                                        placeholder="John Doe"
                                    />
                                </div>
                            </div>

                            {/* Email */}
                            <div>
                                <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Email Address
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Mail className="h-5 w-5 text-gray-400" />
                                    </div>
                                    <input
                                        id="email"
                                        name="email"
                                        type="email"
                                        required
                                        value={formData.email}
                                        onChange={handleChange}
                                        className="form-input pl-10"
                                        placeholder="student@example.com"
                                    />
                                </div>
                            </div>

                            {/* Password */}
                            <div>
                                <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Password
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Lock className="h-5 w-5 text-gray-400" />
                                    </div>
                                    <input
                                        id="password"
                                        name="password"
                                        type="password"
                                        required
                                        value={formData.password}
                                        onChange={handleChange}
                                        className="form-input pl-10"
                                        placeholder="••••••••"
                                    />
                                </div>
                            </div>

                            {/* Confirm Password */}
                            <div>
                                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Confirm Password
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Lock className="h-5 w-5 text-gray-400" />
                                    </div>
                                    <input
                                        id="confirmPassword"
                                        name="confirmPassword"
                                        type="password"
                                        required
                                        value={formData.confirmPassword}
                                        onChange={handleChange}
                                        className="form-input pl-10"
                                        placeholder="••••••••"
                                    />
                                </div>
                            </div>

                            {/* Submit Button */}
                            <button
                                type="submit"
                                disabled={loading}
                                className="btn btn-primary w-full"
                            >
                                {loading ? (
                                    <>
                                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                        <span>Creating Account...</span>
                                    </>
                                ) : (
                                    <>
                                        <UserPlus className="w-5 w-5" />
                                        <span>Create Student Account</span>
                                    </>
                                )}
                            </button>
                        </form>
                    )}

                    {/* Login Link */}
                    {!success && (
                        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700 text-center">
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Already have an account?{' '}
                                <Link to="/login" className="text-emerald-700 dark:text-emerald-300 hover:underline font-medium">
                                    Sign in
                                </Link>
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default StudentRegister;
