import React, { useState } from 'react';
import { UserPlus, BookOpen, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

const JoinClass = ({ onSuccess }) => {
    const [inviteCode, setInviteCode] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });

    const handleJoinClass = async (e) => {
        e.preventDefault();

        if (!inviteCode.trim()) {
            setMessage({ type: 'error', text: 'Please enter an invite code' });
            return;
        }

        try {
            setLoading(true);
            setMessage({ type: '', text: '' });

            const response = await axios.post('http://localhost:8000/api/student/join-class', {
                invite_code: inviteCode.trim()
            });

            setMessage({
                type: 'success',
                text: `Successfully joined ${response.data.class_name}!`
            });
            setInviteCode('');

            // Call onSuccess callback if provided
            if (onSuccess) {
                setTimeout(() => onSuccess(), 1500);
            }

            setLoading(false);
        } catch (error) {
            console.error('Error joining class:', error);
            setMessage({
                type: 'error',
                text: error.response?.data?.detail || 'Failed to join class. Please check the invite code.'
            });
            setLoading(false);
        }
    };

    return (
        <div className="w-full">
            <div className="panel panel-body border-0 panel-elevate">
                <div className="flex items-center gap-3 mb-6">
                    <UserPlus className="w-6 h-6 text-emerald-600" />
                    <h2 className="page-title">Join a Class</h2>
                </div>

                <div className="mb-6">
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                        Enter the invite code provided by your teacher to join a new class.
                        You can join multiple classes using the same profile.
                    </p>
                </div>

                <form onSubmit={handleJoinClass} className="space-y-4">
                    <div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Invite Code
                            </label>
                            <input
                                type="text"
                                value={inviteCode}
                                onChange={(e) => setInviteCode(e.target.value)}
                                placeholder="Enter 12-character invite code"
                                maxLength={12}
                                className="form-input text-lg tracking-wider uppercase"
                                disabled={loading}
                            />
                        </div>
                    </div>

                    {message.text && (
                        <div className={`p-4 rounded-lg flex items-center gap-2 ${message.type === 'success'
                            ? 'bg-green-50 text-green-800 border border-green-200'
                            : 'bg-red-50 text-red-800 border border-red-200'
                            }`}>
                            {message.type === 'success' ? (
                                <CheckCircle className="w-5 h-5" />
                            ) : (
                                <AlertCircle className="w-5 h-5" />
                            )}
                            <p>{message.text}</p>
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading || !inviteCode.trim()}
                        className="btn btn-primary w-full"
                    >
                        <BookOpen className="w-5 h-5" />
                        {loading ? 'Joining...' : 'Join Class'}
                    </button>
                </form>

                {/* Info Box */}
                <div className="mt-6 p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
                    <h3 className="font-semibold text-emerald-900 dark:text-emerald-300 mb-2">How It Works</h3>
                    <ul className="text-sm text-emerald-800 dark:text-emerald-400 space-y-1">
                        <li>• Your existing profile and face encodings will be used</li>
                        <li>• No need to upload videos again for each class</li>
                        <li>• You can join as many classes as you want</li>
                        <li>• Each class will track your attendance separately</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default JoinClass;
