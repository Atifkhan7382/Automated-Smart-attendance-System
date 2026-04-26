import React, { useState, useEffect } from 'react';
import { Download, Calendar, Filter, BarChart3, Trash2 } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { attendanceAPI, studentAPI } from '../services/api';

const Reports = () => {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [exporting, setExporting] = useState(false);
  
  // Filter state
  const [filters, setFilters] = useState({
    class_name: '',
    start_date: '',
    end_date: '',
  });
  
  const [availableClasses, setAvailableClasses] = useState([]);

  useEffect(() => {
    fetchAvailableClasses();
    generateReport();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchAvailableClasses = async () => {
    try {
      const students = await studentAPI.getStudents();
      const classes = [...new Set(students.map((s) => s.class_name))];
      setAvailableClasses(classes);
    } catch (err) {
      console.error('Error fetching classes:', err);
    }
  };

  const generateReport = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        ...(filters.class_name && { class_name: filters.class_name }),
        ...(filters.start_date && { start_date: filters.start_date }),
        ...(filters.end_date && { end_date: filters.end_date }),
      };
      
      const data = await attendanceAPI.getReport(params);
      setReportData(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate report');
      console.error('Error generating report:', err);
    } finally {
      setLoading(false);
    }
  };

  const exportReport = async () => {
    try {
      setExporting(true);
      
      const params = {
        ...(filters.class_name && { class_name: filters.class_name }),
        ...(filters.start_date && { start_date: filters.start_date }),
        ...(filters.end_date && { end_date: filters.end_date }),
      };
      
      const response = await attendanceAPI.exportData(params);
      
      if (response.download_url) {
        // Create a temporary link to download the file
        const link = document.createElement('a');
        link.href = `${process.env.REACT_APP_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000'}${response.download_url}`;
        link.download = response.download_url.split('/').pop() || 'attendance_report.xlsx';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (err) {
      console.error('Error exporting report:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to export report';
      alert(errorMessage);
    } finally {
      setExporting(false);
    }
  };

  const exportSessionReport = async (attendanceId) => {
    try {
      setExporting(true);
      
      const response = await attendanceAPI.exportSessionAttendance(attendanceId);
      
      if (response.download_url) {
        // Create a temporary link to download the file
        const link = document.createElement('a');
        link.href = `${process.env.REACT_APP_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000'}${response.download_url}`;
        link.download = response.download_url.split('/').pop() || 'session_attendance.xlsx';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (err) {
      console.error('Error exporting session report:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to export session report';
      alert(errorMessage);
    } finally {
      setExporting(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({ class_name: '', start_date: '', end_date: '' });
  };

  const deleteAttendanceRecord = async (recordId) => {
    console.log('Attempting to delete record with ID:', recordId);
    
    if (!window.confirm('Are you sure you want to delete this attendance record? This action cannot be undone.')) {
      return;
    }

    try {
      const result = await attendanceAPI.deleteAttendanceRecord(recordId);
      console.log('Delete result:', result);
      alert('Attendance record deleted successfully!');
      generateReport(); // Refresh the report
    } catch (err) {
      console.error('Full error object:', err);
      console.error('Error response:', err.response);
      console.error('Error status:', err.response?.status);
      console.error('Error data:', err.response?.data);
      
      let errorMessage;
      if (err.response?.status === 422) {
        errorMessage = 'Validation error: The record ID might be invalid or the record might not exist.';
      } else if (err.response?.status === 404) {
        errorMessage = 'Record not found. It might have been already deleted.';
      } else {
        errorMessage = err.response?.data?.detail || err.message || 'Failed to delete attendance record';
      }
      alert(errorMessage);
    }
  };

  const attendanceTrend = (reportData?.daily_records || []).map((record) => ({
    date: new Date(record.date).toLocaleDateString(),
    attendance: Number(record.attendance_percentage || 0)
  }));

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="page-title">Attendance Reports</h2>
          <p className="page-subtitle">Generate and export attendance analytics</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={exportReport}
            disabled={exporting || !reportData}
            className="btn btn-primary"
          >
            {exporting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Exporting...
              </>
            ) : (
              <>
                <Download className="h-4 w-4" />
                Export Excel
              </>
            )}
          </button>
          <button
            onClick={async () => {
              if (window.confirm('Are you sure you want to delete ALL attendance history? This action cannot be undone.')) {
                try {
                  await attendanceAPI.clearAllHistory();
                  alert('All attendance history cleared successfully!');
                  generateReport(); // Refresh the report
                } catch (err) {
                  console.error('Error clearing history:', err);
                  const errorMessage = err.response?.data?.detail || err.message || 'Failed to clear attendance history';
                  alert(errorMessage);
                }
              }
            }}
            className="btn btn-danger"
          >
            <Trash2 className="h-4 w-4" />
            Clear All History
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="panel panel-body">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Filter className="h-5 w-5" />
          Filters
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Class
            </label>
            <select
              value={filters.class_name}
              onChange={(e) => handleFilterChange('class_name', e.target.value)}
              className="form-select"
            >
              <option value="">All Classes</option>
              {availableClasses.map(className => (
                <option key={className} value={className}>{className}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => handleFilterChange('start_date', e.target.value)}
              className="form-input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              End Date
            </label>
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) => handleFilterChange('end_date', e.target.value)}
              className="form-input"
            />
          </div>
          <div className="flex items-end gap-2">
            <button
              onClick={generateReport}
              className="btn btn-primary flex-1"
            >
              Generate Report
            </button>
            <button
              onClick={clearFilters}
              className="btn btn-secondary"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Report Content */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg p-6">
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
          <button
            onClick={generateReport}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 dark:bg-red-600 dark:hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      ) : reportData ? (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="panel panel-body">
              <div className="flex items-center">
                <div className="action-icon">
                  <Calendar className="h-6 w-6" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Sessions</p>
                  <p className="text-2xl font-bold">{reportData.summary?.total_sessions || 0}</p>
                </div>
              </div>
            </div>
            <div className="panel panel-body">
              <div className="flex items-center">
                <div className="action-icon action-icon--highlight">
                  <BarChart3 className="h-6 w-6" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Students Tracked</p>
                  <p className="text-2xl font-bold">{reportData.summary?.total_students || 0}</p>
                </div>
              </div>
            </div>
            <div className="panel panel-body">
              <div className="flex items-center">
                <div className="action-icon action-icon--warm">
                  <BarChart3 className="h-6 w-6" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Attendance</p>
                  <p className="text-2xl font-bold">
                    {reportData.summary?.average_attendance_percentage?.toFixed(1) || 0}%
                  </p>
                </div>
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

          {/* Daily Records */}
          <div className="panel">
            <div className="panel-header">
              <h3 className="text-lg font-semibold">Daily Attendance Records</h3>
            </div>
            <div className="panel-body">
              {reportData.daily_records && reportData.daily_records.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="table-head">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Class
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Present
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Total
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Attendance %
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                      {reportData.daily_records.map((record) => (
                        <tr key={record.id} className="table-row">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">
                            {new Date(record.date).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">
                            {record.class_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {record.present_count}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {record.total_records}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            <span className={`badge ${(record.attendance_percentage || 0) >= 80
                              ? 'badge-success'
                              : (record.attendance_percentage || 0) >= 60
                              ? 'badge-warning'
                              : 'badge-danger'}`}>
                              {record.attendance_percentage?.toFixed(1) || 0}%
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => exportSessionReport(record.id)}
                                className="btn btn-secondary text-sm"
                                title="Export session attendance report"
                              >
                                <Download className="h-4 w-4" />
                                Export Session
                              </button>
                              <button
                                onClick={() => deleteAttendanceRecord(record.id)}
                                className="btn btn-danger text-sm"
                                title="Delete this attendance record"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">No attendance records found</p>
              )}
            </div>
          </div>

          {/* Student Summary */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border dark:border-gray-700">
            <div className="px-6 py-4 border-b dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Student Attendance Summary</h3>
            </div>
            <div className="p-6">
              {reportData.student_summary && reportData.student_summary.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Student
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Student ID
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Class
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Sessions Present
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Total Sessions
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Attendance %
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                      {reportData.student_summary.map((student) => (
                        <tr key={student.student_id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-200">
                            {student.name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {student.student_id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {student.class_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {student.present_sessions}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {student.total_sessions}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              (student.attendance_percentage || 0) >= 80
                                ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400'
                                : (student.attendance_percentage || 0) >= 60
                                ? 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-400'
                                : 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-400'
                            }`}>
                              {student.attendance_percentage?.toFixed(1) || 0}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">No student data found</p>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border dark:border-gray-700 p-12 text-center">
          <BarChart3 className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">Click "Generate Report" to view attendance analytics</p>
        </div>
      )}
    </div>
  );
};

export default Reports;
