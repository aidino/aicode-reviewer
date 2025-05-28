import sys
sys.path.append("../src/webapp/backend")

from webapp.backend.database import init_database

if __name__ == "__main__":
    print("[INFO] Resetting and initializing database schema...")
    init_database()
    print("[SUCCESS] Database schema initialized (all tables created, including Project/Repository)") 