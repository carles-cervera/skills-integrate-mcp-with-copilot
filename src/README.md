# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.

## Teacher access

Only authenticated teachers can register or unregister students. Activity details and participant lists remain visible to everyone.

Create a teacher account with:

```
python -m src.manage_teachers
```

The command writes a salted password hash to `src/teachers.json`; no plaintext password is stored. The JSON file is checked in so assigned teacher accounts can be shared with the deployment. Set a stable, random `SESSION_SECRET` environment variable when running the application. Set `SESSION_COOKIE_SECURE=true` when serving over HTTPS.

Teacher sessions expire after eight hours. There is no in-app account maintenance page; add assigned accounts through the command-line tool.
