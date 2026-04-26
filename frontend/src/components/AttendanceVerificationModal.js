import React, { useState } from 'react';
import { X, CheckCircle, AlertCircle, HelpCircle } from 'lucide-react';

const AttendanceVerificationModal = ({ isOpen, onClose, verifications, attendanceId, onVerificationComplete }) => {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState(null);

    if (!isOpen || !verifications || verifications.length === 0) {
        return null;
    }

    const currentVerification = verifications[currentIndex];
    const isLastVerification = currentIndex === verifications.length - 1;

    // Debug logging
    console.log('Current verification:', currentVerification);
    console.log('Candidates:', currentVerification.candidates);

    const handleVerify = async (studentId, action) => {
        try {
            setSubmitting(true);
            setError(null);

            const formData = new FormData();
            formData.append('attendance_id', attendanceId);
            formData.append('face_index', currentVerification.face_index);
            formData.append('action', action);
            if (studentId) {
                formData.append('verified_student_id', studentId);
            }

            const response = await fetch('http://localhost:8000/api/verification/verify-attendance', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Failed to submit verification');
            }

            const result = await response.json();
            console.log('Verification result:', result);

            // Move to next verification or close
            if (isLastVerification) {
                onVerificationComplete();
                onClose();
            } else {
                setCurrentIndex(currentIndex + 1);
            }
        } catch (err) {
            console.error('Verification error:', err);
            setError(err.message || 'Failed to submit verification');
        } finally {
            setSubmitting(false);
        }
    };

    const handleSkip = () => {
        if (isLastVerification) {
            onClose();
        } else {
            setCurrentIndex(currentIndex + 1);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="panel max-w-3xl w-full max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="sticky top-0 bg-white dark:bg-gray-800 border-b dark:border-gray-700 p-4 flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-bold">Verify Face Match</h2>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            Face {currentIndex + 1} of {verifications.length}
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    >
                        <X className="h-6 w-6" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {error && (
                        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg p-4">
                            <p className="text-red-600 dark:text-red-400">{error}</p>
                        </div>
                    )}

                    {/* Face Crop */}
                    <div className="text-center">
                        <div className="inline-block bg-gray-100 dark:bg-gray-700 rounded-lg p-4">
                            {currentVerification.face_crop_base64 ? (
                                <img
                                    src={currentVerification.face_crop_base64}
                                    alt="Detected face"
                                    className="max-w-xs max-h-64 rounded-lg shadow-lg"
                                />
                            ) : (
                                <div className="w-64 h-64 flex items-center justify-center text-gray-400">
                                    <AlertCircle className="h-16 w-16" />
                                </div>
                            )}
                        </div>
                        <div className="mt-3">
                            <div className="badge badge-warning">
                                <AlertCircle className="h-4 w-4" />
                                Quality: {(currentVerification.quality_score * 100).toFixed(0)}%
                            </div>
                        </div>
                    </div>

                    {/* Candidates */}
                    <div>
                        <h3 className="text-lg font-semibold mb-4">
                            Who is this person?
                        </h3>
                        <div className="space-y-3">
                            {currentVerification.candidates && currentVerification.candidates.map((candidate, idx) => (
                                <button
                                    key={candidate.student_id}
                                    onClick={() => handleVerify(candidate.student_id, 'approve')}
                                    disabled={submitting}
                                    className={`w-full p-4 rounded-lg border-2 transition-all ${idx === 0
                                        ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20'
                                        : 'border-gray-200 dark:border-gray-700 hover:border-emerald-300 dark:hover:border-emerald-600'
                                        } ${submitting ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md'}`}
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="text-left">
                                            <p className="font-semibold">
                                                {candidate.name}
                                            </p>
                                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                                ID: {candidate.student_id}
                                            </p>
                                        </div>
                                        <div className="text-right">
                                            <div className="flex items-center gap-2">
                                                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                                    {(candidate.similarity * 100).toFixed(1)}% match
                                                </div>
                                                {idx === 0 && (
                                                    <span className="badge badge-info text-xs">
                                                        Best Match
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-3 pt-4 border-t dark:border-gray-700">
                        <button
                            onClick={() => handleVerify(null, 'unknown')}
                            disabled={submitting}
                            className="btn btn-secondary flex-1"
                        >
                            <HelpCircle className="h-5 w-5" />
                            Not Listed / Unknown
                        </button>
                        <button
                            onClick={handleSkip}
                            disabled={submitting}
                            className="btn btn-ghost"
                        >
                            Skip for Now
                        </button>
                    </div>

                    {/* Progress Indicator */}
                    <div className="flex gap-1">
                        {verifications.map((_, idx) => (
                            <div
                                key={idx}
                                className={`flex-1 h-1 rounded-full ${idx === currentIndex
                                    ? 'bg-blue-500'
                                    : idx < currentIndex
                                        ? 'bg-green-500'
                                        : 'bg-gray-200 dark:bg-gray-700'
                                    }`}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AttendanceVerificationModal;
