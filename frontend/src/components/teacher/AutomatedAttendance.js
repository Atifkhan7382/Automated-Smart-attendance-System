import React, { useState, useEffect } from 'react';
import { Play, Square, Settings, Camera, Clock, CheckCircle, XCircle, Activity } from 'lucide-react';
import { teacherAPI } from '../../services/api';
import axios from 'axios';

const AutomatedAttendance = () => {
    const [classes, setClasses] = useState([]);
    const [selectedClass, setSelectedClass] = useState('');
    const [status, setStatus] = useState(null);
    const [settings, setSettings] = useState({
        interval_minutes: 30,
        camera_source: '0'
    });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadClasses();
        loadStatus();
        loadSettings();

        // Poll status every 5 seconds
        const interval = setInterval(loadStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    const loadClasses = async () => {
        try {
            const data = await teacherAPI.getClasses();
            setClasses(data);
        } catch (error) {
            console.error('Error loading classes:', error);
        }
    };

    const loadStatus = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/automation/status');
            setStatus(response.data);
        } catch (error) {
            console.error('Error loading status:', error);
        }
    };

    const loadSettings = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/automation/settings');
            setSettings(response.data);
            if (response.data.class_name) {
                setSelectedClass(response.data.class_name);
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    };

    const startAutomation = async () => {
        if (!selectedClass) {
            alert('Please select a class');
            return;
        }

        try {
            setLoading(true);
            await axios.post('http://localhost:8000/api/automation/start', {
                class_name: selectedClass
            });
            alert('Automated attendance started successfully!');
            loadStatus();
            setLoading(false);
        } catch (error) {
            console.error('Error starting automation:', error);
            alert('Failed to start automation: ' + (error.response?.data?.detail || error.message));
            setLoading(false);
        }
    };

    const stopAutomation = async () => {
        try {
            setLoading(true);
            await axios.post('http://localhost:8000/api/automation/stop');
            alert('Automated attendance stopped');
            loadStatus();
            setLoading(false);
        } catch (error) {
            console.error('Error stopping automation:', error);
            alert('Failed to stop automation');
            setLoading(false);
        }
    };

    const updateSettings = async () => {
        try {
            await axios.post('http://localhost:8000/api/automation/settings', settings);
            alert('Settings updated successfully');
        } catch (error) {
            console.error('Error updating settings:', error);
            alert('Failed to update settings');
        }
    };

    const isRunning = status?.is_running || false;

    return (
        <div className="w-full">
            <div className="panel panel-body border-0 panel-elevate">
                <div className="flex items-center gap-3 mb-6">
                    <Camera className="w-6 h-6 text-emerald-600" />
                    <h2 className="page-title">Automated Attendance</h2>
                </div>

                {/* Status Card */}
                <div className={`rounded-lg p-6 mb-6 border-2 ${isRunning ? 'bg-emerald-50 border-emerald-200 dark:bg-emerald-900/30 dark:border-emerald-800' : 'bg-gray-50 border-gray-200 dark:bg-gray-900/40 dark:border-gray-700'}`}>
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <Activity className={`w-8 h-8 ${isRunning ? 'text-emerald-600 animate-pulse' : 'text-gray-400'}`} />
                            <div>
                                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
                                    {isRunning ? 'Automation Active' : 'Automation Stopped'}
                                </h3>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    {isRunning ? `Running for class: ${settings.class_name}` : 'Configure and start automation'}
                                </p>
                            </div>
                        </div>
                        {isRunning ? (
                            <CheckCircle className="w-12 h-12 text-emerald-600" />
                        ) : (
                            <XCircle className="w-12 h-12 text-gray-400" />
                        )}
                    </div>

                    {/* Statistics */}
                    {status && (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                            <div className="panel panel-muted p-3 rounded">
                                <p className="text-xs text-gray-500 dark:text-gray-400">Total Runs</p>
                                <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{status.total_runs || 0}</p>
                            </div>
                            <div className="panel panel-muted p-3 rounded">
                                <p className="text-xs text-gray-500 dark:text-gray-400">Successful</p>
                                <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-300">{status.successful_runs || 0}</p>
                            </div>
                            <div className="panel panel-muted p-3 rounded">
                                <p className="text-xs text-gray-500 dark:text-gray-400">Failed</p>
                                <p className="text-2xl font-bold text-red-600 dark:text-red-300">{status.failed_runs || 0}</p>
                            </div>
                            <div className="panel panel-muted p-3 rounded">
                                <p className="text-xs text-gray-500 dark:text-gray-400">Next Run</p>
                                <p className="text-sm font-semibold text-gray-800 dark:text-gray-100">
                                    {status.next_run ? new Date(status.next_run).toLocaleTimeString() : 'N/A'}
                                </p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Configuration */}
                <div className="panel panel-muted p-6 mb-6 border border-gray-100 dark:border-gray-700 rounded-lg">
                    <div className="flex items-center gap-2 mb-4">
                        <Settings className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                        <h3 className="font-semibold text-gray-700 dark:text-gray-200">Configuration</h3>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Class Selection */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Class
                            </label>
                            <select
                                value={selectedClass}
                                onChange={(e) => setSelectedClass(e.target.value)}
                                disabled={isRunning}
                                className="form-select"
                            >
                                <option value="">Select a class</option>
                                {classes.map((cls) => (
                                    <option key={cls.id} value={cls.class_name}>
                                        {cls.class_name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Interval */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Interval (minutes)
                            </label>
                            <input
                                type="number"
                                min="1"
                                max="1440"
                                value={settings.interval_minutes}
                                onChange={(e) => setSettings({ ...settings, interval_minutes: parseInt(e.target.value) })}
                                disabled={isRunning}
                                className="form-input"
                            />
                        </div>

                        {/* Camera Source */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Camera Source
                            </label>
                            <input
                                type="text"
                                value={settings.camera_source}
                                onChange={(e) => setSettings({ ...settings, camera_source: e.target.value })}
                                disabled={isRunning}
                                placeholder="0 (default camera) or RTSP URL"
                                className="form-input"
                            />
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Use 0 for default camera or enter RTSP URL</p>
                        </div>

                        {/* Update Settings Button */}
                        <div className="flex items-end">
                            <button
                                onClick={updateSettings}
                                disabled={isRunning}
                                className="btn btn-secondary w-full"
                            >
                                Update Settings
                            </button>
                        </div>
                    </div>
                </div>

                {/* Control Buttons */}
                <div className="flex gap-4">
                    {!isRunning ? (
                        <button
                            onClick={startAutomation}
                            disabled={loading || !selectedClass}
                            className="btn btn-primary flex-1"
                        >
                            <Play className="w-5 h-5" />
                            {loading ? 'Starting...' : 'Start Automation'}
                        </button>
                    ) : (
                        <button
                            onClick={stopAutomation}
                            disabled={loading}
                            className="btn btn-danger flex-1"
                        >
                            <Square className="w-5 h-5" />
                            {loading ? 'Stopping...' : 'Stop Automation'}
                        </button>
                    )}
                </div>

                {/* Info Box */}
                <div className="mt-6 p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
                    <h3 className="font-semibold text-emerald-900 dark:text-emerald-100 mb-2">How It Works</h3>
                    <ul className="text-sm text-emerald-800 dark:text-emerald-200 space-y-1">
                        <li>• Automatically captures images from the camera at set intervals</li>
                        <li>• Processes images using face recognition to identify students</li>
                        <li>• Marks attendance and saves records automatically</li>
                        <li>• Runs continuously until manually stopped</li>
                        <li>• Perfect for classrooms with fixed camera setups</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default AutomatedAttendance;
