# Delete Student Data Script - Usage Guide

## Overview

This script allows you to delete student photos, videos, and face encodings from the system.

## Features

- ✅ Delete data for specific students
- ✅ Delete data for all students in a class
- ✅ Delete data for ALL students
- ✅ List all students with data status
- ✅ Interactive mode with menu
- ✅ Command-line mode for automation
- ✅ Confirmation prompts for safety

## Usage

### Interactive Mode (Recommended)

```bash
cd backend
python scripts/delete_student_data.py
```

This will show a menu:
```
1. List all students
2. Delete data for specific student
3. Delete data for all students in a class
4. Delete data for ALL students
5. Exit
```

### Command-Line Mode

**List all students:**
```bash
python scripts/delete_student_data.py list
```

**Delete specific student:**
```bash
python scripts/delete_student_data.py delete S001
```

**Delete all students in a class:**
```bash
python scripts/delete_student_data.py delete-class "Computer Science 101"
```

**Delete ALL student data:**
```bash
python scripts/delete_student_data.py delete-all
```

**Show help:**
```bash
python scripts/delete_student_data.py help
```

## What Gets Deleted

When you delete student data, the script removes:

1. **Student Videos** - `data/student_videos/{student_id}/`
2. **Student Images** - `data/student_images/{student_id}/` (extracted frames)
3. **Database Image Path** - Clears the `image_path` field
4. **Face Encodings** - Removed on next service reload

## Safety Features

- ✅ Confirmation prompts before deletion
- ✅ Shows list of affected students
- ✅ Requires typing exact phrases for dangerous operations
- ✅ Verbose output showing what's being deleted

## Examples

### Example 1: Delete Single Student

```bash
$ python scripts/delete_student_data.py delete S001

🗑️  Deleting data for student: S001
   ✅ Deleted videos: data/student_videos/S001
   ✅ Deleted images: data/student_images/S001
   ✅ Cleared database image path
   ℹ️  Face encodings will be removed on next service reload
```

### Example 2: Delete Class Students

```bash
$ python scripts/delete_student_data.py delete-class "AI"

⚠️  Found 3 students in class 'AI':
   - John Doe (S001)
   - Jane Smith (S002)
   - Bob Johnson (S003)

Delete data for all 3 students? (yes/no): yes

🗑️  Deleting data for students in class 'AI'...
   ✅ John Doe (S001)
   ✅ Jane Smith (S002)
   ✅ Bob Johnson (S003)

✅ Deleted data for 3 students
```

### Example 3: List Students

```bash
$ python scripts/delete_student_data.py list

📊 Student Data Status:
================================================================================
Student ID      Name                 Class           Has Data  
--------------------------------------------------------------------------------
S001            John Doe             AI              Yes       
S002            Jane Smith           AI              Yes       
S003            Bob Johnson          Unassigned      No        
================================================================================
Total students: 3
```

## Integration with Frontend

The frontend already has a delete button in the Video Management page. This script is for:
- **Administrators** - Bulk cleanup operations
- **Automation** - Scheduled cleanup tasks
- **Troubleshooting** - Manual data cleanup

## Notes

- The script does NOT delete the student record from the database
- Students can re-upload videos after deletion
- Face encodings are automatically cleaned up when the service reloads
- Always backup your database before bulk deletions

## Troubleshooting

**Script can't find database:**
- Make sure you're running from the `backend` directory
- Check that `data/attendance.db` exists

**Permission errors:**
- Ensure you have write permissions to the data directories
- On Windows, close any programs that might have files open

**Students not showing up:**
- Run `python scripts/check_db_simple.py` to verify database
- Check that students table has records
