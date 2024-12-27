from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def get_schema():
    return os.getenv('DB_SCHEMA', 'default_schema')

class Teacher(db.Model):
    __tablename__ = 'teachers'
    __table_args__ = {'schema': get_schema()}  # Use the configured schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String, nullable=False)

    # Relationship with ClassTeacher
    class_teachers = db.relationship('ClassTeacher', backref='teacher', lazy=True)

class Class(db.Model):
    __tablename__ = 'classes'
    __table_args__ = {'schema': get_schema()}  # Use the configured schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Relationship with ClassTeacher
    class_teachers = db.relationship('ClassTeacher', backref='class_', lazy=True)

class ClassTeacher(db.Model):
    __tablename__ = 'class_teachers'
    __table_args__ = {'schema': get_schema()}  # Use the configured schema
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey(f'{get_schema()}.classes.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(f'{get_schema()}.teachers.id'), nullable=False)

class Student(db.Model):
    __tablename__ = 'students'
    __table_args__ = {'schema': get_schema()}  # Use the configured schema
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey(f'{get_schema()}.classes.id'), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    parent_phone = db.Column(db.String(20), nullable=True)
    date_joined = db.Column(db.Date, nullable=True)
    active = db.Column(db.Boolean, default=True)
    inactive_date = db.Column(db.Date, nullable=True)

class Score(db.Model):
    __tablename__ = 'scores'
    __table_args__ = {'schema': get_schema()}  # Use the configured schema

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(f'{get_schema()}.students.id'), nullable=False)
    lesson_date = db.Column(db.Date, nullable=False)
    criteria_id = db.Column(db.Integer, db.ForeignKey(f'{get_schema()}.criteria.id'), nullable=False)
    value = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.Column(db.String(255), nullable=True)

    # Relationships
    student = db.relationship('Student', backref='scores', lazy=True)
    criteria = db.relationship('Criteria', backref='scores', lazy=True)

class Criteria(db.Model):
    __tablename__ = 'criteria'
    __table_args__ = {'schema': get_schema()}  # Use the configured schema

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    label = db.Column(db.String(255), nullable=False)