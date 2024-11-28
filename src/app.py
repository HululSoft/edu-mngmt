import base64
import os

from flask import Flask, request, render_template, redirect, url_for, session

from data_manager import DataManager

app = Flask(__name__)
app.secret_key = 'supersecretkey'
data_manager = DataManager(os.path.join(os.path.dirname(__file__), 'data'))

@app.route('/')
def index():
    if 'teacher_id' in session:
        return redirect(url_for('select_class'))
    return redirect(url_for('login'))

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
def select_class():
    if 'teacher_id' not in session:
        return redirect(url_for('login'))

    teacher_id = session['teacher_id']
    classes = data_manager.get_classes_by_teacher(teacher_id)
    teacher_name = data_manager.get_teacher_name(teacher_id)

    return render_template('select_class.html', teacher_name=teacher_name, classes=classes)

@app.route('/attendance/<int:class_id>', methods=['GET', 'POST'])
def attendance(class_id):
    if 'teacher_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        lesson_date = request.form['lesson_date']
        students = data_manager.get_students_by_class(class_id)
        score_labels = data_manager.load_score_labels()
        
        
        for student in students:
            student_id = student['id']
            new_score = {
                'student_id': student_id,
                'lesson_date': lesson_date,
            }
            for score in score_labels:
                new_score[score['name']] = f"{score['name']}_{student_id}" in request.form

            data_manager.save_score(new_score)
        
        return redirect(url_for('select_class'))

    students = data_manager.get_students_by_class(class_id)
    scores_labels = data_manager.load_score_labels()
    return render_template('attendance.html', students=students, class_id=class_id, scores_labels=scores_labels)

@app.route('/monthly_report/<int:class_id>/<int:student_id>', methods=['GET', 'POST'])
def monthly_report(class_id, student_id):
    if 'teacher_id' not in session:
        return redirect(url_for('login'))

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


@app.route('/logout')
def logout():
    session.pop('teacher_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
