import React, { useState } from 'react';
import { studentAPI } from '../../services/api';
import { Video, Upload, Trash2, AlertCircle, CheckCircle, Camera, X } from 'lucide-react';

const VideoManagement = () => {
    const [hasVideo, setHasVideo] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [selectedFile, setSelectedFile] = useState(null);

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            // Validate file type
            if (!file.type.startsWith('video/')) {
                setError('Please select a valid video file');
                return;
            }

            // Validate file size (max 50MB)
            if (file.size > 50 * 1024 * 1024) {
                setError('Video file must be less than 50MB');
                return;
            }

            setSelectedFile(file);
            setError('');
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            setError('Please select a video file');
            return;
        }

        setUploading(true);
        setError('');
        setSuccess('');

        try {
            await studentAPI.uploadVideo(selectedFile);
            setSuccess('Video uploaded successfully! Your face encodings have been generated.');
            setHasVideo(true);
            setSelectedFile(null);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to upload video');
        } finally {
            setUploading(false);
        }
    };

    const handleDelete = async () => {
        if (!window.confirm('Are you sure you want to delete your face recognition video? This will remove your attendance tracking.')) {
            return;
        }

        try {
            await studentAPI.deleteVideo();
            setSuccess('Video deleted successfully');
            setHasVideo(false);
            setSelectedFile(null);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to delete video');
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="page-title mb-2">Face Recognition Video</h2>
                <p className="page-subtitle">
                    Upload a video of your face for attendance tracking
                </p>
            </div>

            {/* Instructions */}
            <div className="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-emerald-900 dark:text-emerald-100 mb-3 flex items-center">
                    <Camera className="w-5 h-5 mr-2" />
                    Recording Guidelines
                </h3>
                <ul className="space-y-2 text-sm text-emerald-800 dark:text-emerald-200">
                    <li className="flex items-start">
                        <span className="mr-2">•</span>
                        <span>Record a 5-10 second video of your face</span>
                    </li>
                    <li className="flex items-start">
                        <span className="mr-2">•</span>
                        <span>Ensure good lighting and face the camera directly</span>
                    </li>
                    <li className="flex items-start">
                        <span className="mr-2">•</span>
                        <span>Slowly turn your head left and right during recording</span>
                    </li>
                    <li className="flex items-start">
                        <span className="mr-2">•</span>
                        <span>Keep a neutral expression and remove glasses if possible</span>
                    </li>
                    <li className="flex items-start">
                        <span className="mr-2">•</span>
                        <span>Maximum file size: 50MB</span>
                    </li>
                </ul>
            </div>

            {/* Error/Success Messages */}
            {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
                </div>
            )}

            {success && (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 flex items-start space-x-3">
                    <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-green-800 dark:text-green-200">{success}</p>
                </div>
            )}

            {/* Upload Section */}
            <div className="panel panel-body">
                {!selectedFile ? (
                    <div className="text-center">
                        <div className="upload-area p-12">
                            <Video className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                            <h3 className="text-lg font-medium mb-2">
                                Upload Face Recognition Video
                            </h3>
                            <p className="text-sm page-subtitle mb-4">
                                Select a video file from your device
                            </p>
                            <label className="btn btn-primary cursor-pointer">
                                <Upload className="w-5 h-5" />
                                <span>Choose Video</span>
                                <input
                                    type="file"
                                    accept="video/*"
                                    onChange={handleFileSelect}
                                    className="hidden"
                                />
                            </label>
                        </div>
                    </div>
                ) : (
                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 panel panel-muted rounded-lg">
                            <div className="flex items-center space-x-3">
                                <Video className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
                                <div>
                                    <p className="font-medium">{selectedFile.name}</p>
                                    <p className="text-sm page-subtitle">
                                        {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                                    </p>
                                </div>
                            </div>
                            <button
                                onClick={() => setSelectedFile(null)}
                                className="btn btn-ghost px-3"
                            >
                                <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                            </button>
                        </div>

                        <div className="flex space-x-3">
                            <button
                                onClick={handleUpload}
                                disabled={uploading}
                                className="btn btn-primary flex-1"
                            >
                                {uploading ? (
                                    <>
                                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                        <span>Uploading...</span>
                                    </>
                                ) : (
                                    <>
                                        <Upload className="w-5 h-5" />
                                        <span>Upload Video</span>
                                    </>
                                )}
                            </button>
                            <button
                                onClick={() => setSelectedFile(null)}
                                className="btn btn-secondary"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* Current Video Status */}
            {hasVideo && (
                <div className="panel panel-body">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="p-3 bg-emerald-100 dark:bg-emerald-900/20 rounded-lg">
                                <CheckCircle className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
                            </div>
                            <div>
                                <h3 className="font-medium">Video Active</h3>
                                <p className="text-sm page-subtitle">
                                    Your face recognition is set up and ready for attendance tracking
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={handleDelete}
                            className="btn btn-danger"
                        >
                            <Trash2 className="w-4 h-4" />
                            <span>Delete</span>
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default VideoManagement;
