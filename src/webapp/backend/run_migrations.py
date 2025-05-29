#!/usr/bin/env python3
"""
Script để chạy database migrations với đúng configuration
"""
import os
import sys
from alembic.config import Config
from alembic import command

def run_migrations():
    """Chạy database migrations"""
    
    # Thiết lập database URL từ environment variables
    postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
    postgres_port = os.getenv('POSTGRES_PORT', '5432')
    postgres_user = os.getenv('POSTGRES_USER', 'aicode')
    postgres_password = os.getenv('POSTGRES_PASSWORD', 'aicode123')
    postgres_db = os.getenv('POSTGRES_DB', 'aicode_reviewer')
    
    database_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
    
    print(f"Connecting to database: {postgres_host}:{postgres_port}/{postgres_db}")
    print(f"User: {postgres_user}")
    
    # Thiết lập alembic config
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    
    try:
        # Chạy migrations
        print("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully!")
        
    except Exception as e:
        print(f"Error running migrations: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations() 