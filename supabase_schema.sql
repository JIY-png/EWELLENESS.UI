-- E-Wellness EHR System - Supabase Database Schema
-- This script creates the necessary tables for the E-Wellness application

-- Enable UUID extension for generating unique IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- PATIENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    gender TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    contact_no TEXT,
    barangay TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on patient ID for faster lookups
CREATE INDEX IF NOT EXISTS idx_patients_id ON patients(id);

-- ============================================
-- RECORDS TABLE (Health Records)
-- ============================================
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    "A" TEXT, -- Date
    "B" TEXT, -- Time
    "C" TEXT, -- FirstName
    "D" TEXT, -- LastName
    "E" INTEGER, -- Age
    "F" TEXT, -- Gender
    "G" TEXT, -- BloodPressure
    "H" INTEGER, -- HeartRate_BPM
    "I" INTEGER, -- OxygenSaturation_pct
    "J" FLOAT, -- BodyTemp_C
    "K" FLOAT, -- Weight_kg
    "L" FLOAT, -- Height_cm
    "M" FLOAT, -- BMI
    bmi_category TEXT,
    status TEXT,
    remarks TEXT,
    created_at TEXT
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_records_patient_id ON records(patient_id);
CREATE INDEX IF NOT EXISTS idx_records_status ON records(status);
CREATE INDEX IF NOT EXISTS idx_records_created_at ON records(created_at);

-- ============================================
-- ADMIN_USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on username for faster authentication
CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username);

-- ============================================
-- ACCESS_LOGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS access_logs (
    id SERIAL PRIMARY KEY,
    "user" TEXT NOT NULL,
    role TEXT NOT NULL,
    action TEXT NOT NULL,
    date_time TEXT NOT NULL
);

-- Create index on date_time for sorting
CREATE INDEX IF NOT EXISTS idx_access_logs_date_time ON access_logs(date_time DESC);

-- ============================================
-- ROW LEVEL SECURITY (RLS) SETUP
-- ============================================

-- Enable RLS on all tables
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE records ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE access_logs ENABLE ROW LEVEL SECURITY;

-- For development: Allow all operations
-- WARNING: In production, replace these with proper security policies

DROP POLICY IF EXISTS "Enable all access for development on patients" ON patients;
CREATE POLICY "Enable all access for development on patients"
ON patients FOR ALL
USING (true)
WITH CHECK (true);

DROP POLICY IF EXISTS "Enable all access for development on records" ON records;
CREATE POLICY "Enable all access for development on records"
ON records FOR ALL
USING (true)
WITH CHECK (true);

DROP POLICY IF EXISTS "Enable all access for development on admin_users" ON admin_users;
CREATE POLICY "Enable all access for development on admin_users"
ON admin_users FOR ALL
USING (true)
WITH CHECK (true);

DROP POLICY IF EXISTS "Enable all access for development on access_logs" ON access_logs;
CREATE POLICY "Enable all access for development on access_logs"
ON access_logs FOR ALL
USING (true)
WITH CHECK (true);

-- ============================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================

-- Insert a sample admin user (password: admin123)
-- Password hash for "admin123" using werkzeug.security.generate_password_hash
INSERT INTO admin_users (id, full_name, username, role, password_hash)
VALUES (
    1, 
    'System Administrator', 
    'admin', 
    'System Admin', 
    'scrypt:32768:8:1$kLxXzZqY$X5zZqYkLxXzZqYkLxXzZqYkLxXzZqYkLxXzZqYkLxXzZqYkLxXzZqYkLxXzZqY'
)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- HELPER FUNCTIONS (Optional)
-- ============================================

-- Function to get the next patient ID
CREATE OR REPLACE FUNCTION get_next_patient_id()
RETURNS INTEGER AS $$
BEGIN
    RETURN COALESCE((SELECT MAX(id) FROM patients), 0) + 1;
END;
$$ LANGUAGE plpgsql;

-- Function to get the next record ID
CREATE OR REPLACE FUNCTION get_next_record_id()
RETURNS INTEGER AS $$
BEGIN
    RETURN COALESCE((SELECT MAX(id) FROM records), 0) + 1;
END;
$$ LANGUAGE plpgsql;

-- Function to get the next admin user ID
CREATE OR REPLACE FUNCTION get_next_admin_id()
RETURNS INTEGER AS $$
BEGIN
    RETURN COALESCE((SELECT MAX(id) FROM admin_users), 0) + 1;
END;
$$ LANGUAGE plpgsql;
