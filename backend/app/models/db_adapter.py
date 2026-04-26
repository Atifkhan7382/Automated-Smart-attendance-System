"""
Smart Database Adapter
Automatically uses Firebase (cloud) or SQLite (local development)
"""

import os
from typing import Dict, List, Optional

# Try to use Firebase if credentials are available
USE_FIREBASE = bool(
    os.getenv('FIREBASE_CREDENTIALS') or 
    os.path.exists('firebase-credentials.json') or
    os.path.exists('app/firebase-credentials.json')
)

if USE_FIREBASE:
    print("🔥 Using Firebase (Cloud Mode)")
    from app.models import firebase_database as db_impl
else:
    print("💾 Using SQLite (Local Development Mode)")
    from app.models import database as db_impl

# Re-export all functions
init_db = db_impl.init_db

# Export database-specific functions if they exist
if hasattr(db_impl, 'get_db_connection'):
    get_db_connection = db_impl.get_db_connection
elif hasattr(db_impl, 'get_db'):
    get_db = db_impl.get_db

__all__ = ['init_db', 'USE_FIREBASE']
