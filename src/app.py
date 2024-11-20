from flask import Flask, request, render_template, redirect, url_for, session, send_file
from data_manager import DataManager
from io import BytesIO
import base64 
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
data_manager = DataManager('data')

@app.route('/')
def index():
    if 'teacher_id' in session:
        return redirect(url_for('select_class'))
    return redirect(url_for('login'))

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
        teacher_name = data_manager.get_teacher_name(class_data['teacher_id'])
        
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

@app.route('/logout')
def logout():
    session.pop('teacher_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
