from datetime import datetime, date
from typing import List, Dict, Optional, Tuple

from flask import Blueprint, request, jsonify
from models import db, Student, Class, Score, Criteria


bp = Blueprint("performance_api", __name__)

ATTENDANCE_CRITERION_NAME = "attendance"


def parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def get_attendance_criteria_id() -> Optional[int]:
    crit = db.session.query(Criteria).filter(Criteria.name == ATTENDANCE_CRITERION_NAME).first()
    return crit.id if crit else None


def get_class_lessons_in_range(class_id: int, start: Optional[date], end: Optional[date]) -> List[date]:
    # Distinct lesson dates for the class based on scores across students in the class
    q = (
        db.session.query(Score.lesson_date)
        .join(Student, Student.id == Score.student_id)
        .filter(Student.class_id == class_id)
    )
    if start:
        q = q.filter(Score.lesson_date >= start)
    if end:
        q = q.filter(Score.lesson_date <= end)
    dates = [r[0] for r in q.distinct().order_by(Score.lesson_date.asc()).all()]
    return dates


def student_active_on(student: Student, on_date: date) -> bool:
    # A student is considered active on a lesson date if:
    # - date_joined is None or <= on_date
    # - inactive_date is None or >= on_date
    if student.date_joined and student.date_joined > on_date:
        return False
    if student.inactive_date and student.inactive_date < on_date:
        return False
    return True


def get_class_students(class_id: int) -> List[Student]:
    return db.session.query(Student).filter(Student.class_id == class_id).all()


def get_present_dates_for_student(student_id: int, start: Optional[date], end: Optional[date], attendance_criteria_id: int) -> List[date]:
    q = (
        db.session.query(Score.lesson_date)
        .filter(
            Score.student_id == student_id,
            Score.criteria_id == attendance_criteria_id,
            Score.value.is_(True),
        )
    )
    if start:
        q = q.filter(Score.lesson_date >= start)
    if end:
        q = q.filter(Score.lesson_date <= end)
    return [r[0] for r in q.distinct().order_by(Score.lesson_date.asc()).all()]


def get_attendance_lesson_dates_for_student(student_id: int, start: Optional[date], end: Optional[date], attendance_criteria_id: int) -> List[date]:
    # All lesson dates that have an attendance record for this student, regardless of True/False
    q = (
        db.session.query(Score.lesson_date)
        .filter(
            Score.student_id == student_id,
            Score.criteria_id == attendance_criteria_id,
        )
    )
    if start:
        q = q.filter(Score.lesson_date >= start)
    if end:
        q = q.filter(Score.lesson_date <= end)
    return [r[0] for r in q.distinct().order_by(Score.lesson_date.asc()).all()]


def compute_streaks(lesson_dates: List[date], present_dates: set) -> Tuple[int, int]:
    longest = 0
    current = 0
    for d in lesson_dates:
        if d in present_dates:
            current += 1
            if current > longest:
                longest = current
        else:
            current = 0
    return longest, current


def compute_student_performance(student_id: int, class_id: int, start: Optional[date], end: Optional[date]) -> Dict:
    attendance_criteria_id = get_attendance_criteria_id()
    if not attendance_criteria_id:
        return {"error": f"Attendance criterion '{ATTENDANCE_CRITERION_NAME}' not found."}

    # Only include lessons where this student has an attendance record (True or False)
    lesson_dates = get_attendance_lesson_dates_for_student(student_id, start, end, attendance_criteria_id)
    total_lessons = len(lesson_dates)

    present_dates = set(get_present_dates_for_student(student_id, start, end, attendance_criteria_id))
    attended = len([d for d in lesson_dates if d in present_dates])
    percentage = round((attended / total_lessons) * 100, 2) if total_lessons else 0.0

    longest_streak, current_streak = compute_streaks(lesson_dates, present_dates)

    return {
        "student_id": student_id,
        "class_id": class_id,
        "start_date": start.isoformat() if start else None,
        "end_date": end.isoformat() if end else None,
        "attended_lessons": attended,
        "total_lessons": total_lessons,
        "attendance_percentage": percentage,
        "longest_attendance_streak": longest_streak,
        "current_attendance_streak": current_streak,
    }


def compute_class_performance(class_id: int, start: Optional[date], end: Optional[date]) -> Dict:
    attendance_criteria_id = get_attendance_criteria_id()
    if not attendance_criteria_id:
        return {"error": f"Attendance criterion '{ATTENDANCE_CRITERION_NAME}' not found."}

    # Get all attendance scores for the class in the date range
    q = (
        db.session.query(Score)
        .join(Student, Student.id == Score.student_id)
        .filter(
            Student.class_id == class_id,
            Score.criteria_id == attendance_criteria_id
        )
    )

    if start:
        q = q.filter(Score.lesson_date >= start)
    if end:
        q = q.filter(Score.lesson_date <= end)

    all_attendance_scores = q.all()

    # Count total attendance records and those marked as present
    total_attendance_records = len(all_attendance_scores)
    present_attendance_records = sum(1 for score in all_attendance_scores if score.value is True)

    # Calculate percentage
    percentage = (
        round((present_attendance_records / total_attendance_records) * 100, 2)
        if total_attendance_records > 0
        else 0.0
    )

    # Get unique lesson dates for reference
    lesson_dates = list(set(score.lesson_date for score in all_attendance_scores))
    lesson_dates.sort()

    return {
        "class_id": class_id,
        "start_date": start.isoformat() if start else None,
        "end_date": end.isoformat() if end else None,
        "lesson_dates_count": len(lesson_dates),
        "total_present_attendance_records": present_attendance_records,
        "total_attendance_records": total_attendance_records,
        "class_attendance_percentage": percentage,
    }


@bp.route("/student", methods=["GET"])
def student_performance():
    try:
        student_id = int(request.args.get("student_id"))
        class_id = int(request.args.get("class_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "student_id and class_id are required integers"}), 400

    start = parse_date(request.args.get("start_date"))
    end = parse_date(request.args.get("end_date"))

    result = compute_student_performance(student_id, class_id, start, end)
    return jsonify(result)


@bp.route("/class/<int:class_id>", methods=["GET"])
def class_performance(class_id: int):
    start = parse_date(request.args.get("start_date"))
    end = parse_date(request.args.get("end_date"))
    result = compute_class_performance(class_id, start, end)
    return jsonify(result)


@bp.route("/school", methods=["GET"])
def school_performance():
    start = parse_date(request.args.get("start_date"))
    end = parse_date(request.args.get("end_date"))

    classes = db.session.query(Class).order_by(Class.id.asc()).all()
    results = [compute_class_performance(c.id, start, end) for c in classes]

    return jsonify({"classes": results})
