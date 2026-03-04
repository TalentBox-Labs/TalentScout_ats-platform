import sqlite3
import bcrypt
from datetime import datetime

conn = sqlite3.connect('backend/ats_platform.db')
cursor = conn.cursor()

# Hash the password
password = "admin123"  # Admin password
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Create organization for workcrew.ai
cursor.execute("""
INSERT INTO organizations (id, name, domain, is_active, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?)
""", (
    'admin-org-uuid-123',
    'WorkCrew AI',
    'workcrew.ai',
    1,
    datetime.utcnow().isoformat(),
    datetime.utcnow().isoformat()
))

# Create admin user
cursor.execute("""
INSERT INTO users (id, email, hashed_password, first_name, last_name, is_active, is_verified, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    'admin-user-uuid-123',
    'thomas@workcrew.ai',
    hashed,
    'Thomas',
    'Admin',
    1,  # is_active
    1,  # is_verified
    datetime.utcnow().isoformat(),
    datetime.utcnow().isoformat()
))

# Add user to organization as admin
cursor.execute("""
INSERT INTO organization_members (id, organization_id, user_id, role, is_active, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    'admin-member-uuid-123',
    'admin-org-uuid-123',
    'admin-user-uuid-123',
    'admin',
    1,
    datetime.utcnow().isoformat(),
    datetime.utcnow().isoformat()
))

conn.commit()
conn.close()

print("Admin user created successfully!")
print("Email: thomas@workcrew.ai")
print("Password: admin123")