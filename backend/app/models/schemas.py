from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

class AttendanceStatus(str, Enum):
    present = "present"
    absent = "absent"

class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    student_id: str = Field(..., min_length=1, max_length=50)
    class_name: str = Field(..., min_length=1, max_length=50)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    class_name: Optional[str] = Field(None, min_length=1, max_length=50)

class StudentResponse(StudentBase):
    id: int
    image_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AttendanceRecord(BaseModel):
    session_id: str
    student_id: str
    name: str
    status: AttendanceStatus
    confidence: Optional[float] = 0.0
    timestamp: datetime

class AttendanceSession(BaseModel):
    session_id: str
    class_name: str
    image_path: str
    total_faces_detected: int
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class AttendanceResult(BaseModel):
    attendance_id: str
    class_name: str
    timestamp: datetime
    present: List[Dict[str, Any]]
    absent: List[Dict[str, Any]]
    total_students: int
    total_faces_detected: int
    attendance_percentage: float

class AttendanceReport(BaseModel):
    daily_report: List[Dict[str, Any]]
    student_summary: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    filters: Dict[str, Any]

class SystemStatistics(BaseModel):
    total_students: int
    total_sessions: int
    total_classes: int
    recent_attendance_rate: float
    last_session: Optional[Dict[str, Any]] = None
    class_statistics: List[Dict[str, Any]]

class FaceRecognitionParams(BaseModel):
    tolerance: Optional[float] = Field(0.6, ge=0.1, le=1.0)
    model: Optional[str] = Field("hog", pattern="^(hog|cnn)$")

class SearchRequest(BaseModel):
    search_term: str = Field(..., min_length=1)
    
class ReportRequest(BaseModel):
    class_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        if v and info.data.get('start_date'):
            if v < info.data['start_date']:
                raise ValueError('end_date must be after start_date')
        return v

class AttendanceMarkRequest(BaseModel):
    class_name: str = Field(..., min_length=1)
    
class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)