import React, { useState, useEffect } from 'react';
import { Users, Calendar, TrendingUp, Clock } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { statsAPI } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      const data = await statsAPI.getStatistics();
      setStats(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch statistics');
      console.error('Error fetching statistics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg p-4">
        <p className="text-red-600 dark:text-red-400">{error}</p>
        <button
          onClick={fetchStatistics}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 dark:bg-red-600 dark:hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  const attendanceByClass = (stats?.class_statistics || []).map((item) => ({
    name: item.class_name,
    attendance: Number(item.attendance_percentage || 0)
  }));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="page-title mb-2">Dashboard</h2>
        <p className="page-subtitle">Overview of your attendance system</p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="panel panel-body">
          <div className="flex items-center">
            <div className="action-icon">
              <Users className="h-6 w-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Students</p>
              <p className="text-2xl font-bold">{stats?.total_students || 0}</p>
            </div>
          </div>
        </div>

        <div className="panel panel-body">
          <div className="flex items-center">
            <div className="action-icon action-icon--highlight">
              <Calendar className="h-6 w-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Classes</p>
              <p className="text-2xl font-bold">{stats?.total_classes || 0}</p>
            </div>
          </div>
        </div>

        <div className="panel panel-body">
          <div className="flex items-center">
            <div className="action-icon action-icon--warm">
              <Clock className="h-6 w-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Sessions</p>
              <p className="text-2xl font-bold">{stats?.total_attendance_records || 0}</p>
            </div>
          </div>
        </div>

        <div className="panel panel-body">
          <div className="flex items-center">
            <div className="action-icon action-icon--highlight">
              <TrendingUp className="h-6 w-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Attendance</p>
              <p className="text-2xl font-bold">
                {stats?.average_attendance_percentage?.toFixed(1) || 0}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Attendance Rate Chart */}
      <div className="panel">
        <div className="panel-header">
          <h3 className="text-lg font-semibold">Attendance Rate by Class</h3>
        </div>
        <div className="panel-body">
          {attendanceByClass.length > 0 ? (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={attendanceByClass} margin={{ top: 10, right: 16, left: 0, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e1e6ee" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} interval={0} angle={-18} textAnchor="end" height={60} />
                  <YAxis domain={[0, 100]} tickFormatter={(value) => `${value}%`} />
                  <Tooltip formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Attendance']} />
                  <Bar dataKey="attendance" fill="#2a9d8f" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-center py-8">No class data available</p>
          )}
        </div>
      </div>

      {/* Class Statistics */}
      <div className="panel">
        <div className="panel-header">
          <h3 className="text-lg font-semibold">Class Statistics</h3>
        </div>
        <div className="panel-body">
          {stats?.class_statistics && stats.class_statistics.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="table-head">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Class Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Students
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Sessions
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Attendance Rate
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {stats.class_statistics.map((classStats, index) => (
                    <tr key={index} className="table-row">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-200">
                        {classStats.class_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {classStats.total_students}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {classStats.total_sessions}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        <span className={`badge ${(classStats.attendance_percentage || 0) >= 80
                          ? 'badge-success'
                          : (classStats.attendance_percentage || 0) >= 60
                          ? 'badge-warning'
                          : 'badge-danger'} `}>
                          {classStats.attendance_percentage?.toFixed(1) || 0}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-center py-8">No class data available</p>
          )}
        </div>
      </div>

      {/* Recent Sessions */}
      <div className="panel">
        <div className="panel-header">
          <h3 className="text-lg font-semibold">Recent Sessions</h3>
        </div>
        <div className="panel-body">
          {stats?.recent_sessions && stats.recent_sessions.length > 0 ? (
            <div className="space-y-4">
              {stats.recent_sessions.map((session) => (
                <div key={session.id} className="flex items-center justify-between p-4 panel panel-muted rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{session.class_name}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{new Date(session.date).toLocaleDateString()}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {session.present_count}/{session.total_records} Present
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {session.attendance_percentage?.toFixed(1) || 0}% Attendance
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-center py-8">No recent sessions</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
