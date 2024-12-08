import base64
import os
from functools import wraps

from flask import Flask, request, render_template, redirect, url_for, session, jsonify

from data_manager import DataManager

app = Flask(__name__)
app.secret_key = 'supersecretkey'
data_manager = DataManager(os.path.join(os.path.dirname(__file__), 'data'))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'teacher_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return redirect(url_for('select_class'))

# adding a route for admin: /admin. this will allow admin, to assign teachers to classes, add new teachers, and add new classes
@app.route('/admin')
def admin():
    teachers = data_manager.load_teachers()
    classes = data_manager.load_classes()
    return render_template('management.html', teachers=teachers, classes=classes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        teacher = data_manager.get_teacher_by_name(username)
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

    return render_template('select_class.html', teacher_name=teacher_name, classes=classes)

@app.route('/attendance/<int:class_id>', methods=['GET', 'POST'])
@login_required
def attendance(class_id):
    if request.method == 'POST':
        lesson_date = request.form['lesson_date']
        students = data_manager.get_students_by_class(class_id)
        score_labels = data_manager.load_score_labels()
        
        
        for student in students:
            student_id = student['id']
            new_score = {
                'student_id': student_id,
                'lesson_date': lesson_date,
                'class_id': class_id
            }
            for score in score_labels:
                new_score[score['name']] = f"{score['name']}_{student_id}" in request.form

            data_manager.save_score(new_score)
        
        return redirect(url_for('select_class'))
    class_name = data_manager.get_class_by_id(class_id)['name']
    students = data_manager.get_students_by_class(class_id)
    scores_labels = data_manager.load_score_labels()
    return render_template('attendance.html', students=students, class_id=class_id, scores_labels=scores_labels, class_name=class_name)

# route for attendance data. accepts a class id and a specific date. GET method. return json data
@app.route('/attendance_data/<int:class_id>/<date>')
def attendance_data(class_id, date):
    result = data_manager.get_scores_by_date(date, class_id, include_adjacent_dates=True)
    return jsonify(result)




@app.route('/monthly_report/<int:class_id>/<int:student_id>', methods=['GET', 'POST'])
@login_required
def monthly_report(class_id, student_id):
    if request.method == 'POST':
        month = request.form['month']
        year = request.form['year']
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
def remove_class(teacher_id, class_id):
    data_manager.unassign_class_from_teacher(teacher_id, class_id)
    return redirect(url_for('admin'))



@app.route('/add_class/<int:teacher_id>/<int:class_id>')
def add_class(teacher_id, class_id):
    # Add the class to the teacher's classes
    data_manager.assign_class_to_teacher(teacher_id, class_id)
    return redirect(url_for('admin'))

@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    teacher_name = request.form['teacher_name']
    password = request.form['teacher_password']
    data_manager.add_new_teacher(teacher_name, password)
    return redirect(url_for('admin'))

# route for add new class
@app.route('/add_new_class', methods=['POST'])
def add_new_class():
    class_name = request.form['class_name']
    # get the teacher id from the form as integer
    assigned_teacher = int(request.form['teacher_id'])
    data_manager.add_new_class(class_name, assigned_teacher)
    return redirect(url_for('admin'))

# route for add new student
@app.route('/add_new_student/<int:class_id>', methods=['POST'])
def add_new_student(class_id):
    student_name = request.form['student_name']
    data_manager.add_new_student(student_name, class_id)
    return redirect(url_for('attendance', class_id=class_id))

# route for showing student info. accepts student id
@app.route('/student/<int:student_id>')
def student(student_id):
    student = data_manager.get_student_by_id(student_id)
    # load classes to display in the drop down
    classes = data_manager.load_classes()
    return render_template('student.html', student=student, classes=classes)


# route for update_student. it accepts FormData for a student id
@app.route('/update_student/<int:student_id>', methods=['POST'])
def update_student(student_id):
    student_name = request.form['name']
    class_id = int(request.form['class'])
    phone_number = request.form['phone']
    parent_number = request.form['parent_phone']
    join_date = request.form['date_joined']
    try:
        data_manager.update_student(student_id, student_name, class_id, phone_number, parent_number, join_date)
        return jsonify({'message': 'Student updated successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': f'Error updating student: {str(e)}'}), 400



@app.route('/logout')
def logout():
    session.pop('teacher_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
