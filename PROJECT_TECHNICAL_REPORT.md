# AttendAI Technical Report

## 1. Project Overview

### Purpose of the system
AttendAI is an AI-powered attendance management system that uses face detection and recognition to mark student attendance from classroom images (manual) or camera feeds (automated). The system provides a web UI for teachers and students, REST APIs for programmatic interaction, and data export to Excel for reporting and audits.

### Problems it solves
- Manual attendance is slow, error-prone, and hard to audit at scale.
- Classroom images often contain multiple students at different distances; the system uses multi-scale detection and quality checks to improve accuracy.
- Teachers need a configurable, repeatable attendance workflow with reporting and auditability.

### Target users
- Teachers: create classes, enroll students, mark attendance (manual/automated), review reports, and verify ambiguous matches.
- Students: enroll using video, view attendance, download reports, join/leave classes.
- Admin or power users: manage students via CRUD endpoints and maintenance scripts.

### Operating environment
- Backend: Python 3.8+, FastAPI, SQLite, OpenCV, PyTorch, Ultralytics YOLO, InsightFace/DeepFace, optional GPU.
- Frontend: React 18, TailwindCSS, Axios.
- OS: Windows, Linux, macOS.

### Assumptions and constraints
- Student images/videos are stored in local disk paths (`data/student_images`, `data/student_videos`).
- SQLite is used for persistence by default.
- Face recognition accuracy depends on image quality, lighting, and enrollment image variety.
- GPU acceleration is optional but improves throughput.
- The system uses a single-process FastAPI app; long-running tasks are handled in-process.

## 2. System Architecture

### High-level architecture diagram (text)
- Client (Browser)
  - React UI (Teacher, Student, Shared components)
  - Axios API client
- Backend API (FastAPI)
  - Auth + JWT
  - Class/Student/Attendance services
  - Face recognition pipelines
  - Automation service (camera capture + scheduling)
  - Verification pipeline
  - SQLite persistence
- Storage
  - SQLite database (`data/attendance.db`)
  - Encodings (`data/encodings/*.pkl`)
  - Images/videos (`data/student_images`, `data/attendance_images`, `data/student_videos`)

### Module breakdown
- API Layer: request validation, authentication, routing.
- Service Layer: business logic for attendance, classes, students, automation, recognition.
- Utilities: face quality metrics, landmarks analysis, GPU utilities, verification management.
- Persistence: SQLite schema + adapter.
- Frontend: dashboards, settings, reports, attendance flows.

### Services and components
- FaceRecognitionService: legacy HOG/CNN recognition, image enhancement, caching.
- YOLOv8FaceRecognitionService: YOLO/InsightFace-based recognition pipeline and continual learning.
- AttendanceService: save attendance, reports, export to Excel.
- AutomationService: scheduled camera capture, quality gate, retry loop, attendance submission.
- StudentManagementService / ClassService / AuthService: domain CRUD and enrollment flows.
- VerificationManager: store and manage teacher verification records.

### Data flow between modules
- Manual attendance:
  - Frontend uploads image -> `/api/attendance/mark` -> quality checks -> recognition -> attendance save -> verification records -> response.
- Automated attendance:
  - AutomationService captures image -> quality assessment -> recognition -> AttendanceService save -> status updates.
- Student enrollment:
  - Student/teacher uploads video -> VideoProcessingService extracts frames -> YOLOv8FaceRecognitionService generates encodings -> save encodings.
- Reporting:
  - AttendanceService queries DB -> generates aggregated report -> Excel export.

### External dependencies
- Ultralytics YOLO for face detection.
- InsightFace (ArcFace) for embeddings.
- Optional DeepFace/face_recognition legacy path.
- OpenCV for IO and image processing.
- Pandas and openpyxl for Excel export.

### Technology stack with reasons
- FastAPI: async-friendly, OpenAPI docs, typed validation.
- React: component-based UI with good ecosystem.
- TailwindCSS: fast, consistent styling.
- SQLite: lightweight, local storage with minimal ops.
- YOLO + InsightFace: accurate detection and recognition, widely used.

## 3. Source Code Structure

### Folder hierarchy (top-level)
- backend/
  - app/ (FastAPI application)
  - data/ (settings, encodings, images, DB)
  - scripts/ (maintenance utilities)
  - tests/ (unit/integration tests)
  - requirements*.txt (dependencies)
- frontend/
  - src/ (React app)
  - public/ (static assets)
  - package.json (dependencies/scripts)
- data/ (repo-level data outputs)
- README.md, PROJECT_GUIDE.md

### File responsibilities (exhaustive inventory)

Backend core:
- [backend/app/main.py] API entrypoint, routers, core endpoints, startup init.
- [backend/app/api/deps.py] Auth dependency resolution for request context.
- [backend/app/api/endpoints/auth.py] Register/login/logout, password change.
- [backend/app/api/endpoints/teacher.py] Class management and class roster.
- [backend/app/api/endpoints/student.py] Student self-service flows.
- [backend/app/api/endpoints/students.py] Student CRUD, image/video enrollment.
- [backend/app/api/endpoints/settings.py] Settings persistence and rebuild encodings job.
- [backend/app/api/endpoints/optimized_attendance.py] Optimized attendance flow.
- [backend/app/api/endpoints/verification.py] Teacher verification flow.
- [backend/app/api/endpoints/attendance.py] (empty stub).
- [backend/app/api/endpoints/upload.py] (empty stub).
- [backend/app/models/database.py] SQLite schema + manager.
- [backend/app/models/schemas.py] Pydantic models for students/attendance/report.
- [backend/app/models/auth_schemas.py] Pydantic models for auth/classes.
- [backend/app/models/db_adapter.py] Database abstraction interface.
- [backend/app/models/firebase_database.py] Firestore-backed persistence.
- [backend/app/core/security.py] JWT, password hashing, invite codes.
- [backend/app/core/config.py] empty config placeholder.
- [backend/app/services/attendance.py] Attendance save/report/export flows.
- [backend/app/services/attendance_helper.py] Verification-related attendance updates.
- [backend/app/services/auth_service.py] Auth business logic.
- [backend/app/services/class_service.py] Class + enrollment business logic.
- [backend/app/services/student_management.py] Student CRUD and stats.
- [backend/app/services/automation.py] Scheduled attendance.
- [backend/app/services/face_recognition.py] Legacy face_recognition pipeline.
- [backend/app/services/yolov8_face_recognition.py] YOLO + InsightFace pipeline.
- [backend/app/services/optimized_attendance.py] Batch optimized attendance.
- [backend/app/services/continual_learning_methods.py] Continual learning helpers.
- [backend/app/services/video_processing.py] Video frame extraction and quality filtering.
- [backend/app/services/yolov8_attendance.py] LBP/histogram fallback pipeline.
- [backend/app/services/azure_face_recognition.py] Azure Face API integration.
- [backend/app/services/cloud_face_recognition.py] Cloud fallback attendance.
- [backend/app/services/simple_face_matching.py] Lightweight image matching utility.
- [backend/app/utils/face_quality.py] Image quality scoring.
- [backend/app/utils/facial_landmarks_68.py] 68-point landmark analysis.
- [backend/app/utils/verification_manager.py] Verification record handling.
- [backend/app/utils/firebase_storage.py] Firebase storage integration.
- [backend/app/utils/gpu_utils.py] GPU detection/optimizations.
- [backend/app/utils/gpu_image_processing.py] GPU-accelerated enhancement.
- [backend/app/utils/face_recognition_wrapper.py] Safe `face_recognition` wrapper.
- [backend/app/utils/helpers.py] empty helpers placeholder.

Backend configuration and data:
- [backend/data/app_settings.json] Face recognition settings.
- [backend/data/automation_settings.json] Automation config.
- [backend/data/automation_status.json] Automation runtime status.
- [backend/data/encodings/] serialized encodings.
- [backend/data/models/] model files.
- [backend/data/student_images/] student images.
- [backend/data/student_videos/] student videos.
- [backend/data/attendance_images/] attendance images.

Backend scripts:
- [backend/scripts/README.md] Script usage.
- [backend/scripts/rebuild_encodings_robust.py] Rebuild encodings (multi-image average).
- [backend/scripts/rebuild_all_encodings.py] Rebuild encodings (alternate).
- [backend/scripts/generate_encodings.py] Process videos to encodings.
- [backend/scripts/reset_database.py] DB reset.
- [backend/scripts/reset_database_quick.py] DB reset + encodings cleanup.
- [backend/scripts/migrate_database.py] Schema migration.
- [backend/scripts/optimize_database.py] DB optimization.
- [backend/scripts/check_database.py], [backend/scripts/inspect_db.py] diagnostics.
- [backend/scripts/test_api_with_images.py], [backend/scripts/test_verification_flow.py], [backend/scripts/test_quality_features.py] test scripts.
- [backend/scripts/clear_student_data.py], [backend/scripts/delete_student_data.py] data cleanup.
- [backend/scripts/rebuild_all_encodings.py], [backend/scripts/rebuild_encodings_robust.py] encoding rebuilds.

Backend tests:
- [backend/tests/test_face_quality.py] Face quality tests.
- [backend/tests/test_facial_landmarks.py] Landmarks tests.
- [backend/tests/test_integration.py] Confidence formula tests.

Frontend:
- [frontend/src/index.js] React entrypoint.
- [frontend/src/App.js] Router + providers.
- [frontend/src/index.css] Tailwind and theme styles.
- [frontend/src/contexts/AuthContext.js] Auth state and token management.
- [frontend/src/contexts/ThemeContext.js] Night mode and persistence.
- [frontend/src/services/api.js] Axios API client wrapper.
- [frontend/src/components/ProtectedRoute.js] Role-guarded routes.
- [frontend/src/components/AttendanceMarking.js] Manual attendance UI.
- [frontend/src/components/AttendanceVerificationModal.js] Teacher verification UI.
- [frontend/src/components/QualityErrorModal.js] Quality errors UI.
- [frontend/src/components/common/ThemeToggle.js] Theme toggle UI.
- [frontend/src/components/StudentManagement.js] Student CRUD UI.
- [frontend/src/components/teacher/*] Teacher dashboards and pages.
- [frontend/src/components/student/*] Student dashboards and pages.

Configuration:
- [frontend/package.json] scripts and dependencies.
- [frontend/tailwind.config.js] Tailwind config (dark mode class).
- [frontend/postcss.config.js] PostCSS config.

### Entry points
- Backend: [backend/app/main.py]
- Frontend: [frontend/src/index.js]

### Configuration management
- Runtime settings stored in JSON: [backend/data/app_settings.json], [backend/data/automation_settings.json].
- Settings API updates these files: [backend/app/api/endpoints/settings.py].

## 4. Features and Functional Requirements

### Feature: Manual attendance marking
- Description: Teacher uploads classroom image; system detects and recognizes students.
- Trigger: UI button in [frontend/src/components/AttendanceMarking.js].
- Inputs: class_name, image file (multipart). API: POST /api/attendance/mark.
- Outputs: attendance record with present/absent lists, confidence, verification data.
- Edge cases: no faces found, blurry image, missing encodings, empty class.
- Failure conditions: invalid image, processing errors, DB failures.
- Validation rules: image MIME type; quality thresholds and face detection checks.

### Feature: Automated attendance
- Description: Scheduler captures images from camera/RTSP and marks attendance.
- Trigger: Start automation button in [frontend/src/components/teacher/AutomatedAttendance.js].
- Inputs: class_name, interval_minutes, camera_source, quality_retry config.
- Outputs: periodic attendance records with status updates.
- Edge cases: camera unavailable, no faces, repeated quality failures.
- Failure conditions: capture failure, processing errors.
- Validation rules: class_name required; quality retry loop enforces min_quality_threshold.

### Feature: Face encoding rebuild
- Description: Rebuild all or single-student encodings, show progress.
- Trigger: Settings dashboard action in [frontend/src/components/teacher/Settings.js].
- Inputs: optional student_id.
- Outputs: progress status + saved encodings.
- Edge cases: missing student image folders, no faces.
- Failure conditions: InsightFace not initialized, IO errors.
- Validation rules: optional student ID; backend verifies folder existence.

### Feature: Student enrollment (video)
- Description: Student uploads video to generate encodings.
- Trigger: Student dashboard Video Management.
- Inputs: student video (multipart).
- Outputs: extracted frames, encodings generated.
- Edge cases: invalid video, zero faces.
- Failure conditions: ffmpeg/OpenCV errors, encoding failure.
- Validation rules: video format validation.

### Feature: Teacher verification
- Description: Borderline matches are routed to teacher for approval.
- Trigger: Manual attendance with ambiguous matches; verification modal.
- Inputs: attendance_id, face_index, action, verified_student_id.
- Outputs: updated verification records; optional encoding add.
- Edge cases: duplicate verification; encoding add fails.
- Failure conditions: missing attendance record; invalid student ID.
- Validation rules: action in {approve, reject, unknown}.

### Feature: Reporting and export
- Description: Attendance summary and session exports to Excel.
- Trigger: Teacher/Student report pages.
- Inputs: optional date range and class filters.
- Outputs: report data + Excel file URL.
- Edge cases: empty record sets.
- Failure conditions: export IO errors.
- Validation rules: date format; session_id must exist.

## 5. Workflows (Step-by-step)

### Automation workflow
1. Teacher sets automation settings and starts automation.
2. AutomationService enters loop: capture image from camera/RTSP.
3. Assess image quality; retry capture if below threshold.
4. Process attendance via face recognition pipeline.
5. Save attendance to DB; update status and schedule next run.
6. Repeat at interval.

### Manual attendance workflow
1. Teacher uploads photo.
2. Backend performs quality checks if enabled.
3. Detect faces and compare embeddings.
4. Save attendance record and present/absent lists.
5. If ambiguous matches, create verification records.

### Admin operations
- Create/delete classes, enroll students, remove students, reset system, rebuild encodings.

### User operations
- Student login, view attendance, download report, join/leave class, upload enrollment video.

### Error flows
- Quality validation failure -> HTTP 422 with issues.
- Missing encodings -> returns all students absent.
- Capture failure in automation -> retries until max attempts.

## 6. Algorithms and Logic

### Face recognition (YOLOv8 + InsightFace)
- Purpose: detect faces and generate normalized embeddings for comparison.
- Logic: detect faces -> generate embedding -> cosine similarity against stored embeddings.
- Complexity: O(F * E) for F faces and E embeddings.
- Alternatives: legacy `face_recognition` or histogram+LBP fallback.

### Quality assessment
- Purpose: reject poor images and improve recognition reliability.
- Logic: compute blur/brightness/size/contrast, weighted average.
- Complexity: O(P) for image pixels.

### Multi-scale detection (legacy)
- Purpose: detect small/distant faces.
- Logic: rescale images, run HOG detection, de-duplicate boxes.
- Complexity: O(S * P) where S is number of scales.

### Continual learning
- Purpose: improve encodings over time using verified faces.
- Logic: verify quality + confidence -> store additional encoding with cap.

## 7. Mathematics and Formulas

- Face quality score:
  - Blur score: $Q_{blur} = min(Var(\nabla^2 I)/500, 1)$
  - Brightness score: $Q_{brightness} = 1 - |mean - 128|/128$
  - Size score: $Q_{size} = min(\min(h, w)/112, 1)$
  - Contrast score: $Q_{contrast} = min(\sigma/60, 1)$
  - Overall: $Q = \sum_i w_i Q_i$
- Quality-weighted confidence:
  - $C = similarity \times (0.7 + 0.3 \times quality)$
- Attendance percentage:
  - $P = (present / total) \times 100$

## 8. Data Design

### Database schema (SQLite)
- users(id, email, password_hash, full_name, role, is_active, created_at, updated_at)
- classes(id, class_name, teacher_id, description, invite_code, invite_expires_at, created_at, updated_at)
- class_enrollments(id, class_id, student_id, enrolled_at)
- students(student_id, name, class_name, image_path, user_id, created_at, updated_at)
- attendance_records(id, class_id, class_name, date, image_path, total_faces_detected, created_at)
- student_attendance(id, attendance_record_id, student_id, status, confidence, created_at)
- attendance_verifications(id, attendance_record_id, face_index, face_crop_path, bbox_x1..bbox_y2, quality_score, suggested_student_id, suggested_similarity, verified_student_id, verification_action, verified_at, encoding_added, created_at)

### Relationships
- users(teacher) -> classes (1:N)
- classes -> class_enrollments (1:N)
- students -> class_enrollments (1:N)
- attendance_records -> student_attendance (1:N)
- attendance_records -> attendance_verifications (1:N)

### Indexing strategy
- Email, role, class, attendance date, attendance record, student attendance indexes. See [backend/app/models/database.py].

### Sample records
- users: `{id:1,email:'t@x.com',role:'teacher'}`
- classes: `{id:1,class_name:'AI',teacher_id:1}`
- students: `{student_id:'11',name:'Salman',class_name:'AI'}`
- attendance_records: `{id:101,class_name:'AI',date:'2026-02-09'}`
- student_attendance: `{attendance_record_id:101,student_id:'11',status:'present'}`

### Migration strategy
- `migrate_database.py` adds columns/indexes if missing.
- Scripts for reset/cleanup are in [backend/scripts].

## 9. Class and Object Design

Examples (full list of classes is in Section 3):
- `AutomationService`: scheduling, capture, quality retries, status tracking.
- `AttendanceService`: DB writes, report queries, export.
- `StudentManagementService`: CRUD, stats, enrolled students.
- `YOLOv8FaceRecognitionService`: detection + embeddings, settings, continual learning.
- `FaceRecognitionService`: legacy path with HOG/CNN.

Each class is defined in its respective service file under [backend/app/services].

## 10. API / Interface Documentation

See Section 4 (Features) and Section 2 (API endpoints). All APIs use JSON except file uploads (multipart). Authentication uses Bearer tokens for protected routes; see [backend/app/api/deps.py] and [backend/app/core/security.py].

## 11. Implementation Details

- Encodings are stored as pickled numpy arrays in `data/encodings/*.pkl`.
- The system supports both legacy `face_recognition` and YOLOv8 + InsightFace; selection is controlled by `useYOLOv8` in settings.
- Automation status is persisted to JSON to survive restarts.
- Frontend relies on Axios and uses Tailwind dark mode class on the root element.

## 12. Infrastructure and Deployment

- Runtime requirements: Python 3.8+, Node 16+, optional CUDA.
- Setup: install backend deps, run uvicorn, install frontend deps, run `npm start`.
- Environment variables: optional `.env` for DB and storage.
- CI/CD: not defined in repo; build script via `npm run build`.

## 13. Security Design

- JWT authentication with password hashing (bcrypt).
- Role-based access control enforced in dependencies.
- File upload validation for images/videos.
- Invite codes for class enrollment.

## 14. Performance Considerations

- GPU acceleration paths in `gpu_utils` and `gpu_image_processing`.
- Caching for class students and encodings in recognition services.
- Batch DB insert for attendance records.
- Optimized attendance processor for concurrency.

## 15. Logging, Monitoring, Debugging

- Logging via Python `logging` module in automation and recognition services.
- Console logs for key steps (quality assessment, detection counts).
- Debug scripts in [backend/scripts].

## 16. Testing Strategy

- Unit tests for face quality and landmarks.
- Integration tests for confidence formulas.
- Manual test scripts for API and verification flows.

## 17. Known Limitations and Future Improvements

- SQLite may limit scale; migrate to Postgres for production.
- Background tasks run in-process; use a job queue for heavy rebuilds.
- Improve error handling and progress reporting for long tasks.
- Add automated tests for API endpoints and frontend.

## 18. Glossary

- ArcFace: face recognition model producing embeddings.
- Embedding: numeric vector representing a face.
- YOLO: object detection model for faces.
- HOG/CNN: legacy face detection models in `face_recognition`.
- Verification: human-in-the-loop confirmation for ambiguous matches.
- Continual learning: incremental encoding updates from verified data.
