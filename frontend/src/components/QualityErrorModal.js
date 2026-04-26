import React from 'react';
import { X, AlertTriangle, Lightbulb, Info } from 'lucide-react';

/**
 * Quality Error Modal Component
 * Displays detailed quality validation errors from HTTP 422 responses
 */
const QualityErrorModal = ({ isOpen, onClose, errorData }) => {
    if (!isOpen || !errorData) return null;

    const {
        error = 'Image quality too low',
        message = '',
        quality_threshold = 0.7,
        issues = [],
        suggestions = []
    } = errorData;

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="flex items-center justify-center min-h-screen p-4">
                <div className="relative panel max-w-2xl w-full mx-auto">
                    {/* Header */}
                    <div className="flex items-center justify-between p-6 border-b dark:border-gray-700">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-full">
                                <AlertTriangle className="h-6 w-6 text-amber-700 dark:text-amber-300" />
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold">
                                    Image Quality Issue
                                </h3>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    {error}
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                        >
                            <X className="h-5 w-5" />
                        </button>
                    </div>

                    {/* Content */}
                    <div className="p-6 space-y-6">
                        {/* Message */}
                        {message && (
                            <div className="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-700 rounded-lg p-4">
                                <div className="flex gap-3">
                                    <Info className="h-5 w-5 text-emerald-600 dark:text-emerald-400 flex-shrink-0 mt-0.5" />
                                    <div>
                                        <p className="text-sm text-emerald-900 dark:text-emerald-200">
                                            {message}
                                        </p>
                                        <p className="text-xs text-emerald-700 dark:text-emerald-300 mt-1">
                                            Quality threshold: {(quality_threshold * 100).toFixed(0)}%
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Issues */}
                        {issues && issues.length > 0 && (
                            <div>
                                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                                    <AlertTriangle className="h-4 w-4 text-amber-700 dark:text-amber-300" />
                                    Detected Issues ({issues.length})
                                </h4>
                                <div className="space-y-2">
                                    {issues.map((issue, index) => (
                                        <div
                                            key={index}
                                            className="flex items-start gap-3 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-lg"
                                        >
                                            <div className="w-6 h-6 rounded-full bg-amber-200 dark:bg-amber-800 flex items-center justify-center flex-shrink-0">
                                                <span className="text-xs font-semibold text-amber-700 dark:text-amber-300">
                                                    {index + 1}
                                                </span>
                                            </div>
                                            <p className="text-sm text-amber-900 dark:text-amber-200 flex-1">
                                                {issue}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Suggestions */}
                        {suggestions && suggestions.length > 0 && (
                            <div>
                                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                                    <Lightbulb className="h-4 w-4 text-amber-600 dark:text-amber-400" />
                                    Improvement Suggestions
                                </h4>
                                <div className="space-y-2">
                                    {suggestions.map((suggestion, index) => (
                                        <div
                                            key={index}
                                            className="flex items-start gap-3 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-lg"
                                        >
                                            <div className="w-6 h-6 rounded-full bg-amber-200 dark:bg-amber-800 flex items-center justify-center flex-shrink-0">
                                                <Lightbulb className="h-3 w-3 text-amber-700 dark:text-amber-300" />
                                            </div>
                                            <p className="text-sm text-amber-900 dark:text-amber-200 flex-1">
                                                {suggestion}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Quality Tips */}
                        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                            <h5 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                                Quick Tips for Better Quality
                            </h5>
                            <ul className="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                                <li>• Ensure good, even lighting across the classroom</li>
                                <li>• Hold the camera steady or use a tripod</li>
                                <li>• Position camera to capture students' faces clearly</li>
                                <li>• Avoid backlighting (windows behind students)</li>
                                <li>• Make sure students are facing the camera</li>
                            </ul>
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="flex justify-end gap-3 p-6 border-t dark:border-gray-700 bg-gray-50 dark:bg-gray-750">
                        <button
                            onClick={onClose}
                            className="btn btn-primary"
                        >
                            Try Again
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default QualityErrorModal;
