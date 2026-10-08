---
name: run-dev
description: >-
  Use this skill when the user asks to start, run, or launch the local development server for the Flask application.
---

# Run Development Environment

Use these instructions to start the E-Wellness Flask application locally.

## Steps

1.  **Check Virtual Environment**:
    Verify if the `.venv` directory exists. If it does not, create it:
    `python -m venv .venv`

2.  **Activate Virtual Environment**:
    Run the activation script (Windows PowerShell):
    `.\.venv\Scripts\Activate.ps1`

3.  **Install Dependencies**:
    Ensure all requirements are installed:
    `pip install -r requirements.txt`

4.  **Verify Environment Variables**:
    Ensure a `.env` file exists in the root directory. It must contain the necessary Supabase credentials for the app to function properly.

5.  **Run the Server**:
    Start the Flask development server:
    `python app.py`

*Note: If you run the server for the user, be sure to use your run_command tool and set IsDaemon to true if the process should stay alive in the background.*
