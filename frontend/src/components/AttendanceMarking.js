import React, { useState, useRef } from 'react';
import { Camera, Upload, Users, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { attendanceAPI } from '../services/api';
import { refreshAttendanceData } from '../utils/attendanceHelpers';
import QualityErrorModal from './QualityErrorModal';
import AttendanceVerificationModal from './AttendanceVerificationModal';

const AttendanceMarking = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [className, setClassName] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [qualityError, setQualityError] = useState(null);
  const [showQualityModal, setShowQualityModal] = useState(false);
  const [showVerificationModal, setShowVerificationModal] = useState(false);
  const [pendingVerifications, setPendingVerifications] = useState([]);
  const [attendanceId, setAttendanceId] = useState(null);
  const fileInputRef = useRef(null);


  const handleImageSelect = (file) => {
    setSelectedImage(file);
    setResult(null);
    setError(null);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target?.result);
    };
    reader.readAsDataURL(file);
  };

  const handleFileInput = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleImageSelect(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      handleImageSelect(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedImage || !className.trim()) {
      alert('Please select an image and enter a class name');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setQualityError(null);

      const formData = new FormData();
      formData.append('class_name', className.trim());
      formData.append('file', selectedImage);

      const data = await attendanceAPI.markAttendance(formData);
      setResult(data);
      setAttendanceId(data.attendance_id);

      // Check for pending verifications
      console.log('Attendance response:', data);
      console.log('Has pending verifications:', data.has_pending_verifications);
      console.log('Pending verifications:', data.pending_verifications);

      if (data.has_pending_verifications && data.pending_verifications && data.pending_verifications.length > 0) {
        console.log('Setting pending verifications:', data.pending_verifications);
        setPendingVerifications(data.pending_verifications);
        setShowVerificationModal(true);
      }
    } catch (err) {
      // Check if it's a quality error (HTTP 422)
      if (err.response?.status === 422) {
        const errorDetail = err.response?.data?.detail;

        // Check if it's a structured quality error
        if (typeof errorDetail === 'object' && errorDetail.error) {
          setQualityError(errorDetail);
          setShowQualityModal(true);
        } else {
          // Fallback for simple error messages
          setError(typeof errorDetail === 'string' ? errorDetail : 'Image quality too low');
        }
      } else {
        setError(err.response?.data?.detail || 'Failed to process attendance');
      }
      console.error('Error marking attendance:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerificationComplete = async () => {
    // Refresh attendance results after verification
    console.log('Verification complete! Reloading attendance data...');
    console.log('Current result before refresh:', result);
    console.log('Attendance ID:', attendanceId);

    const updatedData = await refreshAttendanceData(attendanceId);
    console.log('Updated data from refresh:', updatedData);

    if (updatedData) {
      // Merge updated data with existing result, ensuring we update the counts
      const newResult = {
        ...result,
        present: updatedData.present,
        absent: updatedData.absent,
        attendance_percentage: updatedData.attendance_percentage,
        total_students: updatedData.present.length + updatedData.absent.length
      };

      console.log('New result after merge:', newResult);
      setResult(newResult);
      console.log('Attendance data refreshed successfully');
    } else {
      console.error('Failed to get updated data');
    }
  };


  const resetForm = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setClassName('');
    setResult(null);
    setError(null);
    setQualityError(null);
    setShowQualityModal(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleQualityModalClose = () => {
    setShowQualityModal(false);
    // Keep the image and form data so user can try again
  };

  return (
    <>
      {/* Quality Error Modal */}
      <QualityErrorModal
        isOpen={showQualityModal}
        onClose={handleQualityModalClose}
        errorData={qualityError}
      />

      {/* Verification Modal */}
      <AttendanceVerificationModal
        isOpen={showVerificationModal}
        onClose={() => setShowVerificationModal(false)}
        verifications={pendingVerifications}
        attendanceId={attendanceId}
        onVerificationComplete={handleVerificationComplete}
      />

      <div className="space-y-6">
        <div>
          <h2 className="page-title mb-2">Mark Attendance</h2>
          <p className="page-subtitle">Upload a classroom photo to automatically mark attendance</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upload Section */}
          <div className="panel panel-body">
            <h3 className="text-lg font-semibold mb-4">Upload Classroom Photo</h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Class Name
                </label>
                <input
                  type="text"
                  value={className}
                  onChange={(e) => setClassName(e.target.value)}
                  placeholder="Enter class name (e.g., CS101, Math-A, etc.)"
                  className="form-input"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Classroom Photo
                </label>

                {!imagePreview ? (
                  <div
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    className="upload-area p-8 text-center cursor-pointer"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <Upload className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-600 dark:text-gray-300 mb-2">
                      Drag and drop an image here, or click to select
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Supports JPG, PNG, GIF up to 10MB
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="relative">
                      <img
                        src={imagePreview}
                        alt="Selected classroom"
                        className="w-full h-64 object-cover rounded-lg"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          setSelectedImage(null);
                          setImagePreview(null);
                        }}
                        className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                      >
                        <XCircle className="h-4 w-4" />
                      </button>
                    </div>
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="btn btn-secondary w-full"
                    >
                      Choose Different Image
                    </button>
                  </div>
                )}

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileInput}
                  className="hidden"
                />
              </div>

              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={loading || !selectedImage || !className.trim()}
                  className="btn btn-primary flex-1"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <Camera className="h-4 w-4" />
                      Mark Attendance
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={resetForm}
                  className="btn btn-secondary"
                >
                  Reset
                </button>
              </div>
            </form>

            {error && (
              <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg">
                <p className="text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}
          </div>

          {/* Results Section */}
          <div className="panel panel-body">
            <h3 className="text-lg font-semibold mb-4">Attendance Results</h3>

            {!result ? (
              <div className="text-center py-12">
                <Users className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">Upload a classroom photo to see attendance results</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Summary */}
                <div className="panel panel-muted p-4 rounded-lg">
                  <div className="grid grid-cols-2 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{result.present?.length || 0}</p>
                      <p className="text-sm page-subtitle">Present</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-red-600 dark:text-red-400">{result.absent?.length || 0}</p>
                      <p className="text-sm page-subtitle">Absent</p>
                    </div>
                  </div>
                  <div className="mt-4 text-center">
                    <p className="text-lg font-semibold">
                      {result.attendance_percentage?.toFixed(1) || 0}% Attendance
                    </p>
                    <p className="text-sm page-subtitle">
                      {result.total_faces_detected || 0} faces detected in image
                    </p>
                    {result.has_pending_verifications && (
                      <div className="mt-3">
                        <button
                          onClick={() => setShowVerificationModal(true)}
                          className="btn btn-secondary"
                        >
                          <AlertCircle className="h-4 w-4" />
                          {pendingVerifications.length} face{pendingVerifications.length !== 1 ? 's' : ''} need verification
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Present Students */}
                {result.present && result.present.length > 0 && (
                  <div>
                    <h4 className="font-medium text-emerald-700 dark:text-emerald-400 mb-3 flex items-center gap-2">
                      <CheckCircle className="h-4 w-4" />
                      Present Students ({result.present.length})
                    </h4>
                    <div className="space-y-2">
                      {result.present.map((student) => (
                        <div key={student.student_id} className="flex justify-between items-center p-3 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg">
                          <div>
                            <p className="font-medium">{student.name}</p>
                            <p className="text-sm page-subtitle">{student.student_id}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-emerald-700 dark:text-emerald-400">
                              {(student.confidence * 100).toFixed(1)}% confidence
                            </p>
                            {student.quality_score && (
                              <p className="text-xs page-subtitle">
                                Quality: {(student.quality_score * 100).toFixed(0)}%
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Absent Students */}
                {result.absent && result.absent.length > 0 && (
                  <div>
                    <h4 className="font-medium text-red-700 dark:text-red-400 mb-3 flex items-center gap-2">
                      <XCircle className="h-4 w-4" />
                      Absent Students ({result.absent.length})
                    </h4>
                    <div className="space-y-2">
                      {result.absent.map((student) => (
                        <div key={student.student_id} className="flex justify-between items-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                          <div>
                            <p className="font-medium">{student.name}</p>
                            <p className="text-sm page-subtitle">{student.student_id}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="text-xs page-subtitle text-center">
                  Attendance marked on {new Date(result.timestamp).toLocaleString()}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default AttendanceMarking;
