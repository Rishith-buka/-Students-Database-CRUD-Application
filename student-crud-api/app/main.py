from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, status

from app.crud import create_student, delete_student, get_student_by_id, get_students, patch_student, update_student
from app.database import ensure_database_directory, init_db
from app.models import StudentCreate, StudentPatch, StudentResponse, StudentUpdate


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize database tables when the app starts."""
    ensure_database_directory()
    init_db()
    yield


app = FastAPI(
    title="Students Database CRUD Application",
    description="Beginner-friendly FastAPI API for managing student records with SQLite persistence.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student_endpoint(student: StudentCreate):
    """Create a new student record."""
    try:
        return create_student(student)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get("/students", response_model=list[StudentResponse])
def list_students(
    name: Optional[str] = Query(default=None, description="Filter by student name."),
    course: Optional[str] = Query(default=None, description="Filter by course name."),
    date_of_birth: Optional[str] = Query(default=None, description="Filter by date of birth (YYYY-MM-DD)."),
):
    """List students with optional filters by name, course, and date of birth."""
    return get_students(name=name, course=course, date_of_birth=date_of_birth)


@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student_endpoint(student_id: int):
    """Retrieve a single student by id."""
    try:
        return get_student_by_id(student_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student_endpoint(student_id: int, student: StudentUpdate):
    """Fully replace a student record."""
    try:
        return update_student(student_id, student)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.patch("/students/{student_id}", response_model=StudentResponse)
def patch_student_endpoint(student_id: int, student: StudentPatch):
    """Partially update a student record."""
    try:
        return patch_student(student_id, student)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student_endpoint(student_id: int):
    """Delete a student record."""
    if not delete_student(student_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student with id {student_id} does not exist.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
