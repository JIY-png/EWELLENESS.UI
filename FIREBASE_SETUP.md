# Firebase Setup Instructions (DEPRECATED)

**NOTE: This project has been migrated from Firebase to Supabase. Please use [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for the current setup instructions.**

This document is kept for reference purposes only and describes the previous Firebase Firestore setup.

---

## Legacy Firebase Setup

This document provides step-by-step instructions for connecting the E-Wellness EHR System to Firebase Firestore (legacy version).

## Prerequisites

- A Google account
- Python 3.8 or higher
- Virtual environment set up (already done)

## Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or create a new project
3. Enter a project name (e.g., "ewellness-ehr-system")
4. Follow the setup wizard and enable Google Analytics if desired
5. Click "Create project"

## Step 2: Set Up Firestore Database

1. In the Firebase Console, select your project
2. Go to "Build" > "Firestore Database"
3. Click "Create database"
4. Choose a location for your database (select a location near your users)
5. Select "Start in Test Mode" for development (you can change this later)
6. Click "Create"

## Step 3: Get Service Account Key

1. In the Firebase Console, go to Project Settings (gear icon)
2. Go to the "Service accounts" tab
3. Click "Generate new private key"
4. Select "JSON" as the key type
5. Click "Create"
6. The JSON file will be downloaded automatically
7. **Important**: Rename this file to `service-account-key.json`
8. Place the file in the root directory of this project (same folder as `app.py`)

## Step 4: Configure Firestore Security Rules

For development, you can use test mode rules. For production, update the rules in Firebase Console:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## Step 5: Install Dependencies

The required dependencies for the legacy Firebase version are in `requirements.txt`:
```
Flask>=3.0.0
reportlab
firebase-admin
```

## Step 6: Verify Firebase Connection

Run the application:
```bash
.venv\Scripts\python.exe app.py
```

If Firebase is configured correctly, you should see:
```
Firebase initialized successfully
 * Running on http://127.0.0.1:5000
```

## Firestore Collections

The application uses the following Firestore collections:

- **patients**: Stores patient information
  - Fields: id, first_name, last_name, gender, birth_date, contact_no, barangay

- **records**: Stores health records
  - Fields: id, patient_id, patient_name, temperature, heart_rate, oxygen_saturation, blood_pressure, height, weight, bmi, bmi_category, status, remarks, created_at

- **admin_users**: Stores admin user accounts
  - Fields: id, full_name, username, role, password_hash

- **access_logs**: Stores system access logs
  - Fields: id, user, role, action, date_time

## Migration to Supabase

The project has been migrated from Firebase to Supabase for better performance and easier management. To migrate your existing Firebase data:

1. Export your data from Firebase Firestore
2. Transform the data to match the Supabase schema (see `supabase_schema.sql`)
3. Import the data into Supabase using the SQL Editor or API
4. Follow the [SUPABASE_SETUP.md](SUPABASE_SETUP.md) instructions to configure the new backend

## Additional Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firestore Python SDK](https://firebase.google.com/docs/firestore/quickstart)
- [Firebase Admin Python SDK](https://firebase.google.com/docs/admin/setup)
