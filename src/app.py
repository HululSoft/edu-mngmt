import base64
import logging
import os
import time
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from data_manager import DataManager
from models import db

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DB_SCHEMA'] = os.getenv('DB_SCHEMA', 'school_management')  # Default schema

app.secret_key = 'supersecretkey'

# Initialize the database
db.init_app(app)

data_manager = DataManager(db.session)

logging.basicConfig(level=logging.INFO)
custom_logger = logging.getLogger("custom")
custom_logger.setLevel(logging.INFO)

logging.getLogger('werkzeug').setLevel(logging.ERROR)


@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_request(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        log_message = (
            f'{request.remote_addr} - - [{time.strftime("%d/%b/%Y %H:%M:%S")}] '
            f'"{request.method} {request.path} {request.environ.get("SERVER_PROTOCOL")}" '
            f'{response.status_code} - {duration:.3f}s'
        )
        custom_logger.info(log_message)
    return response

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'teacher_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'teacher_id' not in session:
            return redirect(url_for('login'))
        if not data_manager.is_teacher_admin(session['teacher_id']):
            return "Forbidden", 403 # Or redirect to a non-admin page
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return redirect(url_for('select_class'))

# adding a route for admin: /admin. this will allow admin, to assign teachers to classes, add new teachers, and add new classes
@app.route('/admin')
@admin_required
def admin():
    teachers = data_manager.load_teachers()
    classes = data_manager.load_classes()
    teachers_with_assigned_classes = data_manager.get_teachers_with_assigned_classes()

    return render_template('management.html', teachers=teachers, classes=classes,teachers_with_assigned_classes=teachers_with_assigned_classes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        teacher = data_manager.get_teacher_by_name_or_username(username)
        if teacher and validate_password(teacher['password'], password):
            session['teacher_id'] = teacher['id']
            return redirect(url_for('select_class'))
        return "Invalid credentials", 401

    return render_template('login.html')

def validate_password(stored_encrypted_password: str, input_password: str) -> bool:
    # Decrypt the stored password and compare it with the input
    decrypted_password = decrypt_password(stored_encrypted_password)
    return decrypted_password == input_password

# Decrypting a password
def decrypt_password(encrypted_password: str) -> str:
    # Decode the Base64 string back to bytes, then decode to a plaintext string
    return base64.b64decode(encrypted_password.encode()).decode()

@app.route('/select_class')
@login_required
def select_class():
    teacher_id = session['teacher_id']
    classes = data_manager.get_classes_by_teacher(teacher_id)
    teacher_name = data_manager.get_teacher_name(teacher_id)
    is_admin = data_manager.is_teacher_admin(teacher_id)
    return render_template('select_class.html', teacher_name=teacher_name, classes=classes, is_admin=is_admin)

@app.route('/attendance/<int:class_id>', methods=['GET', 'POST'])
@login_required
def attendance(class_id):
    if request.method == 'POST':
        lesson_date = request.form['lesson_date']
        students = data_manager.get_students_by_class(class_id)
        score_labels = data_manager.load_score_labels()

        student_notes = request.form['notes'] # a json string like this: '{"32": {<score_label>: "some notes"} }' where 32 is the student id
        student_notes = eval(student_notes)
        lesson_subject = request.form['lesson_subject']
        lesson_activity = request.form['lesson_activity']
        students_score_data = dict()
        for student in students:
            student_id = student['id']
            new_score = {}
            for score in score_labels:
                new_score[score['name']] = {
                    'value': f'{score["name"]}_{student_id}' in request.form,
                    'notes': student_notes.get(str(student_id), {}).get(score['name'], None)
                }
            students_score_data[student_id] = new_score
        data_manager.save_scores(class_id, lesson_date, students_score_data, lesson_subject, lesson_activity)

    class_name = data_manager.get_class_by_id(class_id)['name']
    students = data_manager.get_students_by_class(class_id)
    scores_labels = data_manager.load_score_labels()
    return render_template('attendance.html', students=students, class_id=class_id, scores_labels=scores_labels, class_name=class_name, lesson_subject='', lesson_activity='')

# route for attendance data. accepts a class id and a specific date. GET method. return json data
@app.route('/attendance_data/<int:class_id>/<date>')
def attendance_data(class_id, date):
    result = data_manager.get_scores_by_date(date, class_id, include_adjacent_dates=True)
    return jsonify(result)




@app.route('/monthly_report/<int:class_id>/<int:student_id>', methods=['GET', 'POST'])
@login_required
def monthly_report(class_id, student_id):
    if request.method == 'POST':
        month = int(request.form['month'])
        year = int(request.form['year'])
        student = data_manager.get_student_by_id(student_id)
        class_data = data_manager.get_class_by_id(class_id)
        scores_labels=data_manager.load_score_labels()
        teacher_name = data_manager.get_teacher_name(session['teacher_id'])

        report = data_manager.get_monthly_report(student_id, class_id, month,year)
        print("scores_labels=",scores_labels)
        return render_template(
            'report_template.html',
            student=student,
            class_data=class_data,
            scores=report,
            scores_labels=scores_labels,
            month=month,
            year=year,
            teacher_name=teacher_name
        )

    return render_template('monthly_report_form.html', class_id=class_id, student_id=student_id)


@app.route('/remove_class/<int:teacher_id>/<int:class_id>')
@admin_required
def remove_class(teacher_id, class_id):
    data_manager.unassign_class_from_teacher(teacher_id, class_id)
    return redirect(url_for('admin'))



# route for deleting a lesson by date and class id
@app.route('/lessons/<int:class_id>/<date>', methods=['DELETE'])
@login_required
def delete_lesson(class_id, date):
    data_manager.delete_lesson(date, class_id)
    return redirect(url_for('attendance', class_id=class_id))

@app.route('/add_class/<int:teacher_id>/<int:class_id>')
@admin_required
def add_class(teacher_id, class_id):
    # Add the class to the teacher's classes
    data_manager.assign_class_to_teacher(teacher_id, class_id)
    return redirect(url_for('admin'))

@app.route('/add_teacher', methods=['POST'])
@admin_required
def add_teacher():
    teacher_name = request.form['teacher_name']
    teacher_username = request.form['teacher_username']
    password = request.form['teacher_password']
    data_manager.add_new_teacher(teacher_name, teacher_username, password)
    return redirect(url_for('admin'))

# route for add new class
@app.route('/add_new_class', methods=['POST'])
@admin_required
def add_new_class():
    class_name = request.form['class_name']
    # get the teacher id from the form as integer
    assigned_teacher = int(request.form['teacher_id'])
    data_manager.add_new_class(class_name, assigned_teacher)
    return redirect(url_for('admin'))


# route for showing student info. accepts student id
@app.route('/student/<int:student_id>')
def student(student_id):
    student = data_manager.get_student_by_id(student_id)
    # load classes to display in the drop down
    classes = data_manager.load_classes()
    return render_template('student.html', student=student, classes=classes)


@app.route('/students/new', methods=['GET', 'POST'])
@login_required
def add_student():
    # Load all classes for admin, or teacher's classes for regular teachers
    if request.referrer and 'manage_students' in request.referrer:
        # Coming from admin management page - show all classes
        classes = data_manager.load_classes()
    else:
        # Coming from teacher page - show only teacher's classes
        classes = data_manager.get_classes_by_teacher(session['teacher_id'])

    if request.method == 'GET':
        return render_template('student.html', classes=classes, student={})

    student_name = request.form['name']
    class_id = int(request.form['class'])
    phone_number = request.form['phone']
    parent_number = request.form['parent_phone']
    join_date = request.form['date_joined']
    try:
        data_manager.add_new_student(student_name, class_id, phone_number, parent_number, join_date)
    except Exception as e:
        print(e)
        return render_template('student.html', error=str(e), student=request.form, classes=classes), 400

    # Redirect back to manage_students if coming from admin, otherwise to attendance
    if request.referrer and 'manage_students' in request.referrer:
        return redirect(url_for('manage_students'))
    else:
        return redirect(url_for('attendance', class_id=class_id))


# route for update_student. it accepts FormData for a student id
@app.route('/update_student/<int:student_id>', methods=['POST'])
@login_required
def update_student(student_id):
    student_name = request.form['name']
    class_id = int(request.form['class'])
    phone_number = request.form['phone']
    parent_number = request.form['parent_phone']
    join_date = request.form['date_joined']
    try:
        data_manager.update_student(student_id, student_name, class_id, phone_number, parent_number, join_date)
        return redirect(url_for('attendance', class_id=class_id))
    except Exception as e:
        print(e)
        return render_template('student.html', error=str(e), student=request.form)


#rote to activate a student. accepts student id
@app.route('/activate_student/<int:student_id>/<int:class_id>')
@login_required
def activate_student(student_id, class_id):
    data_manager.set_student_active(student_id, True)
    return redirect(url_for('attendance', class_id=class_id))

# route for delete_student. it accepts student id and class id
@app.route('/delete_student/<int:student_id>/<int:class_id>')
@login_required
def delete_student(student_id, class_id):
    data_manager.set_student_active(student_id, False)
    return redirect(url_for('attendance', class_id=class_id))

# route to show all json data
@app.route('/internal/data')
def internal_data():
    return jsonify(data_manager.get_all_data())

@app.route('/logout')
def logout():
    session.pop('teacher_id', None)
    return redirect(url_for('login'))

@app.route('/manage_students')
@login_required
def manage_students():
    students = data_manager.get_all_students_with_details()
    classes = data_manager.load_classes()
    return render_template('manage_students.html', students=students, classes=classes)

@app.route('/update_student_admin/<int:student_id>', methods=['POST'])
@login_required
def update_student_admin(student_id):
    name = request.form.get('name')
    phone = request.form.get('phone')
    parent_phone = request.form.get('parent_phone')
    date_joined = request.form.get('date_joined')
    status = request.form.get('status') == 'true'
    class_id = int(request.form.get('class_id'))

    data_manager.update_student_admin(student_id, name, phone, parent_phone, date_joined, status, class_id)
    return redirect(url_for('manage_students'))

@app.route('/delete_student_permanently/<int:student_id>', methods=['POST'])
@login_required
def delete_student_permanently(student_id):
    try:
        data_manager.delete_student_permanently(student_id)
        return redirect(url_for('manage_students'))
    except Exception as e:
        # Handle error gracefully
        return redirect(url_for('manage_students'))

if __name__ == '__main__':
    app.run(debug=True)
