from __future__ import annotations

import sqlite3
from datetime import date
from typing import Any, Optional

from app.database import get_connection
from app.models import StudentCreate, StudentPatch, StudentUpdate


def row_to_student(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a SQLite row into a JSON-friendly dictionary."""
    return {
        "student_id": row["student_id"],
        "full_name": row["full_name"],
        "date_of_birth": row["date_of_birth"],
        "email": row["email"],
        "phone": row["phone"],
        "course": row["course"],
        "address": row["address"],
        "enrollment_date": row["enrollment_date"],
    }


def create_student(student_data: StudentCreate) -> dict[str, Any]:
    """Create a new student record."""
    with get_connection() as connection:
        try:
            cursor = connection.execute(
                """
                INSERT INTO students (
                    full_name,
                    date_of_birth,
                    email,
                    phone,
                    course,
                    address,
                    enrollment_date,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                (
                    student_data.full_name.strip(),
                    student_data.date_of_birth.isoformat(),
                    student_data.email,
                    student_data.phone,
                    student_data.course.strip() if student_data.course else None,
                    student_data.address.strip() if student_data.address else None,
                    student_data.enrollment_date.isoformat() if student_data.enrollment_date else None,
                ),
            )
            connection.commit()
            student_id = cursor.lastrowid
        except sqlite3.IntegrityError as exc:
            raise ValueError("A student with this email or phone number already exists.") from exc

    return get_student_by_id(student_id)


def get_students(
    name: Optional[str] = None,
    course: Optional[str] = None,
    date_of_birth: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Fetch students with optional filters for name, course, and DOB."""
    query = "SELECT * FROM students WHERE 1 = 1"
    params: list[Any] = []

    if name:
        query += " AND LOWER(full_name) LIKE LOWER(?)"
        params.append(f"%{name.strip()}%")
    if course:
        query += " AND LOWER(course) LIKE LOWER(?)"
        params.append(f"%{course.strip()}%")
    if date_of_birth:
        query += " AND date_of_birth = ?"
        params.append(date_of_birth)

    query += " ORDER BY student_id ASC"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

    return [row_to_student(row) for row in rows]


def get_student_by_id(student_id: int) -> dict[str, Any]:
    """Fetch one student by their id."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,),
        ).fetchone()

    if row is None:
        raise KeyError(f"Student with id {student_id} does not exist.")
    return row_to_student(row)


def update_student(student_id: int, student_data: StudentUpdate) -> dict[str, Any]:
    """Replace a student's data completely."""
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,),
        ).fetchone()
        if existing is None:
            raise KeyError(f"Student with id {student_id} does not exist.")

        try:
            connection.execute(
                """
                UPDATE students
                SET full_name = ?,
                    date_of_birth = ?,
                    email = ?,
                    phone = ?,
                    course = ?,
                    address = ?,
                    enrollment_date = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE student_id = ?
                """,
                (
                    student_data.full_name.strip(),
                    student_data.date_of_birth.isoformat(),
                    student_data.email,
                    student_data.phone,
                    student_data.course.strip() if student_data.course else None,
                    student_data.address.strip() if student_data.address else None,
                    student_data.enrollment_date.isoformat() if student_data.enrollment_date else None,
                    student_id,
                ),
            )
            connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("A student with this email or phone number already exists.") from exc

    return get_student_by_id(student_id)


def patch_student(student_id: int, student_data: StudentPatch) -> dict[str, Any]:
    """Apply a partial update to a student record."""
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,),
        ).fetchone()
        if existing is None:
            raise KeyError(f"Student with id {student_id} does not exist.")

        updates: dict[str, Any] = {}
        if student_data.full_name is not None:
            updates["full_name"] = student_data.full_name.strip()
        if student_data.date_of_birth is not None:
            updates["date_of_birth"] = student_data.date_of_birth.isoformat()
        if student_data.email is not None:
            updates["email"] = student_data.email
        if student_data.phone is not None:
            updates["phone"] = student_data.phone
        if student_data.course is not None:
            updates["course"] = student_data.course.strip()
        if student_data.address is not None:
            updates["address"] = student_data.address.strip()
        if student_data.enrollment_date is not None:
            updates["enrollment_date"] = student_data.enrollment_date.isoformat()

        if not updates:
            return row_to_student(existing)

        if "email" not in updates and "phone" not in updates:
            if existing["email"] is None and existing["phone"] is None:
                raise ValueError("At least one contact detail (email or phone) is required.")

        if "email" in updates and updates["email"] is None and existing["phone"] is None:
            raise ValueError("Either email or phone number is required.")
        if "phone" in updates and updates["phone"] is None and existing["email"] is None:
            raise ValueError("Either email or phone number is required.")

        set_clauses = ", ".join(f"{field} = ?" for field in updates)
        values = list(updates.values())
        values.extend([student_id])

        try:
            connection.execute(
                f"UPDATE students SET {set_clauses}, updated_at = CURRENT_TIMESTAMP WHERE student_id = ?",
                tuple(values),
            )
            connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("A student with this email or phone number already exists.") from exc

    return get_student_by_id(student_id)


def delete_student(student_id: int) -> bool:
    """Delete a student record."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM students WHERE student_id = ?",
            (student_id,),
        )
        connection.commit()
    return cursor.rowcount > 0
