# Supabase Setup Instructions

This document provides step-by-step instructions for connecting the E-Wellness EHR System to Supabase.

## Prerequisites

- A Supabase account (free tier available at https://supabase.com)
- Python 3.8 or higher
- Virtual environment set up (already done)

## Step 1: Create a Supabase Project

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Click "New Project"
3. Enter a project name (e.g., "ewellness-ehr-system")
4. Set a database password (save this securely)
5. Choose a region closest to your users
6. Click "Create new project"
7. Wait for the project to be provisioned (usually 1-2 minutes)

## Step 2: Get Your Supabase Credentials

1. In the Supabase Dashboard, go to Project Settings (gear icon)
2. Go to the "API" section
3. Copy the following values:
   - **Project URL** (e.g., https://xxxxxxxx.supabase.co)
   - **anon public key** (public API key)
   - **service_role key** (secret key with full access)

## Step 3: Set Up Environment Variables

Create a `.env` file in the project root (same folder as `app.py`) with the following content:

```env
SUPABASE_URL=your_project_url_here
SUPABASE_KEY=your_service_role_key_here
```

**Important**: Use the `service_role key`, not the `anon public key`, as the application needs full database access.

## Step 4: Create Database Tables

Run the SQL script provided in `supabase_schema.sql` in the Supabase SQL Editor:

1. In the Supabase Dashboard, go to the "SQL Editor" (icon that looks like a terminal)
2. Click "New Query"
3. Copy the contents of `supabase_schema.sql`
4. Paste it into the editor
5. Click "Run" to execute the script

This will create the following tables:
- `patients` - Stores patient information
- `records` - Stores health records
- `admin_users` - Stores admin user accounts
- `access_logs` - Stores system access logs

## Step 5: Configure Row Level Security (RLS)

For development, you can disable RLS. For production, enable RLS and configure policies:

**Development (Disable RLS):**
```sql
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE records ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE access_logs ENABLE ROW LEVEL SECURITY;

-- Disable RLS for development
ALTER TABLE patients DISABLE ROW LEVEL SECURITY;
ALTER TABLE records DISABLE ROW LEVEL SECURITY;
ALTER TABLE admin_users DISABLE ROW LEVEL SECURITY;
ALTER TABLE access_logs DISABLE ROW LEVEL SECURITY;
```

**Production (Enable RLS with policies):**
```sql
-- Enable RLS
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE records ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE access_logs ENABLE ROW LEVEL SECURITY;

-- Allow all operations for development (restrict in production)
CREATE POLICY "Enable all access for development" ON patients
  FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Enable all access for development" ON records
  FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Enable all access for development" ON admin_users
  FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Enable all access for development" ON access_logs
  FOR ALL USING (true) WITH CHECK (true);
```

## Step 6: Install Dependencies

The required dependencies are in `requirements.txt`:
```
Flask>=3.0.0
reportlab
supabase
python-dotenv
```

Install them:
```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Step 7: Verify Supabase Connection

Run the application:
```bash
.venv\Scripts\python.exe app.py
```

If Supabase is configured correctly, you should see:
```
Supabase initialized successfully
 * Running on http://127.0.0.1:5000
```

If you see an error, check:
1. `.env` file exists in the project root
2. The file contains valid Supabase credentials
3. Your Supabase project is active
4. The database tables have been created

## Database Schema

### patients Table
- `id` (integer, primary key)
- `first_name` (text)
- `last_name` (text)
- `gender` (text)
- `birth_date` (text)
- `contact_no` (text)
- `barangay` (text)

### records Table
- `id` (integer, primary key)
- `patient_id` (integer)
- `A` (text) - Date
- `B` (text) - Time
- `C` (text) - FirstName
- `D` (text) - LastName
- `E` (integer) - Age
- `F` (text) - Gender
- `G` (text) - BloodPressure
- `H` (integer) - HeartRate_BPM
- `I` (integer) - OxygenSaturation_pct
- `J` (float) - BodyTemp_C
- `K` (float) - Weight_kg
- `L` (float) - Height_cm
- `M` (float) - BMI
- `bmi_category` (text)
- `status` (text)
- `remarks` (text)
- `created_at` (text)

### admin_users Table
- `id` (integer, primary key)
- `full_name` (text)
- `username` (text)
- `role` (text)
- `password_hash` (text)

### access_logs Table
- `id` (integer, primary key, auto-increment)
- `user` (text)
- `role` (text)
- `action` (text)
- `date_time` (text)

## Initial Data Setup

The application will automatically create records when you add data through the UI. To create an initial admin user:

1. Run the application
2. Navigate to http://127.0.0.1:5000/signup
3. Create your first admin account
4. The account will be stored in Supabase

## Troubleshooting

### "Supabase initialization error"
- Ensure `.env` file exists in the project root
- Check that the file contains valid Supabase credentials
- Verify your Supabase project is active

### "Permission denied" errors
- Check Row Level Security (RLS) policies in Supabase
- Ensure you're using the service_role key, not the anon key
- Verify the database tables have been created

### Data not persisting
- Verify your Supabase project is active
- Check your internet connection
- Review Supabase Dashboard for any errors
- Check the application logs for specific error messages

### "Module not found: supabase"
- Ensure you've installed the dependencies: `pip install -r requirements.txt`
- Make sure you're using the correct virtual environment

## Production Deployment

For production deployment:

1. **Use Environment Variables**: Store credentials in environment variables, never commit `.env` to version control
2. **Enable RLS**: Configure proper Row Level Security policies
3. **Use Connection Pooling**: Consider using a connection pool for better performance
4. **Monitor Usage**: Set up Supabase monitoring and alerts
5. **Backup**: Enable automated backups in Supabase settings
6. **Restrict API Keys**: Use the anon key for client-side operations and service_role key only for server-side

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://supabase.com/docs/reference/python)
- [Supabase SQL Editor](https://supabase.com/docs/guides/database)

## Migration from Firebase

If you're migrating from Firebase Firestore:

1. Export your existing data from Firebase
2. Transform the data to match the Supabase schema
3. Import the data into Supabase using the SQL Editor or API
4. Update the application code to use Supabase (already done in this version)
5. Test all functionality to ensure data integrity

The data structures are similar, but Supabase uses PostgreSQL which is a relational database, while Firebase uses a NoSQL document database. The schema provided maintains the same data model while leveraging PostgreSQL's relational capabilities.
