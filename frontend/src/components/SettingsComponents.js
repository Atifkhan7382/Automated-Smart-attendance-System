// File: frontend/src/components/Settings.js
import React, { useState, useEffect } from 'react';
import { Moon, Sun } from 'lucide-react';
import { getModelStatus, automationAPI, studentAPI } from '../services/api';

function Settings({ onBack, darkMode, toggleDarkMode }) {
  const [modelStatus, setModelStatus] = useState(null);
  const [settings, setSettings] = useState({
    fpsExtraction: 2,
    similarityThreshold: 0.6,
    useGPU: false,
  });
  const [automationSettings, setAutomationSettings] = useState({
    enabled: false,
    interval_minutes: 30,
    class_name: '',
    camera_source: '0',
  });
  const [automationStatus, setAutomationStatus] = useState(null);
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadModelStatus();
    loadSettings();
    loadAutomationSettings();
    loadAutomationStatus();
    loadClasses();

    // Poll automation status every 10 seconds
    const interval = setInterval(() => {
      if (automationSettings.enabled) {
        loadAutomationStatus();
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [automationSettings.enabled]);

  const loadModelStatus = async () => {
    try {
      const response = await getModelStatus();
      setModelStatus(response.data);
    } catch (error) {
      console.error('Error loading model status:', error);
    }
  };

  const loadSettings = () => {
    const saved = localStorage.getItem('appSettings');
    if (saved) {
      setSettings(JSON.parse(saved));
    }
  };

  const saveSettings = () => {
    localStorage.setItem('appSettings', JSON.stringify(settings));
    alert('Settings saved successfully!');
  };

  const loadAutomationSettings = async () => {
    try {
      const response = await automationAPI.getSettings();
      setAutomationSettings(response);
    } catch (error) {
      console.error('Error loading automation settings:', error);
    }
  };

  const loadAutomationStatus = async () => {
    try {
      const response = await automationAPI.getStatus();
      setAutomationStatus(response);
    } catch (error) {
      console.error('Error loading automation status:', error);
    }
  };

  const loadClasses = async () => {
    try {
      const data = await studentAPI.getStudents();
      // Extract students array from API response
      const students = Array.isArray(data) ? data : (data.students || []);
      const uniqueClasses = [...new Set(students.map((s) => s.class_name))].filter(Boolean);
      setClasses(uniqueClasses);
    } catch (error) {
      console.error('Error loading classes:', error);
      setClasses([]);
    }
  };

  const saveAutomationSettings = async () => {
    try {
      setLoading(true);
      await automationAPI.updateSettings(automationSettings);
      alert('Automation settings saved successfully!');
      await loadAutomationStatus();
    } catch (error) {
      console.error('Error saving automation settings:', error);
      alert('Failed to save automation settings');
    } finally {
      setLoading(false);
    }
  };

  const handleStartAutomation = async () => {
    if (!automationSettings.class_name) {
      alert('Please select a class first');
      return;
    }
    try {
      setLoading(true);
      await automationAPI.start(automationSettings.class_name);
      setAutomationSettings({ ...automationSettings, enabled: true });
      await loadAutomationStatus();
      alert('Automated attendance started successfully!');
    } catch (error) {
      console.error('Error starting automation:', error);
      alert('Failed to start automation');
    } finally {
      setLoading(false);
    }
  };

  const handleStopAutomation = async () => {
    try {
      setLoading(true);
      const response = await automationAPI.stop();
      console.log('Stop automation response:', response);

      // Update local state based on response
      if (response.message && response.message.includes('stopped successfully')) {
        setAutomationSettings({ ...automationSettings, enabled: false });
        await loadAutomationStatus();
        alert('Automated attendance stopped successfully!');
      } else {
        alert(`Automation stop response: ${response.message || 'Unknown response'}`);
      }
    } catch (error) {
      console.error('Error stopping automation:', error);
      alert('Failed to stop automation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="settings">
      <div className="page-header">
        <button className="btn-back" onClick={onBack}>
          ← Back
        </button>
        <h2>Settings</h2>
      </div>

      <div className="settings-content">
        <div className="settings-section">
          <h3>Model Information</h3>
          {modelStatus ? (
            <div className="model-info">
              <p>
                <strong>Status:</strong>{' '}
                <span className={`status ${modelStatus.status}`}>
                  {modelStatus.status === 'trained' ? '✓ Trained' : '⚠️ Not Trained'}
                </span>
              </p>
              {modelStatus.status === 'trained' && (
                <>
                  <p>
                    <strong>Version:</strong> {modelStatus.version}
                  </p>
                  <p>
                    <strong>Accuracy:</strong> {modelStatus.accuracy?.toFixed(2)}%
                  </p>
                  <p>
                    <strong>Classes:</strong> {modelStatus.num_classes}
                  </p>
                  <p>
                    <strong>Created:</strong>{' '}
                    {new Date(modelStatus.created_at).toLocaleString()}
                  </p>
                </>
              )}
            </div>
          ) : (
            <p>Loading model information...</p>
          )}
        </div>

        <div className="settings-section">
          <h3>Appearance</h3>
          <div className="setting-item">
            <label>Dark Mode</label>
            <div className="flex items-center gap-3">
              <button
                onClick={toggleDarkMode}
                className="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors"
                style={{
                  backgroundColor: darkMode ? 'var(--color-bg-secondary)' : 'var(--color-bg-secondary)',
                  color: 'var(--color-text-primary)',
                  border: '1px solid var(--color-border)'
                }}
              >
                {darkMode ? (
                  <>
                    <Sun className="h-5 w-5" style={{ color: '#eab308' }} />
                    <span>Light Mode</span>
                  </>
                ) : (
                  <>
                    <Moon className="h-5 w-5" style={{ color: '#6b7280' }} />
                    <span>Dark Mode</span>
                  </>
                )}
              </button>
            </div>
            <small>Switch between light and dark theme</small>
          </div>
        </div>

        <div className="settings-section">
          <h3>Video Processing</h3>
          <div className="setting-item">
            <label>Frame Extraction FPS</label>
            <input
              type="number"
              min="1"
              max="10"
              value={settings.fpsExtraction}
              onChange={(e) =>
                setSettings({ ...settings, fpsExtraction: Number(e.target.value) })
              }
            />
            <small>Frames per second to extract from enrollment videos</small>
          </div>
        </div>

        <div className="settings-section">
          <h3>Recognition Settings</h3>
          <div className="setting-item">
            <label>Similarity Threshold</label>
            <input
              type="range"
              min="0.3"
              max="0.9"
              step="0.05"
              value={settings.similarityThreshold}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  similarityThreshold: Number(e.target.value),
                })
              }
            />
            <span className="value">{settings.similarityThreshold.toFixed(2)}</span>
            <small>
              Minimum similarity score to mark attendance (lower = more lenient)
            </small>
          </div>

          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.useGPU}
                onChange={(e) =>
                  setSettings({ ...settings, useGPU: e.target.checked })
                }
              />
              Use GPU for training (if available)
            </label>
            <small>Enable CUDA acceleration for faster model training</small>
          </div>
        </div>

        <div className="settings-actions">
          <button className="btn-primary" onClick={saveSettings}>
            Save Settings
          </button>
          <button className="btn-secondary" onClick={loadSettings}>
            Reset to Saved
          </button>
        </div>

        <div className="settings-section">
          <h3>Automated Attendance</h3>
          <p className="section-description">
            Configure automatic attendance marking at scheduled intervals
          </p>

          <div className="setting-item">
            <label>Select Class</label>
            <select
              value={automationSettings.class_name}
              onChange={(e) => setAutomationSettings({ ...automationSettings, class_name: e.target.value })}
              disabled={automationSettings.enabled}
            >
              <option value="">-- Select a class --</option>
              {classes.map((className) => (
                <option key={className} value={className}>
                  {className}
                </option>
              ))}
            </select>
            <small>Choose the class for automated attendance marking</small>
          </div>

          <div className="setting-item">
            <label>Interval (minutes)</label>
            <input
              type="number"
              min="5"
              max="240"
              value={automationSettings.interval_minutes}
              onChange={(e) => setAutomationSettings({ ...automationSettings, interval_minutes: Number(e.target.value) })}
              disabled={automationSettings.enabled}
            />
            <small>How often to automatically mark attendance (5-240 minutes)</small>
          </div>

          <div className="setting-item">
            <label>Camera Source</label>
            <input
              type="text"
              value={automationSettings.camera_source}
              onChange={(e) => setAutomationSettings({ ...automationSettings, camera_source: e.target.value })}
              disabled={automationSettings.enabled}
              placeholder="0 for default camera, or RTSP URL"
            />
            <small>Camera device index (0, 1, 2...) or RTSP stream URL</small>
          </div>

          {automationStatus && (
            <div className="automation-status">
              <h4>Status</h4>
              <p>
                <strong>Running:</strong>{' '}
                <span className={`status ${automationStatus.is_running ? 'active' : 'inactive'}`}>
                  {automationStatus.is_running ? '✓ Active' : '⚠️ Inactive'}
                </span>
              </p>
              {automationStatus.last_run && (
                <p>
                  <strong>Last Run:</strong> {new Date(automationStatus.last_run).toLocaleString()}
                </p>
              )}
              {automationStatus.next_run && (
                <p>
                  <strong>Next Run:</strong> {new Date(automationStatus.next_run).toLocaleString()}
                </p>
              )}
              <p>
                <strong>Total Runs:</strong> {automationStatus.total_runs} |
                <strong> Successful:</strong> {automationStatus.successful_runs} |
                <strong> Failed:</strong> {automationStatus.failed_runs}
              </p>
            </div>
          )}

          <div className="automation-actions">
            <button
              className="btn-primary"
              onClick={saveAutomationSettings}
              disabled={loading || automationSettings.enabled}
            >
              Save Settings
            </button>
            {!automationSettings.enabled ? (
              <button
                className="btn-success"
                onClick={handleStartAutomation}
                disabled={loading || !automationSettings.class_name}
              >
                {loading ? 'Starting...' : 'Start Automation'}
              </button>
            ) : (
              <button
                className="btn-danger"
                onClick={handleStopAutomation}
                disabled={loading}
              >
                {loading ? 'Stopping...' : 'Stop Automation'}
              </button>
            )}
          </div>
        </div>

        <div className="settings-section">
          <h3>System Information</h3>
          <div className="system-info">
            <p>
              <strong>Backend API:</strong> {process.env.REACT_APP_API_URL || 'http://localhost:8000/api'}
            </p>
            <p>
              <strong>Version:</strong> 1.0.0
            </p>
            <p>
              <strong>Environment:</strong> {process.env.NODE_ENV}
            </p>
          </div>
        </div>

        <div className="settings-section">
          <h3>About</h3>
          <p>
            AttendAI uses advanced face recognition technology to
            automatically mark classroom attendance. The system employs deep learning
            models trained on student enrollment videos to accurately identify students
            in classroom snapshots.
          </p>
          <div className="tech-stack">
            <span className="badge">React</span>
            <span className="badge">FastAPI</span>
            <span className="badge">PyTorch</span>
            <span className="badge">OpenCV</span>
            <span className="badge">Faiss</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;