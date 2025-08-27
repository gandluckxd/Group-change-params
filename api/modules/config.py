"""
Configuration for Group Change Params API
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_PORT = int(os.getenv("API_PORT", "8002"))
API_HOST = os.getenv("API_HOST", "0.0.0.0")

# Database configuration (direct Firebird connection)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "192.168.1.251"),
    "port": int(os.getenv("DB_PORT", "3050")),
    "database": os.getenv("DB_NAME", "D:/AltawinDB/altawinOffice.FDB"),
    "user": os.getenv("DB_USER", "sysdba"),
    "password": os.getenv("DB_PASSWORD", "masterkey"),
    "charset": os.getenv("DB_CHARSET", "WIN1251")
}

# Logging
ENABLE_LOGGING = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
