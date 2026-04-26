# Backend Utility Scripts

This folder contains utility scripts for database management, encoding generation, system maintenance, and testing.

## 📁 **Script Categories**

### **Database Management**
- `inspect_db.py` - Inspect database contents
- `migrate_database.py` - Database migration script
- `clear_student_data.py` - Clear student data from database
- `reset_system.py` - Reset entire system

### **Encoding Management**
- `generate_encodings.py` - Generate face encodings
- `rebuild_all_encodings.py` - Rebuild all encodings
- `rebuild_encodings_robust.py` - Robust encoding rebuild
- `check_encodings.py` - Check encoding status
- `inspect_encodings.py` - Inspect encoding files
- `inspect_encodings_detailed.py` - Detailed encoding inspection

### **Student Management**
- `add_missing_students.py` - Add missing students to database

### **Class Management**
- `generate_invite_codes.py` - Generate class invite codes
- `check_invites.py` - Check invite code status

### **System Configuration**
- `check_settings.py` - Check system settings

### **Testing & Quality**
- `test_api_with_images.py` - Test API endpoints with images
- `test_quality_features.py` - Test quality assessment features

---

## 🚀 **Usage**

### **Run from backend directory:**
```bash
cd backend
python scripts/script_name.py
```

### **Examples:**
```bash
# Check database
python scripts/inspect_db.py

# Generate encodings
python scripts/generate_encodings.py

# Test quality features
python scripts/test_quality_features.py

# Check system settings
python scripts/check_settings.py
```

---

## ⚠️ **Important Notes**

- **Run from backend directory**: All scripts expect to be run from the `backend/` directory
- **Database scripts**: Be careful with reset and clear scripts - they modify data
- **Encoding scripts**: May take time depending on number of students
- **Test scripts**: Useful for manual testing and verification

---

## 📚 **Script Descriptions**

### `inspect_db.py`
Displays database contents including students, classes, and attendance records.

### `migrate_database.py`
Handles database schema migrations and updates.

### `generate_encodings.py`
Generates face encodings from student videos.

### `rebuild_all_encodings.py`
Rebuilds all face encodings (useful after model updates).

### `check_encodings.py`
Checks which students have valid encodings.

### `clear_student_data.py`
Removes student data from the system (use with caution).

### `reset_system.py`
Resets the entire system to initial state (use with extreme caution).

### `test_api_with_images.py`
Manual testing script for API endpoints with image uploads.

### `test_quality_features.py`
Tests face quality assessment and landmarks features.

---

**For comprehensive testing, see the `tests/` directory.**
