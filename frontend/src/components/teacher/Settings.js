import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Save, RotateCcw, AlertCircle, CheckCircle } from 'lucide-react';
import axios from 'axios';

const Settings = () => {
    const [settings, setSettings] = useState({
        fpsExtraction: 2,
        similarityThreshold: 0.25,
        detectionConfidence: 0.25,
        useGPU: false
    });
    const [rebuildStudentId, setRebuildStudentId] = useState('');
    const [rebuildStatus, setRebuildStatus] = useState({
        status: 'idle',
        current: 0,
        total: 0,
        message: '',
        last_error: null,
        success_count: 0,
        failed_count: 0,
        current_student: null
    });

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });

    useEffect(() => {
        loadSettings();
        fetchRebuildStatus();
    }, []);

    useEffect(() => {
        if (rebuildStatus.status !== 'running') {
            return undefined;
        }

        const interval = setInterval(fetchRebuildStatus, 2000);
        return () => clearInterval(interval);
    }, [rebuildStatus.status]);

    const loadSettings = async () => {
        try {
            setLoading(true);
            const response = await axios.get('http://localhost:8000/api/settings');
            setSettings(response.data);
            setLoading(false);
        } catch (error) {
            console.error('Error loading settings:', error);
            setLoading(false);
            setMessage({ type: 'error', text: 'Failed to load settings. Using defaults.' });
        }
    };

    const handleSave = async () => {
        try {
            setSaving(true);
            setMessage({ type: '', text: '' });

            await axios.post('http://localhost:8000/api/settings', settings);

            setMessage({ type: 'success', text: 'Settings saved successfully!' });
            setSaving(false);

            setTimeout(() => setMessage({ type: '', text: '' }), 3000);
        } catch (error) {
            console.error('Error saving settings:', error);
            setMessage({ type: 'error', text: 'Failed to save settings.' });
            setSaving(false);
        }
    };

    const fetchRebuildStatus = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/settings/rebuild-encodings/status');
            setRebuildStatus(response.data || { status: 'idle' });
        } catch (error) {
            console.error('Error fetching rebuild status:', error);
        }
    };

    const handleRebuildEncodings = async () => {
        try {
            setMessage({ type: '', text: '' });
            const payload = rebuildStudentId.trim() ? { student_id: rebuildStudentId.trim() } : {};
            await axios.post('http://localhost:8000/api/settings/rebuild-encodings', payload);
            await fetchRebuildStatus();
        } catch (error) {
            console.error('Error starting rebuild:', error);
            setMessage({ type: 'error', text: 'Failed to start rebuild.' });
        }
    };

    const handleReset = () => {
        setSettings({
            fpsExtraction: 2,
            similarityThreshold: 0.25,
            detectionConfidence: 0.25,
            useGPU: false
        });
        setMessage({ type: 'info', text: 'Settings reset to defaults.' });
    };

    const handleChange = (field, value) => {
        setSettings(prev => ({
            ...prev,
            [field]: value
        }));
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-gray-500 dark:text-gray-400">Loading settings...</div>
            </div>
        );
    }

    return (
        <div className="w-full">
            <div className="panel panel-body border-0 panel-elevate">
                <div className="flex items-center gap-3 mb-4">
                    <SettingsIcon className="w-6 h-6 text-emerald-600" />
                    <h2 className="page-title">Face Recognition Settings</h2>
                </div>

                {message.text && (
                        <div className={`mb-4 p-4 rounded-lg flex items-center gap-2 ${message.type === 'success' ? 'bg-green-50 text-green-800 dark:bg-green-900/30 dark:text-green-200' :
                            message.type === 'error' ? 'bg-red-50 text-red-800 dark:bg-red-900/30 dark:text-red-200' :
                            'bg-blue-50 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200'
                        }`}>
                        {message.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                        {message.text}
                    </div>
                )}

                <div className="space-y-4">
                    {/* FPS Extraction */}
                    <div className="border-b border-gray-200 dark:border-gray-700 pb-5">
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                            Frame Extraction Rate (FPS)
                        </label>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                            Number of frames to extract per second from student videos. Higher values = more training data but slower processing.
                        </p>
                        <div className="flex items-center gap-4">
                            <input
                                type="range"
                                min="1"
                                max="5"
                                step="1"
                                value={settings.fpsExtraction}
                                onChange={(e) => handleChange('fpsExtraction', parseInt(e.target.value))}
                                className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
                                style={{
                                    background: `linear-gradient(90deg, #2a9d8f ${((settings.fpsExtraction - 1) / 4) * 100}%, rgba(148,163,184,0.4) ${((settings.fpsExtraction - 1) / 4) * 100}%)`
                                }}
                            />
                            <span className="text-lg font-bold text-blue-600 w-12 text-center">
                                {settings.fpsExtraction}
                            </span>
                        </div>
                        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                            <span>Faster</span>
                            <span>More Accurate</span>
                        </div>
                    </div>

                    {/* Similarity Threshold */}
                    <div className="border-b border-gray-200 dark:border-gray-700 pb-5">
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                            Face Recognition Similarity Threshold
                        </label>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                            Minimum similarity score (0-1) to consider a face match. Lower = more lenient, Higher = more strict.
                        </p>
                        <div className="flex items-center gap-4">
                            <input
                                type="range"
                                min="0.1"
                                max="0.6"
                                step="0.05"
                                value={settings.similarityThreshold}
                                onChange={(e) => handleChange('similarityThreshold', parseFloat(e.target.value))}
                                className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
                                style={{
                                    background: `linear-gradient(90deg, #2a9d8f ${((settings.similarityThreshold - 0.1) / 0.5) * 100}%, rgba(148,163,184,0.4) ${((settings.similarityThreshold - 0.1) / 0.5) * 100}%)`
                                }}
                            />
                            <span className="text-lg font-bold text-blue-600 w-16 text-center">
                                {settings.similarityThreshold.toFixed(2)}
                            </span>
                        </div>
                        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                            <span>Lenient (0.1)</span>
                            <span>Strict (0.6)</span>
                        </div>
                    </div>

                    {/* Detection Confidence */}
                    <div className="border-b border-gray-200 dark:border-gray-700 pb-5">
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                            Face Detection Confidence
                        </label>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                            Minimum confidence score (0-1) for face detection. Higher values reduce false positives.
                        </p>
                        <div className="flex items-center gap-4">
                            <input
                                type="range"
                                min="0.1"
                                max="0.7"
                                step="0.05"
                                value={settings.detectionConfidence}
                                onChange={(e) => handleChange('detectionConfidence', parseFloat(e.target.value))}
                                className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
                                style={{
                                    background: `linear-gradient(90deg, #2a9d8f ${((settings.detectionConfidence - 0.1) / 0.6) * 100}%, rgba(148,163,184,0.4) ${((settings.detectionConfidence - 0.1) / 0.6) * 100}%)`
                                }}
                            />
                            <span className="text-lg font-bold text-blue-600 w-16 text-center">
                                {settings.detectionConfidence.toFixed(2)}
                            </span>
                        </div>
                        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                            <span>Detect More (0.1)</span>
                            <span>More Accurate (0.7)</span>
                        </div>
                    </div>

                    {/* GPU Acceleration */}
                    <div className="pb-5">
                        <label className="flex items-center gap-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.useGPU}
                                onChange={(e) => handleChange('useGPU', e.target.checked)}
                                className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                            />
                            <div>
                                <span className="block text-sm font-semibold text-gray-700 dark:text-gray-200">
                                    Enable GPU Acceleration
                                </span>
                                <span className="block text-sm text-gray-500 dark:text-gray-400">
                                    Use GPU for faster face detection and recognition (requires CUDA-compatible GPU)
                                </span>
                            </div>
                        </label>
                    </div>
                </div>

                {/* Rebuild Encodings */}
                <div className="mt-6 panel panel-muted p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-2">
                        Rebuild Face Encodings
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                        Use this if recognition is inaccurate. Leave student ID empty to rebuild all.
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Student ID (optional)
                            </label>
                            <input
                                type="text"
                                value={rebuildStudentId}
                                onChange={(e) => setRebuildStudentId(e.target.value)}
                                placeholder="e.g., 11"
                                className="form-input"
                            />
                        </div>
                        <button
                            onClick={handleRebuildEncodings}
                            disabled={rebuildStatus.status === 'running'}
                            className="btn btn-primary w-full"
                        >
                            {rebuildStatus.status === 'running' ? 'Rebuilding...' : 'Start Rebuild'}
                        </button>
                    </div>

                    <div className="mt-4">
                        <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-300 mb-2">
                            <span>Status: {rebuildStatus.status}</span>
                            <span>{rebuildStatus.current || 0}/{rebuildStatus.total || 0}</span>
                        </div>
                        <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div
                                className="h-2 bg-blue-600 rounded-full"
                                style={{ width: `${rebuildStatus.total ? Math.round((rebuildStatus.current / rebuildStatus.total) * 100) : 0}%` }}
                            ></div>
                        </div>
                        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                            {rebuildStatus.current_student && (
                                <div>Processing student: {rebuildStatus.current_student}</div>
                            )}
                            {rebuildStatus.success_count !== undefined && (
                                <div>Success: {rebuildStatus.success_count} | Failed: {rebuildStatus.failed_count}</div>
                            )}
                            {rebuildStatus.last_error && (
                                <div className="text-red-600 dark:text-red-300">Error: {rebuildStatus.last_error}</div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className="btn btn-primary"
                    >
                        <Save className="w-5 h-5" />
                        {saving ? 'Saving...' : 'Save Settings'}
                    </button>

                    <button
                        onClick={handleReset}
                        className="btn btn-secondary"
                    >
                        <RotateCcw className="w-5 h-5" />
                        Reset to Defaults
                    </button>
                </div>

                {/* Info Box */}
                <div className="mt-6 p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
                    <h3 className="font-semibold text-emerald-900 dark:text-emerald-100 mb-2">Recommended Settings</h3>
                    <ul className="text-sm text-emerald-800 dark:text-emerald-200 space-y-1">
                        <li>• <strong>FPS Extraction:</strong> 2-3 for balanced speed and accuracy</li>
                        <li>• <strong>Similarity Threshold:</strong> 0.25-0.35 for good recognition</li>
                        <li>• <strong>Detection Confidence:</strong> 0.25-0.35 to avoid missing faces</li>
                        <li>• <strong>GPU:</strong> Enable if you have a compatible NVIDIA GPU</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default Settings;
