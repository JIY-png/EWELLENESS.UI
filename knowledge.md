# E-Wellness UI Project Knowledge Base

## Overview
This project is a web application built with **Flask** (Python) that serves as an Electronic Health Record (EHR) or wellness system. 

## Tech Stack
* **Backend Framework:** Flask (`app.py`)
* **Database:** Supabase (PostgreSQL) - The project was successfully migrated from Firebase.
* **PDF Generation:** ReportLab (Used for generating dynamic PDF reports)
* **Environment Management:** `python-dotenv` for loading `.env` variables
* **Frontend:** HTML templates with Flask's `render_template` (served from `/templates` and `/static` folders)

## Project Structure
* `app.py`: The main Flask application containing routing and business logic.
* `supabase_schema.sql`: Database schema definition for Supabase.
* `SUPABASE_SETUP.md`: Setup instructions and configurations for the Supabase backend.
* `requirements.txt`: Python dependencies.
* `templates/`: HTML templates for the frontend.
* `static/`: Static assets like images (e.g., `E-Wellness logo.png`), CSS, and JavaScript.

## Setup & Running Locally
1. Activate your Python virtual environment (e.g., `.venv`).
2. Ensure you have your `.env` file properly configured with your Supabase credentials.
3. Install dependencies: `pip install -r requirements.txt`
4. Run the Flask development server: `python app.py`

## Notes & Conventions
*(Add your project conventions, deployment steps, or internal rules here)*
