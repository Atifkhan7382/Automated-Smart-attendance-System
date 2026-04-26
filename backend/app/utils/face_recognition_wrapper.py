"""
Safe wrapper for face_recognition module
Returns empty/default values when face_recognition is not available
"""

# Try to import face_recognition
try:
    import face_recognition as _face_recognition
    AVAILABLE = True
except ImportError:
    _face_recognition = None  # type: ignore
    AVAILABLE = False

def face_locations(image, number_of_times_to_upsample=1, model="hog"):
    """Safe wrapper for face_recognition.face_locations"""
    if not AVAILABLE or _face_recognition is None:
        return []
    return _face_recognition.face_locations(image, number_of_times_to_upsample, model)

def face_encodings(image, known_face_locations=None, num_jitters=1, model="small"):
    """Safe wrapper for face_recognition.face_encodings"""
    if not AVAILABLE or _face_recognition is None:
        return []
    return _face_recognition.face_encodings(image, known_face_locations, num_jitters, model)

def face_distance(face_encodings, face_to_compare):
    """Safe wrapper for face_recognition.face_distance"""
    if not AVAILABLE or _face_recognition is None:
        return []
    return _face_recognition.face_distance(face_encodings, face_to_compare)
