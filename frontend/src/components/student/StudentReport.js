import React, { useState, useEffect } from 'react';
import { FileText, Download, Calendar, TrendingUp, CheckCircle, XCircle } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { studentAPI } from '../../services/api';
import axios from 'axios';

const StudentReport = () => {
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [reportData, setReportData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [exporting, setExporting] = useState(false);

    const generateReport = async () => {
        try {
            setLoading(true);
            const params = new URLSearchParams();
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);

            const response = await axios.get(`http://localhost:8000/api/student/report?${params}`);
            setReportData(response.data);
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
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);

            const response = await axios.get(`http://localhost:8000/api/student/report/export?${params}`);

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

    const attendanceTrend = (reportData?.records || []).map((record) => ({
        date: new Date(record.date).toLocaleDateString(),
        attendance: record.status === 'present' ? 100 : 0
    }));

    return (
        <div className="w-full">
            <div className="panel panel-body border-0">
                <div className="flex items-center gap-3 mb-4">
                    <FileText className="w-6 h-6 text-emerald-600" />
                    <h2 className="page-title">My Attendance Report</h2>
                </div>

                {/* Date Filters */}
                <div className="panel panel-muted p-6 mb-4 border border-gray-100 dark:border-gray-700 rounded-lg">
                    <h3 className="font-semibold mb-4">Filter by Date Range</h3>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                    <div className="space-y-4">
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
                                        <p className="text-sm text-emerald-700 dark:text-emerald-300 font-medium">Present</p>
                                        <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-300">{reportData.present_count || 0}</p>
                                    </div>
                                    <CheckCircle className="w-8 h-8 text-emerald-600 dark:text-emerald-300" />
                                </div>
                            </div>

                            <div className="panel panel-body">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-emerald-700 dark:text-emerald-300 font-medium">Attendance Rate</p>
                                        <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-300">
                                            {reportData.attendance_percentage ? `${reportData.attendance_percentage.toFixed(1)}%` : '0%'}
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
                                                <Tooltip formatter={(value) => [`${Number(value).toFixed(0)}%`, 'Attendance']} />
                                                <Line type="monotone" dataKey="attendance" stroke="#2a9d8f" strokeWidth={3} dot={{ r: 3 }} />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                ) : (
                                    <p className="text-gray-500 dark:text-gray-400 text-center py-6">No sessions available for charting</p>
                                )}
                            </div>
                        </div>

                        {/* Export Button */}
                        <div className="flex justify-end">
                            <button
                                onClick={exportToExcel}
                                disabled={exporting}
                                className="btn btn-primary"
                            >
                                <Download className="w-5 h-5" />
                                {exporting ? 'Exporting...' : 'Export to Excel'}
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
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Confidence</th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                            {reportData.records.map((record, index) => (
                                                <tr key={index} className="table-row">
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                                        {new Date(record.date).toLocaleDateString()}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{record.class_name}</td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                                                        {record.status === 'present' ? (
                                                            <span className="badge badge-success">
                                                                <CheckCircle className="w-4 h-4" />
                                                                Present
                                                            </span>
                                                        ) : (
                                                            <span className="badge badge-danger">
                                                                <XCircle className="w-4 h-4" />
                                                                Absent
                                                            </span>
                                                        )}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                                        {record.confidence ? `${(record.confidence * 100).toFixed(1)}%` : 'N/A'}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}

                        {reportData.records && reportData.records.length === 0 && (
                            <div className="text-center py-10 panel panel-muted border border-gray-100 dark:border-gray-700 rounded-lg">
                                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                                <p className="text-gray-500 dark:text-gray-400">No attendance records found for the selected date range.</p>
                            </div>
                        )}
                    </div>
                )}

                {!reportData && !loading && (
                    <div className="text-center py-10 panel panel-muted border border-gray-100 dark:border-gray-700 rounded-lg">
                        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                        <p className="text-gray-500 dark:text-gray-400">Select a date range and click "Generate Report" to view your attendance data.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default StudentReport;
