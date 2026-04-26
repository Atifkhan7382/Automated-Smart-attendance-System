"""
Quick test to check what's happening with the similarity threshold
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.yolov8_face_recognition import yolov8_face_service

async def check_settings():
    print("Current Settings:")
    print(f"  Similarity Threshold: {yolov8_face_service.similarity_threshold}")
    print(f"  Detection Confidence: {yolov8_face_service.detection_confidence}")
    print(f"  Recognition Model: {yolov8_face_service.face_recognition_model}")
    
    # Reload settings
    yolov8_face_service._load_settings()
    
    print("\nAfter Reload:")
    print(f"  Similarity Threshold: {yolov8_face_service.similarity_threshold}")
    print(f"  Detection Confidence: {yolov8_face_service.detection_confidence}")
    print(f"  Recognition Model: {yolov8_face_service.face_recognition_model}")

asyncio.run(check_settings())
