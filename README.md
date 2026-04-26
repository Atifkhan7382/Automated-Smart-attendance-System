# 🎓 AttendAI

**AI-Powered Face Recognition Attendance Management System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- 8GB RAM (16GB recommended)
- GPU (optional, for 2-5x performance boost)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Atifkhan7382/Automated-Smart-attendance-System.git
cd Automated-Smart-attendance-System

# 2. Backend setup
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Frontend setup (in new terminal)
cd frontend
npm install
npm start
```

### Dependency profiles (choose one)
- Default full CPU build with face recognition and Firebase: [backend/requirements.txt](backend/requirements.txt)
- Cloud/no-compile build (no dlib, headless OpenCV): [backend/requirements-cloud.txt](backend/requirements-cloud.txt)
- GPU build (install torch/torchvision with matching CUDA wheels): [backend/requirements-gpu.txt](backend/requirements-gpu.txt)
- API-only minimal build (no CV/ML, for docs/CI): [backend/requirements-min.txt](backend/requirements-min.txt)

For CUDA, install torch/torchvision from https://pytorch.org/get-started/locally/ with the correct `pip install --index-url https://download.pytorch.org/whl/cu118 torch torchvision` command for your driver/toolkit.

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## ✨ Features

### 🎯 Core Capabilities
- **AI Face Recognition** - YOLOv8 + InsightFace/DeepFace
- **Automated Attendance** - Scheduled marking with camera integration
- **Multi-student Support** - Handle 40-50+ students simultaneously
- **GPU Acceleration** - 2-5x faster with CUDA support
- **Long-distance Recognition** - Detect faces from classroom-wide photos
- **Real-time Processing** - Instant attendance marking
- **Web Interface** - Modern React-based UI

### 📊 Management Features
- **Student Enrollment** - Video/image-based enrollment
- **Attendance Reports** - Export to Excel with detailed analytics
- **Class Management** - Multi-class support
- **Status Monitoring** - Real-time automation tracking
- **Configurable Settings** - Adjust recognition parameters

---

## 📖 Documentation

For complete documentation, setup instructions, API reference, and troubleshooting:

### 👉 **[Read PROJECT_GUIDE.md](PROJECT_GUIDE.md)** 👈

The comprehensive guide includes:
- Detailed installation steps
- Configuration options
- API reference
- Performance optimization
- Troubleshooting guide
- Best practices

---

## 🏗️ Technology Stack

**Backend:**
- FastAPI (Python web framework)
- YOLOv8/v11 (Face detection)
- InsightFace/DeepFace (Face recognition)
- PyTorch (Deep learning)
- OpenCV (Image processing)
- SQLite (Database)

**Frontend:**
- React 18 (UI library)
- TypeScript (Type safety)
- TailwindCSS (Styling)
- Axios (API client)

---

## 📁 Project Structure

```
AttendAI/
├── backend/              # FastAPI backend
│   ├── app/             # Core application
│   │   ├── api/         # API endpoints
│   │   ├── services/    # Business logic
│   │   ├── models/      # Data models
│   │   └── utils/       # Utilities
│   ├── data/            # Data storage
│   └── requirements.txt # Dependencies
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   └── services/    # API client
│   └── package.json
├── testing/             # Test scripts
├── PROJECT_GUIDE.md     # Complete documentation
└── CLEANUP_SUMMARY.md   # Cleanup details
```

---

## 🎓 Usage

### 1. Enroll Students
```bash
# Upload student videos or images via web interface
# System automatically generates face encodings
```

### 2. Mark Attendance
```bash
# Manual: Upload classroom photo
# Automated: Configure camera and schedule in Settings
```

### 3. View Reports
```bash
# Export attendance to Excel
# View historical data with filtering
```

For detailed usage instructions, see [PROJECT_GUIDE.md](PROJECT_GUIDE.md).

---

## ⚡ Performance

| Configuration | Speed | Accuracy | Use Case |
|---------------|-------|----------|----------|
| CPU + YOLOv8n | 2-4 FPS | 92-95% | Standard |
| GPU + YOLOv8n | 8-12 FPS | 95-97% | High accuracy |
| GPU + YOLOv8m | 4-6 FPS | 97-99% | Production |

---

## 🐛 Troubleshooting

### Common Issues

**Zero Recognition:**
```bash
cd backend
python rebuild_encodings_high_quality.py
```

**Low Accuracy:**
- Add more training images (10-15 per student)
- Adjust similarity threshold in settings
- Enable GPU acceleration

**Camera Issues:**
- Verify camera index/RTSP URL
- Check camera permissions
- Test with different indices (0, 1, 2)

For detailed troubleshooting, see [PROJECT_GUIDE.md - Troubleshooting](PROJECT_GUIDE.md#troubleshooting).

---

## 📊 System Requirements

### Minimum
- **CPU**: Intel Core i5 (4 cores)
- **RAM**: 8GB
- **Storage**: 10GB free

### Recommended
- **CPU**: Intel Core i7+ (8 cores)
- **RAM**: 16GB
- **GPU**: NVIDIA GPU with 4GB+ VRAM
- **Storage**: 20GB SSD

---

## 🔧 Configuration

Key settings in `backend/data/app_settings.json`:

```json
{
  "useYOLOv8": true,
  "yolov8Detection": {
    "confidence": 0.50,
    "model": "yolov8n"
  },
  "faceRecognition": {
    "model": "buffalo_l",
    "similarityThreshold": 0.40
  }
}
```

See [PROJECT_GUIDE.md - Configuration](PROJECT_GUIDE.md#configuration) for all options.

---

## 🧪 Testing

```bash
cd testing

# Test GPU performance
python gpu_performance_test.py

# Test accuracy
python simple_accuracy_test.py

# Test speed
python speed_test.py
```

---

## 📝 API Reference

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/students/enroll` | POST | Enroll new student |
| `/api/attendance/mark` | POST | Mark attendance |
| `/api/automation/start` | POST | Start automation |
| `/api/attendance/export` | GET | Export to Excel |

Full API documentation: http://localhost:8000/docs

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Atif Khan**
- GitHub: [@Atifkhan7382](https://github.com/Atifkhan7382)
- Repository: [Automated-Smart-attendance-System](https://github.com/Atifkhan7382/Automated-Smart-attendance-System)

---

## 🆘 Support

For issues, questions, or feature requests:
1. Check [PROJECT_GUIDE.md](PROJECT_GUIDE.md) for detailed documentation
2. Review [CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md) for recent changes
3. Open an issue on GitHub
4. Check API docs at `/docs` endpoint

---

## 📈 Version History

- **v2.0** - YOLOv8 integration, GPU acceleration, project cleanup
- **v1.5** - Automated attendance scheduling
- **v1.0** - Initial release

---

**Last Updated:** January 2025

**Status:** ✅ Production Ready
