# Students Database CRUD Application

## Project overview
This is a beginner-friendly backend project built with Python, FastAPI, SQLite, Pydantic, and Uvicorn. It manages student records using a simple CRUD API and stores data in a local SQLite database.

## Features
- Create a new student
- List all students with optional filters
- Retrieve one student by ID
- Update a student completely with PUT
- Partially update a student with PATCH
- Delete a student
- Automatic SQLite table creation
- Data validation for required fields, dates, and email addresses
- Duplicate email protection
- Swagger API documentation

## Technologies used
- Python 3.10+
- FastAPI
- SQLite
- Pydantic
- Uvicorn
- Pytest
- FastAPI TestClient

## Prerequisites
- Python 3.10 or newer installed
- VS Code installed on Windows
- Git installed (optional, for uploading to GitHub)

## Windows VS Code setup instructions
1. Open VS Code.
2. Open the project folder: `student-crud-api`.
3. Open the terminal in VS Code.
4. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
5. Activate the virtual environment:
   ```bash
   .venv\Scripts\activate
   ```

## Virtual environment activation
After opening the project in VS Code, activate the environment every time you work:

```bash
.venv\Scripts\activate
```

## Dependency installation
Install the required packages:

```bash
pip install -r requirements.txt
```

## Server startup command
Run the app with Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Swagger API documentation URL
Open the browser and visit:

```text
http://127.0.0.1:8000/docs
```

## API endpoints and example request bodies

### 1. Create a student
- Method: `POST`
- URL: `/students`
- Example request body:

```json
{
  "full_name": "Alice Johnson",
  "date_of_birth": "2005-02-15",
  "email": "alice@example.com",
  "phone": "9876543210",
  "course": "Computer Science",
  "address": "123 Main Street",
  "enrollment_date": "2024-08-01"
}
```

### 2. List students
- Method: `GET`
- URL: `/students`
- Optional query parameters:
  - `name`
  - `course`
  - `date_of_birth`

Example:

```text
GET /students?name=alice&course=computer
GET /students?date_of_birth=2005-02-15
```

### 3. Get one student
- Method: `GET`
- URL: `/students/{student_id}`

Example:

```text
GET /students/1
```

### 4. Update a student (full update)
- Method: `PUT`
- URL: `/students/{student_id}`
- Example request body:

```json
{
  "full_name": "Alice Johnson",
  "date_of_birth": "2005-02-15",
  "email": "alice.new@example.com",
  "phone": "9876543211",
  "course": "Computer Science",
  "address": "456 New Street",
  "enrollment_date": "2024-08-15"
}
```

### 5. Partial update a student
- Method: `PATCH`
- URL: `/students/{student_id}`
- Example request body:

```json
{
  "course": "Data Science",
  "address": "45 Learning Avenue"
}
```

### 6. Delete a student
- Method: `DELETE`
- URL: `/students/{student_id}`

Example:

```text
DELETE /students/1
```

## Testing instructions
Run the automated tests with:

```bash
pytest
```

## SQLite database information
- Database file: `students.db`
- Location: project root (`student-crud-api/students.db`)
- The database is created automatically when the app starts.
- Records persist even after restarting the server.

## GitHub upload instructions
1. Create a new repository on GitHub.
2. In VS Code terminal, initialize Git:
   ```bash
   git init
   ```
3. Add all files:
   ```bash
   git add .
   ```
4. Commit the project:
   ```bash
   git commit -m "Initial commit: Students CRUD API"
   ```
5. Link your GitHub repository:
   ```bash
   git remote add origin <your-github-repository-url>
   ```
6. Push the code:
   ```bash
   git branch -M main
   git push -u origin main
   ```

## Notes
- Do not include real student personal information in the database.
- Use the sample dummy records from the tests or add your own sample data as needed.
- The project intentionally avoids authentication to keep the beginner setup simple.
