import React, { useState, useEffect } from 'react';
import { Calendar, Filter, CheckCircle, XCircle, Download, FileText, TrendingUp } from 'lucide-react';
import { studentAPI } from '../../services/api';
import axios from 'axios';

const AttendanceView = () => {
    const [attendance, setAttendance] = useState([]);
    const [filteredAttendance, setFilteredAttendance] = useState([]);
    const [classes, setClasses] = useState([]);
    const [selectedClass, setSelectedClass] = useState('');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [loading, setLoading] = useState(true);
    const [exporting, setExporting] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    useEffect(() => {
        filterAttendance();
    }, [attendance, selectedClass, startDate, endDate]);

    const loadData = async () => {
        try {
            setLoading(true);
            const [attendanceResponse, classesData] = await Promise.all([
                studentAPI.getAttendance(),
                studentAPI.getClasses()
            ]);

            // The API returns {records: [], statistics: {}}
            const attendanceRecords = attendanceResponse.records || [];

            setAttendance(Array.isArray(attendanceRecords) ? attendanceRecords : []);
            setClasses(Array.isArray(classesData) ? classesData : []);
            setLoading(false);
        } catch (err) {
            console.error('Failed to load data:', err);
            setAttendance([]);
            setClasses([]);
            setLoading(false);
        }
    };

    const filterAttendance = () => {
        let filtered = [...attendance];

        if (selectedClass) {
            filtered = filtered.filter(a => a.class_name === selectedClass);
        }

        if (startDate) {
            filtered = filtered.filter(a => new Date(a.date) >= new Date(startDate));
        }

        if (endDate) {
            filtered = filtered.filter(a => new Date(a.date) <= new Date(endDate));
        }

        setFilteredAttendance(filtered);
    };

    const calculateStats = () => {
        const total = filteredAttendance.length;
        const present = filteredAttendance.filter(a => a.status === 'present').length;
        const percentage = total > 0 ? (present / total * 100) : 0;

        return { total, present, percentage };
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

    const reportStats = calculateStats();

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div>
                <h2 className="page-title mb-2">My Attendance</h2>
                <p className="page-subtitle">View and download your attendance records</p>
            </div>

            {/* Statistics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="panel panel-body">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-emerald-700 dark:text-emerald-300 font-medium">Total Sessions</p>
                            <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-300">{reportStats.total}</p>
                        </div>
                        <Calendar className="w-8 h-8 text-emerald-600 dark:text-emerald-300" />
                    </div>
                </div>

                <div className="panel panel-body">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-emerald-700 dark:text-emerald-300 font-medium">Present</p>
                            <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-300">{reportStats.present}</p>
                        </div>
                        <CheckCircle className="w-8 h-8 text-emerald-600 dark:text-emerald-300" />
                    </div>
                </div>

                <div className="panel panel-body">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-emerald-700 dark:text-emerald-300 font-medium">Attendance Rate</p>
                            <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-300">{reportStats.percentage.toFixed(1)}%</p>
                        </div>
                        <TrendingUp className="w-8 h-8 text-emerald-600 dark:text-emerald-300" />
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className="panel panel-muted p-6 border border-gray-100 dark:border-gray-700 rounded-lg">
                <div className="flex items-center gap-2 mb-4">
                    <Filter className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    <h3 className="font-semibold">Filters</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Class
                        </label>
                        <select
                            value={selectedClass}
                            onChange={(e) => setSelectedClass(e.target.value)}
                            className="form-select"
                        >
                            <option value="">All Classes</option>
                            {classes.map((cls) => (
                                <option key={cls.id} value={cls.class_name}>
                                    {cls.class_name}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Start Date
                        </label>
                        <input
                            type="date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            className="form-input"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            End Date
                        </label>
                        <input
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            className="form-input"
                        />
                    </div>

                    <div className="flex items-end">
                        <button
                            onClick={exportToExcel}
                            disabled={exporting || filteredAttendance.length === 0}
                            className="btn btn-primary w-full"
                        >
                            <Download className="w-4 h-4" />
                            {exporting ? 'Exporting...' : 'Export'}
                        </button>
                    </div>
                </div>
            </div>

            {/* Attendance Table */}
            <div className="table-wrap">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="table-head">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                    Date
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                    Class
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                    Status
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                    Confidence
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                            {filteredAttendance.length > 0 ? (
                                filteredAttendance.map((record, index) => (
                                    <tr key={index} className="table-row">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                            {new Date(record.date).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                            {record.class_name}
                                        </td>
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
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="4" className="px-6 py-12 text-center">
                                        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                                        <p className="text-gray-500 dark:text-gray-400">
                                            No attendance records found
                                        </p>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AttendanceView;
