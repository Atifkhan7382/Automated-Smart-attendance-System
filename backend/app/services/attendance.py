from typing import List, Dict, Optional
from datetime import datetime, date
import pandas as pd
import os
import json
import shutil
from app.models.database import DatabaseManager
from app.services.student_management import StudentManagementService

class AttendanceService:
    """Service for managing attendance records"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.student_service = StudentManagementService()
    
    async def save_attendance(self, class_name: str, image_path: str, present_students: List[Dict], 
                            absent_students: List[Dict], total_faces_detected: int) -> int:
        """Save attendance record to database - OPTIMIZED VERSION"""
        try:
            current_date = date.today().isoformat()
            current_time = datetime.now().isoformat()
            
            # OPTIMIZATION 1: Use batch insert for better performance
            conn = self.db.get_db_connection()
            cursor = conn.cursor()
            
            try:
                # Create attendance record
                attendance_query = """
                    INSERT INTO attendance_records (class_name, date, image_path, total_faces_detected, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """
                
                cursor.execute(attendance_query, 
                    (class_name, current_date, image_path, total_faces_detected, current_time))
                attendance_id = cursor.lastrowid or 0
                
                # OPTIMIZATION 2: Batch insert all student attendance records
                student_attendance_query = """
                    INSERT INTO student_attendance (attendance_record_id, student_id, status, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """
                
                # Prepare all records for batch insert
                all_records = []
                
                # Add present students
                for student in present_students:
                    all_records.append((
                        attendance_id, 
                        student['student_id'], 
                        'present', 
                        student.get('confidence', 0.0), 
                        current_time
                    ))
                
                # Add absent students
                for student in absent_students:
                    all_records.append((
                        attendance_id, 
                        student['student_id'], 
                        'absent', 
                        0.0, 
                        current_time
                    ))
                
                # OPTIMIZATION 3: Execute batch insert
                cursor.executemany(student_attendance_query, all_records)
                
                # Commit all changes at once
                conn.commit()
                
                print(f"Saved attendance record {attendance_id} for class {class_name} with {len(all_records)} student records")
                return attendance_id
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
            
        except Exception as e:
            print(f"Error saving attendance: {e}")
            raise e
    
    async def get_attendance_by_id(self, attendance_id: int) -> Optional[Dict]:
        """Get attendance record by ID"""
        try:
            query = """
                SELECT ar.*, 
                       COUNT(sa.id) as total_records,
                       COUNT(CASE WHEN sa.status = 'present' THEN 1 END) as present_count
                FROM attendance_records ar
                LEFT JOIN student_attendance sa ON ar.id = sa.attendance_record_id
                WHERE ar.id = ?
                GROUP BY ar.id
            """
            results = self.db.execute_query(query, (attendance_id,))
            
            if results:
                record = results[0]
                # Get detailed student attendance
                student_query = """
                    SELECT sa.*, s.name
                    FROM student_attendance sa
                    JOIN students s ON sa.student_id = s.student_id
                    WHERE sa.attendance_record_id = ?
                    ORDER BY s.name
                """
                students = self.db.execute_query(student_query, (attendance_id,))
                
                record['students'] = students
                return record
            
            return None
            
        except Exception as e:
            print(f"Error getting attendance by ID: {e}")
            return None
    
    async def generate_report(self, class_name: Optional[str] = None,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> Dict:
        """Generate comprehensive attendance report - OPTIMIZED VERSION"""
        try:
            # OPTIMIZATION 1: Use single optimized query for all data
            optimized_query = """
                WITH attendance_summary AS (
                    SELECT 
                        s.student_id,
                        s.name,
                        s.class_name,
                        COUNT(sa.id) as total_sessions,
                        COUNT(CASE WHEN sa.status = 'present' THEN 1 END) as present_sessions,
                        ROUND(
                            CAST(COUNT(CASE WHEN sa.status = 'present' THEN 1 END) AS FLOAT) / 
                            NULLIF(COUNT(sa.id), 0) * 100, 2
                        ) as attendance_percentage
                    FROM students s
                    LEFT JOIN student_attendance sa ON s.student_id = sa.student_id
                    LEFT JOIN attendance_records ar ON sa.attendance_record_id = ar.id
                    WHERE 1=1
            """
            
            params = []
            
            if class_name:
                optimized_query += " AND s.class_name = ?"
                params.append(class_name)
            
            if start_date:
                optimized_query += " AND ar.date >= ?"
                params.append(start_date)
            
            if end_date:
                optimized_query += " AND ar.date <= ?"
                params.append(end_date)
            
            optimized_query += """
                    GROUP BY s.student_id
                ),
                session_summary AS (
                    SELECT 
                        ar.id,
                        ar.class_name,
                        ar.date,
                        ar.created_at,
                        ar.total_faces_detected,
                        COUNT(sa.id) as total_records,
                        COUNT(CASE WHEN sa.status = 'present' THEN 1 END) as present_count,
                        ROUND(
                            CAST(COUNT(CASE WHEN sa.status = 'present' THEN 1 END) AS FLOAT) / 
                            NULLIF(COUNT(sa.id), 0) * 100, 2
                        ) as attendance_percentage
                    FROM attendance_records ar
                    LEFT JOIN student_attendance sa ON ar.id = sa.attendance_record_id
                    WHERE 1=1
            """
            
            if class_name:
                optimized_query += " AND ar.class_name = ?"
                params.append(class_name)
            
            if start_date:
                optimized_query += " AND ar.date >= ?"
                params.append(start_date)
            
            if end_date:
                optimized_query += " AND ar.date <= ?"
                params.append(end_date)
            
            optimized_query += """
                    GROUP BY ar.id
                    ORDER BY ar.created_at DESC
                    LIMIT 1000
                )
                SELECT 
                    'student' as type,
                    student_id,
                    name,
                    class_name,
                    total_sessions,
                    present_sessions,
                    attendance_percentage,
                    NULL as session_id,
                    NULL as session_date,
                    NULL as session_created_at,
                    NULL as total_faces_detected,
                    NULL as session_total_records,
                    NULL as session_present_count,
                    NULL as session_attendance_percentage
                FROM attendance_summary
                UNION ALL
                SELECT 
                    'session' as type,
                    NULL as student_id,
                    NULL as name,
                    class_name,
                    NULL as total_sessions,
                    NULL as present_sessions,
                    NULL as attendance_percentage,
                    id as session_id,
                    date as session_date,
                    created_at as session_created_at,
                    total_faces_detected,
                    total_records as session_total_records,
                    present_count as session_present_count,
                    attendance_percentage as session_attendance_percentage
                FROM session_summary
                ORDER BY type, class_name, name, session_created_at DESC
            """
            
            # Execute optimized query
            results = self.db.execute_query(optimized_query, tuple(params))
            
            # OPTIMIZATION 2: Process results efficiently
            student_summary = []
            daily_records = []
            
            for row in results:
                if row['type'] == 'student':
                    student_summary.append({
                        'student_id': row['student_id'],
                        'name': row['name'],
                        'class_name': row['class_name'],
                        'total_sessions': row['total_sessions'],
                        'present_sessions': row['present_sessions'],
                        'attendance_percentage': row['attendance_percentage']
                    })
                elif row['type'] == 'session':
                    daily_records.append({
                        'id': row['session_id'],
                        'class_name': row['class_name'],
                        'date': row['session_date'],
                        'created_at': row['session_created_at'],
                        'total_faces_detected': row['total_faces_detected'],
                        'total_records': row['session_total_records'],
                        'present_count': row['session_present_count'],
                        'attendance_percentage': row['session_attendance_percentage']
                    })
            
            # Calculate overall statistics
            total_sessions = len(daily_records)
            total_students = len(student_summary)
            
            if student_summary:
                avg_attendance = sum(s['attendance_percentage'] or 0 for s in student_summary) / total_students
            else:
                avg_attendance = 0
            
            report = {
                'summary': {
                    'total_sessions': total_sessions,
                    'total_students': total_students,
                    'average_attendance_percentage': round(avg_attendance, 2),
                    'date_range': {
                        'start_date': start_date,
                        'end_date': end_date
                    },
                    'class_filter': class_name
                },
                'daily_records': daily_records,
                'student_summary': student_summary
            }
            
            return report
            
        except Exception as e:
            print(f"Error generating report: {e}")
            raise e
    
    async def get_attendance_records(self, class_name: Optional[str] = None,
                                   start_date: Optional[str] = None,
                                   end_date: Optional[str] = None,
                                   limit: int = 50) -> List[Dict]:
        """Get attendance records with optional filters"""
        try:
            query = """
                SELECT ar.*, 
                       COUNT(sa.id) as total_records,
                       COUNT(CASE WHEN sa.status = 'present' THEN 1 END) as present_count,
                       ROUND(
                           CAST(COUNT(CASE WHEN sa.status = 'present' THEN 1 END) AS FLOAT) / 
                           COUNT(sa.id) * 100, 2
                       ) as attendance_percentage
                FROM attendance_records ar
                LEFT JOIN student_attendance sa ON ar.id = sa.attendance_record_id
                WHERE 1=1
            """
            params = []
            
            if class_name:
                query += " AND ar.class_name = ?"
                params.append(class_name)
            
            if start_date:
                query += " AND ar.date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND ar.date <= ?"
                params.append(end_date)
            
            query += " GROUP BY ar.id ORDER BY ar.created_at DESC LIMIT ?"
            params.append(limit)
            
            results = self.db.execute_query(query, tuple(params))
            return results
            
        except Exception as e:
            print(f"Error getting attendance records: {e}")
            return []
    
    async def export_to_excel(self, class_name: Optional[str] = None,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> str:
        """Export attendance data to Excel file"""
        try:
            # Generate report data
            report = await self.generate_report(class_name, start_date, end_date)
            
            # Create Excel file
            os.makedirs("data/exports", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"attendance_report_{timestamp}.xlsx"
            filepath = f"data/exports/{filename}"
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Daily records sheet
                if report['daily_records']:
                    daily_df = pd.DataFrame(report['daily_records'])
                    daily_df.to_excel(writer, sheet_name='Daily Records', index=False)
                
                # Student summary sheet
                if report['student_summary']:
                    student_df = pd.DataFrame(report['student_summary'])
                    student_df.to_excel(writer, sheet_name='Student Summary', index=False)
                
                # Summary statistics sheet
                summary_data = [
                    ['Total Sessions', report['summary']['total_sessions']],
                    ['Total Students', report['summary']['total_students']],
                    ['Average Attendance %', report['summary']['average_attendance_percentage']],
                    ['Start Date', report['summary']['date_range']['start_date'] or 'All'],
                    ['End Date', report['summary']['date_range']['end_date'] or 'All'],
                    ['Class Filter', report['summary']['class_filter'] or 'All Classes']
                ]
                summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            print(f"Exported attendance report to {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            raise e
    
    async def get_statistics(self) -> Dict:
        """Get overall system statistics"""
        try:
            # Total students
            student_count_query = "SELECT COUNT(*) as total FROM students"
            student_result = self.db.execute_query(student_count_query)
            total_students = student_result[0]['total'] if student_result else 0
            
            # Total classes
            class_count_query = "SELECT COUNT(DISTINCT class_name) as total FROM students"
            class_result = self.db.execute_query(class_count_query)
            total_classes = class_result[0]['total'] if class_result else 0
            
            # Total attendance records
            record_count_query = "SELECT COUNT(*) as total FROM attendance_records"
            record_result = self.db.execute_query(record_count_query)
            total_records = record_result[0]['total'] if record_result else 0
            
            # Average attendance percentage (last 30 days)
            avg_attendance_query = """
                SELECT 
                    ROUND(
                        CAST(COUNT(CASE WHEN sa.status = 'present' THEN 1 END) AS FLOAT) / 
                        COUNT(sa.id) * 100, 2
                    ) as avg_percentage
                FROM student_attendance sa
                JOIN attendance_records ar ON sa.attendance_record_id = ar.id
                WHERE ar.date >= date('now', '-30 days')
            """
            avg_result = self.db.execute_query(avg_attendance_query)
            avg_attendance = avg_result[0]['avg_percentage'] if avg_result and avg_result[0]['avg_percentage'] else 0
            
            # Class-wise statistics
            class_stats_query = """
                SELECT 
                    s.class_name,
                    COUNT(DISTINCT s.student_id) as total_students,
                    COUNT(DISTINCT ar.id) as total_sessions,
                    ROUND(
                        CAST(COUNT(CASE WHEN sa.status = 'present' THEN 1 END) AS FLOAT) / 
                        COUNT(sa.id) * 100, 2
                    ) as attendance_percentage
                FROM students s
                LEFT JOIN student_attendance sa ON s.student_id = sa.student_id
                LEFT JOIN attendance_records ar ON sa.attendance_record_id = ar.id
                WHERE ar.date >= date('now', '-30 days') OR ar.date IS NULL
                GROUP BY s.class_name
                ORDER BY s.class_name
            """
            class_stats = self.db.execute_query(class_stats_query)
            
            # Recent sessions
            recent_sessions_query = """
                SELECT ar.*, 
                       COUNT(sa.id) as total_records,
                       COUNT(CASE WHEN sa.status = 'present' THEN 1 END) as present_count
                FROM attendance_records ar
                LEFT JOIN student_attendance sa ON ar.id = sa.attendance_record_id
                GROUP BY ar.id
                ORDER BY ar.created_at DESC
                LIMIT 5
            """
            recent_sessions = self.db.execute_query(recent_sessions_query)
            
            return {
                'total_students': total_students,
                'total_classes': total_classes,
                'total_attendance_records': total_records,
                'average_attendance_percentage': avg_attendance,
                'class_statistics': class_stats,
                'recent_sessions': recent_sessions
            }
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {
                'total_students': 0,
                'total_classes': 0,
                'total_attendance_records': 0,
                'average_attendance_percentage': 0,
                'class_statistics': [],
                'recent_sessions': []
            }
    
    async def delete_attendance_record(self, record_id: int) -> bool:
        """Delete a specific attendance record and all related student attendance"""
        try:
            # First delete all student attendance records for this attendance record
            delete_student_attendance_query = "DELETE FROM student_attendance WHERE attendance_record_id = ?"
            self.db.execute_update(delete_student_attendance_query, (record_id,))
            
            # Then delete the attendance record itself
            delete_record_query = "DELETE FROM attendance_records WHERE id = ?"
            affected_rows = self.db.execute_update(delete_record_query, (record_id,))
            
            if affected_rows > 0:
                print(f"Deleted attendance record {record_id}")
                return True
            else:
                print(f"No attendance record found with id {record_id}")
                return False
            
        except Exception as e:
            print(f"Error deleting attendance record {record_id}: {e}")
            return False
    
    async def generate_session_report(self, attendance_id: int) -> Dict:
        """Generate detailed session attendance report with student names and presence status"""
        try:
            # Get attendance record details
            record = await self.get_attendance_by_id(attendance_id)
            
            if not record:
                raise ValueError(f"Attendance record with ID {attendance_id} not found")
            
            # Get all students enrolled in the class (enrollment-based), fallback to class_name
            enrolled_students = await self.student_service.get_enrolled_students(record['class_name'])
            if enrolled_students:
                all_students = enrolled_students
            else:
                class_students_query = """
                    SELECT student_id, name
                    FROM students 
                    WHERE class_name = ?
                    ORDER BY name
                """
                all_students = self.db.execute_query(class_students_query, (record['class_name'],))
            
            # Create a mapping of student_id to attendance status
            attendance_map = {}
            for student in record['students']:
                attendance_map[student['student_id']] = {
                    'status': student['status'],
                    'confidence': student.get('confidence', 0.0)
                }
            
            # Create session report with all students
            session_students = []
            for student in all_students:
                student_id = student['student_id']
                if student_id in attendance_map:
                    # Student has attendance record
                    attendance_info = attendance_map[student_id]
                    session_students.append({
                        'student_id': student_id,
                        'name': student['name'],
                        'roll_number': '',  # Not available in current schema
                        'status': attendance_info['status'],
                        'present': attendance_info['status'] == 'present',
                        'confidence': attendance_info['confidence'],
                        'marked': True
                    })
                else:
                    # Student not marked (should be considered absent)
                    session_students.append({
                        'student_id': student_id,
                        'name': student['name'],
                        'roll_number': '',  # Not available in current schema
                        'status': 'absent',
                        'present': False,
                        'confidence': 0.0,
                        'marked': False
                    })
            
            # Calculate summary statistics
            total_students = len(session_students)
            present_count = sum(1 for s in session_students if s['present'])
            absent_count = total_students - present_count
            
            session_report = {
                'session_info': {
                    'attendance_id': attendance_id,
                    'class_name': record['class_name'],
                    'date': record['date'],
                    'created_at': record['created_at'],
                    'image_path': record.get('image_path', ''),
                    'total_faces_detected': record.get('total_faces_detected', 0)
                },
                'summary': {
                    'total_students': total_students,
                    'present_count': present_count,
                    'absent_count': absent_count,
                    'attendance_percentage': round((present_count / total_students * 100), 2) if total_students > 0 else 0
                },
                'students': session_students
            }
            
            return session_report
            
        except Exception as e:
            print(f"Error generating session report: {e}")
            raise e
    
    async def export_session_to_excel(self, attendance_id: int) -> str:
        """Export session attendance report to Excel file"""
        try:
            # Generate session report
            session_report = await self.generate_session_report(attendance_id)
            
            # Create Excel file
            os.makedirs("data/exports", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            class_name = session_report['session_info']['class_name']
            date_str = session_report['session_info']['date']
            filename = f"session_attendance_{class_name}_{date_str}_{attendance_id}_{timestamp}.xlsx"
            filepath = f"data/exports/{filename}"
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Combined sheet with summary and student details
                combined_data = []
                
                # Add session summary at the top
                combined_data.append(['=== SESSION SUMMARY ===', ''])
                combined_data.append(['Session ID', session_report['session_info']['attendance_id']])
                combined_data.append(['Class Name', session_report['session_info']['class_name']])
                combined_data.append(['Date', session_report['session_info']['date']])
                combined_data.append(['Session Time', session_report['session_info']['created_at']])
                combined_data.append(['Image Path', session_report['session_info'].get('image_path', '')])
                combined_data.append(['Total Students', session_report['summary']['total_students']])
                combined_data.append(['Present', session_report['summary']['present_count']])
                combined_data.append(['Absent', session_report['summary']['absent_count']])
                combined_data.append(['Attendance Percentage', f"{session_report['summary']['attendance_percentage']}%"])
                combined_data.append(['', ''])  # Empty row
                
                # Add student details section
                combined_data.append(['=== STUDENT ATTENDANCE DETAILS ===', ''])
                combined_data.append(['Student ID', 'Name', 'Status', 'Present', 'Confidence Score'])
                
                for student in session_report['students']:
                    combined_data.append([
                        student['student_id'],
                        student['name'],
                        student['status'].title(),
                        'Yes' if student['present'] else 'No',
                        f"{student['confidence']:.2f}" if student['confidence'] > 0 else 'N/A'
                    ])
                
                # Create DataFrame and export
                combined_df = pd.DataFrame(combined_data)
                combined_df.to_excel(writer, sheet_name='Attendance Report', index=False, header=False)
                
                # Also create separate sheets for detailed view
                summary_data = [
                    ['Session ID', session_report['session_info']['attendance_id']],
                    ['Class Name', session_report['session_info']['class_name']],
                    ['Date', session_report['session_info']['date']],
                    ['Session Time', session_report['session_info']['created_at']],
                    ['Image Path', session_report['session_info'].get('image_path', '')],
                    ['Total Students', session_report['summary']['total_students']],
                    ['Present', session_report['summary']['present_count']],
                    ['Absent', session_report['summary']['absent_count']],
                    ['Attendance Percentage', f"{session_report['summary']['attendance_percentage']}%"]
                ]
                summary_df = pd.DataFrame(summary_data, columns=['Field', 'Value'])
                summary_df.to_excel(writer, sheet_name='Summary Only', index=False)
                
                # Student attendance sheet
                student_data = []
                for student in session_report['students']:
                    student_data.append({
                        'Student ID': student['student_id'],
                        'Name': student['name'],
                        'Status': student['status'].title(),
                        'Present': 'Yes' if student['present'] else 'No',
                        'Confidence': f"{student['confidence']:.2f}" if student['confidence'] > 0 else 'N/A'
                    })
                
                students_df = pd.DataFrame(student_data)
                students_df.to_excel(writer, sheet_name='Students Only', index=False)
            
            print(f"Exported session report to {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error exporting session to Excel: {e}")
            raise e

    async def clear_all_history(self) -> bool:
        """Clear all attendance history but keep students"""
        try:
            # Delete all student attendance records
            self.db.execute_update("DELETE FROM student_attendance")
            
            # Delete all attendance records
            self.db.execute_update("DELETE FROM attendance_records")
            
            # Clean up attendance images directory
            import shutil
            attendance_images_dir = "data/attendance_images"
            if os.path.exists(attendance_images_dir):
                shutil.rmtree(attendance_images_dir)
                os.makedirs(attendance_images_dir, exist_ok=True)
            
            # Clean up exports directory
            exports_dir = "data/exports"
            if os.path.exists(exports_dir):
                shutil.rmtree(exports_dir)
                os.makedirs(exports_dir, exist_ok=True)
            
            print("Cleared all attendance history")
            return True
            
        except Exception as e:
            print(f"Error clearing attendance history: {e}")
            return False