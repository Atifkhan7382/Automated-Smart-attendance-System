// Helper function to refresh attendance data after verification
export const refreshAttendanceData = async (attendanceId) => {
    try {
        console.log('Fetching attendance data for ID:', attendanceId);
        const response = await fetch(`http://localhost:8000/api/attendance/session/${attendanceId}`);
        console.log('Response status:', response.status);

        if (response.ok) {
            const updatedData = await response.json();
            console.log('Received data:', updatedData);
            console.log('Students array:', updatedData.students);

            const result = {
                present: updatedData.students.filter(s => s.status === 'present').map(s => ({
                    student_id: s.student_id,
                    name: s.name,
                    confidence: s.confidence || 1.0
                })),
                absent: updatedData.students.filter(s => s.status === 'absent').map(s => ({
                    student_id: s.student_id,
                    name: s.name
                })),
                attendance_percentage: updatedData.summary.attendance_percentage
            };

            console.log('Transformed result:', result);
            return result;
        }
        return null;
    } catch (error) {
        console.error('Failed to refresh attendance data:', error);
        return null;
    }
};
