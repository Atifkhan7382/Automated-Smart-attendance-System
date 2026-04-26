import React, { useState, useEffect } from 'react';
import { FileText, Download, Calendar, Users, TrendingUp, Filter } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { teacherAPI } from '../../services/api';
import axios from 'axios';

const Reports = () => {
    const [classes, setClasses] = useState([]);
    const [selectedClass, setSelectedClass] = useState('');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [reportData, setReportData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [exporting, setExporting] = useState(false);

    useEffect(() => {
        loadClasses();
    }, []);

    const loadClasses = async () => {
        try {
            const data = await teacherAPI.getClasses();
            setClasses(data);
        } catch (error) {
            console.error('Error loading classes:', error);
        }
    };

    const generateReport = async () => {
        try {
            setLoading(true);
            const params = new URLSearchParams();
            if (selectedClass) params.append('class_name', selectedClass);
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);

            const response = await axios.get(`http://localhost:8000/api/attendance/report?${params}`);

            // Map backend response to frontend format
            const data = response.data;
            const mappedData = {
                total_sessions: data.summary?.total_sessions || 0,
                total_students: data.summary?.total_students || 0,
                average_attendance: data.summary?.average_attendance_percentage || 0,
                records: (data.daily_records || []).map(record => ({
                    id: record.id,
                    date: record.date,
                    class_name: record.class_name,
                    present_count: record.present_count || 0,
                    absent_count: (record.total_records || 0) - (record.present_count || 0),
                    attendance_percentage: record.attendance_percentage || 0
                }))
            };

            setReportData(mappedData);
            setLoading(false);
        } catch (error) {
            console.error('Error generating report:', error);
            setLoading(false);
            alert('Failed to generate report: ' + (error.response?.data?.detail || error.message));
        }
    };

    const exportToExcel = async () => {
        try {
            setExporting(true);
            const params = new URLSearchParams();
            if (selectedClass) params.append('class_name', selectedClass);
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);

            const response = await axios.get(`http://localhost:8000/api/attendance/export?${params}`);

            if (response.data.download_url) {
                window.open(`http://localhost:8000${response.data.download_url}`, '_blank');
            }

            setExporting(false);
        } catch (error) {
            console.error('Error exporting report:', error);
            setExporting(false);
            alert('Failed to export report');
        }
    };

    const exportSessionToExcel = async (sessionId) => {
        try {
            const response = await axios.get(`http://localhost:8000/api/attendance/session/${sessionId}/export`);

            if (response.data.download_url) {
                window.open(`http://localhost:8000${response.data.download_url}`, '_blank');
            }
        } catch (error) {
            console.error('Error exporting session:', error);
            alert('Failed to export session report');
        }
    };

    const deleteSession = async (sessionId) => {
        if (!window.confirm('Are you sure you want to delete this attendance session? This action cannot be undone.')) {
            return;
        }

        try {
            await axios.delete(`http://localhost:8000/api/attendance/session/${sessionId}`);
            alert('Session deleted successfully');
            // Refresh the report
            generateReport();
        } catch (error) {
            console.error('Error deleting session:', error);
            alert('Failed to delete session');
        }
    };

    const clearAllReports = async () => {
        if (!window.confirm('⚠️ WARNING: This will delete ALL attendance records permanently! Are you sure?')) {
            return;
        }

        const confirmation = window.prompt('Type "DELETE ALL" to confirm:');
        if (confirmation !== 'DELETE ALL') {
            alert('Deletion cancelled');
            return;
        }

        try {
            await axios.delete('http://localhost:8000/api/attendance/clear-all');
            alert('All attendance history cleared successfully');
            setReportData(null);
        } catch (error) {
            console.error('Error clearing reports:', error);
            alert('Failed to clear reports');
        }
    };

    const attendanceTrend = (reportData?.records || []).map((record) => ({
        date: new Date(record.date).toLocaleDateString(),
        attendance: Number(record.attendance_percentage || 0)
    }));

    return (
        <div className="w-full">
            <div className="panel panel-body border-0">
                <div className="flex items-center gap-3 mb-6">
                    <FileText className="w-6 h-6 text-emerald-600" />
                    <h2 className="page-title">Attendance Reports</h2>
                </div>

                {/* Filters */}
                <div className="panel panel-muted p-6 mb-6 border border-gray-100 dark:border-gray-700 rounded-lg">
                    <div className="flex items-center gap-2 mb-4">
                        <Filter className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                        <h3 className="font-semibold">Filters</h3>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Class</label>
                            <select
                                value={selectedClass}
                                onChange={(e) => setSelectedClass(e.target.value)}
                                className="form-select"
                            >
                                <option value="">All Classes</option>
                                {classes.map((cls) => (
                                    <option key={cls.id} value={cls.class_name}>{cls.class_name}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Start Date</label>
                            <input
                                type="date"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                                className="form-input"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">End Date</label>
                            <input
                                type="date"
                                value={endDate}
                                onChange={(e) => setEndDate(e.target.value)}
                                className="form-input"
                            />
                        </div>

                        <div className="flex items-end">
                            <button
                                onClick={generateReport}
                                disabled={loading}
                                className="btn btn-primary w-full"
                            >
                                <FileText className="w-4 h-4" />
                                {loading ? 'Generating...' : 'Generate Report'}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Report Results */}
                {reportData && (
                    <div className="space-y-6">
                        {/* Summary Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="panel panel-body">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-emerald-700 dark:text-emerald-300 font-medium">Total Sessions</p>
                                        <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-300">{reportData.total_sessions || 0}</p>
                                    </div>
                                    <Calendar className="w-8 h-8 text-emerald-600 dark:text-emerald-300" />
                                </div>
                            </div>

                            <div className="panel panel-body">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-emerald-700 dark:text-emerald-300 font-medium">Total Students</p>
                                        <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-300">{reportData.total_students || 0}</p>
                                    </div>
                                    <Users className="w-8 h-8 text-emerald-600 dark:text-emerald-300" />
                                </div>
                            </div>

                            <div className="panel panel-body">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-emerald-700 dark:text-emerald-300 font-medium">Avg Attendance</p>
                                        <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-300">
                                            {reportData.average_attendance ? `${reportData.average_attendance.toFixed(1)}%` : '0%'}
                                        </p>
                                    </div>
                                    <TrendingUp className="w-8 h-8 text-emerald-600 dark:text-emerald-300" />
                                </div>
                            </div>
                        </div>

                        {/* Attendance Rate Trend */}
                        <div className="panel">
                            <div className="panel-header">
                                <h3 className="text-lg font-semibold">Attendance Rate Trend</h3>
                            </div>
                            <div className="panel-body">
                                {attendanceTrend.length > 0 ? (
                                    <div className="h-72">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <LineChart data={attendanceTrend} margin={{ top: 10, right: 16, left: 0, bottom: 8 }}>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#e1e6ee" />
                                                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                                                <YAxis domain={[0, 100]} tickFormatter={(value) => `${value}%`} />
                                                <Tooltip formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Attendance']} />
                                                <Line type="monotone" dataKey="attendance" stroke="#2a9d8f" strokeWidth={3} dot={{ r: 3 }} />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                ) : (
                                    <p className="text-gray-500 dark:text-gray-400 text-center py-8">No sessions available for charting</p>
                                )}
                            </div>
                        </div>

                        {/* Export and Clear Buttons */}
                        <div className="flex flex-wrap justify-between items-center gap-3">
                            <button
                                onClick={clearAllReports}
                                className="btn btn-danger"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                                Clear All Reports
                            </button>

                            <button
                                onClick={exportToExcel}
                                disabled={exporting}
                                className="btn btn-primary"
                            >
                                <Download className="w-5 h-5" />
                                {exporting ? 'Exporting...' : 'Export All to Excel'}
                            </button>
                        </div>
                        {/* Detailed Records Table */}
                        {reportData.records && reportData.records.length > 0 && (
                            <div className="table-wrap">
                                <div className="overflow-x-auto">
                                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                        <thead className="table-head">
                                            <tr>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Class</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Present</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Absent</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Attendance %</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                            {reportData.records.map((record, index) => (
                                                <tr key={index} className="table-row">
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                                        {new Date(record.date).toLocaleDateString()}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{record.class_name}</td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 dark:text-green-300 font-medium">{record.present_count}</td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 dark:text-red-300 font-medium">{record.absent_count}</td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                                        <div className="flex items-center gap-2">
                                                            <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                                                <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${record.attendance_percentage}%` }}></div>
                                                            </div>
                                                            <span className="font-medium">{record.attendance_percentage.toFixed(1)}%</span>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                                        <div className="flex items-center gap-2">
                                                            <button
                                                                onClick={() => exportSessionToExcel(record.id)}
                                                                className="btn btn-secondary text-sm"
                                                                title="Download session report"
                                                            >
                                                                <Download className="w-4 h-4" />
                                                                Download
                                                            </button>
                                                            <button
                                                                onClick={() => deleteSession(record.id)}
                                                                className="btn btn-danger text-sm"
                                                                title="Delete this session"
                                                            >
                                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                                </svg>
                                                                Delete
                                                            </button>
                                                        </div>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}

                        {reportData.records && reportData.records.length === 0 && (
                            <div className="text-center py-12 panel panel-muted border border-gray-100 dark:border-gray-700 rounded-lg">
                                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                                <p className="text-gray-500 dark:text-gray-400">No attendance records found for the selected filters.</p>
                            </div>
                        )}
                    </div>
                )}

                {!reportData && !loading && (
                    <div className="text-center py-12 panel panel-muted border border-gray-100 dark:border-gray-700 rounded-lg">
                        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                        <p className="text-gray-500 dark:text-gray-400">Select filters and click "Generate Report" to view attendance data.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Reports;
