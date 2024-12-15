import base64
import json
from datetime import datetime
import calendar

class DataManager:
    def __init__(self, data_dir):
        self.teachers_file = f"{data_dir}/teachers.json"
        self.classes_file = f"{data_dir}/classes.json"
        self.students_file = f"{data_dir}/students.json"
        self.scores_file = f"{data_dir}/scores.json"
        self.scores_labels_file = f"{data_dir}/scores_labels.json"

    def load_score_labels(self):
        """Load score labels and metadata from JSON file."""
        with open(self.scores_labels_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def get_teacher_name(self, teacher_id):
        with open(self.teachers_file, 'r', encoding='utf-8') as file:
            teachers = json.load(file)
        for teacher in teachers:
            if teacher['id'] == teacher_id:
                return teacher['name']
        return None
    
    def get_class_by_id(self, class_id):
        # Load classes data from the classes JSON file
        with open(self.classes_file, 'r',encoding='utf-8') as file:
            classes = json.load(file)
        
        # Find and return the class data by matching the class_id
        for class_data in classes:
            if class_data['id'] == class_id:
                return class_data
        return None  # Return None if no matching class is found
        
    def get_student_by_id(self, student_id):
        # Load students data from the students JSON file
        with open(self.students_file, 'r', encoding='utf-8') as file:
            students = json.load(file)
        
        # Find and return the student data by matching the student_id
        for student in students:
            if student['id'] == student_id:
                return student
        return None  # Return None if no matching student is found
    def get_student_by_name(self, student_name):
        # Load students data from the students JSON file
        with open(self.students_file, 'r',encoding='utf-8') as file:
            students = json.load(file)

        # Find and return the student data by matching the name
        for student in students:
            if student['name'] == student_name:
                return student
        return None
    def get_students_by_class(self, class_id):
        # Load students data from the students JSON file
        with open(self.students_file, 'r',encoding='utf-8') as file:
            students = json.load(file)
        
        # Filter and return the list of students that match the class_id and has no active: false
        class_students = [student for student in students if student['class_id'] == class_id and student.get('active', True)]
        return class_students
        
    def get_classes_by_teacher(self, teacher_id):
        # Load classes data from the classes JSON file
        with open(self.classes_file, 'r',encoding='utf-8') as file:
            classes = json.load(file)
        
        # Filter and return the list of classes with the matching teacher_id in the teacher_ids list
        teacher_classes = [class_data for class_data in classes if teacher_id in class_data['teacher_ids']]
        return teacher_classes
        
    def get_teacher_by_name(self, teacher_name):
        # Load teachers data from the teachers JSON file
        with open(self.teachers_file, 'r',encoding='utf-8') as file:
            teachers = json.load(file)
        
        # Find and return the teacher data by matching the name
        for teacher in teachers:
            if teacher['name'] == teacher_name:
                return teacher
        return None  # Return None if no matching teacher is found
        
    def get_scores_by_student_and_month(self, student_id, month, year):
        with open(self.scores_file, 'r', encoding='utf-8') as file:
            scores = json.load(file)

        month_start = datetime(int(year), int(month), 1)
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month + 1)
        month_end = next_month.replace(day=1)

        return [
            score for score in scores
            if score['student_id'] == student_id and
               month_start <= datetime.strptime(score['lesson_date'], "%Y-%m-%d") < month_end
        ]

    def get_scores_by_date(self, lesson_date, class_id, include_adjacent_dates=False):
        with open(self.scores_file, 'r', encoding='utf-8') as file:
            scores = json.load(file)

        if include_adjacent_dates:
            previous_date = next_date = None
            # extract dates in a set. sort the set by date, and get the dates preceding and following lesson_date
            lesson_dates = set([score["lesson_date"] for score in scores if score['class_id'] == class_id])
            if lesson_date not in lesson_dates:
                lesson_dates.add(lesson_date)
            lesson_dates = sorted(lesson_dates,  key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
            lesson_date_index = lesson_dates.index(lesson_date)
            if lesson_date_index > 0:
                previous_date = lesson_dates[lesson_date_index - 1]
            if lesson_date_index + 1 < len(lesson_dates):
                next_date = lesson_dates[lesson_date_index + 1]
            return dict(scores=[score for score in scores if score['lesson_date'] == lesson_date and score['class_id'] == class_id],
                          previous_date=previous_date, next_date=next_date)
        else:
             return dict(scores=[score for score in scores if score['lesson_date'] == lesson_date and score['class_id'] == class_id])
    def save_score(self, score_data):
        try:
            # Open the file in read mode first to load existing scores
            with open(self.scores_file, 'r', encoding='utf-8') as file:
                try:
                    # Load existing scores from the file
                    scores = json.load(file)
                except json.JSONDecodeError:
                    # Initialize as an empty list if the file is empty or invalid
                    scores = []
        except FileNotFoundError:
            # Initialize as an empty list if the file doesn't exist
            scores = []
        
        # Create a dictionary for quick lookup by (student_id, lesson_date, class_id) tuple
        scores_dict = {(score['student_id'], score['lesson_date'], score['class_id']): score for score in scores}
        
        # Add or replace the score in the dictionary
        key = (score_data['student_id'], score_data['lesson_date'], score_data['class_id'])
        scores_dict[key] = score_data  # Replace or add the score
        
        # Convert the dictionary back to a list
        updated_scores = list(scores_dict.values())
        
        # Open the file in write mode to save the updated scores
        with open(self.scores_file, 'w', encoding='utf-8') as file:
            json.dump(updated_scores, file, indent=4, ensure_ascii=False)

    def get_monthly_report(self, student_id, class_id, month,year):
        scores = self.get_scores_by_student_and_month(student_id, month, year)
        if not scores:
            return None

        aggregated_scores = {score_type['name']: sum(score[score_type['name']] for score in scores)
                             for score_type in self.load_score_labels()}
        
       
        total_lessons = count_fridays(year,month)
        return {
            score_type: round((aggregated_score / total_lessons) * 100, 2)
            for score_type, aggregated_score in aggregated_scores.items()
        }

    def load_teachers(self):
        with open(self.teachers_file, 'r', encoding='utf-8') as file:
            return [{k: v for k, v in teacher.items() if k != 'password'} for teacher in json.load(file)]

    def load_classes(self):
        with open(self.classes_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def unassign_class_from_teacher(self, teacher_id, class_id):
        classes = self.load_classes()
        # find the class with class_id and remove teacher_id from the list of teacher_ids. if teacher_id is not in the list, do nothing
        for class_data in classes:
            if class_data['id'] == class_id:
                if teacher_id in class_data['teacher_ids']:
                    class_data['teacher_ids'].remove(teacher_id)
                    break
        # save the updated classes list to the file
        with open(self.classes_file, 'w', encoding='utf-8') as file:
            json.dump(classes, file, indent=4, ensure_ascii=False)


    def assign_class_to_teacher(self, teacher_id, class_id):
        classes = self.load_classes()
        # make sure class_id is already in the list
        if class_id not in [class_data['id'] for class_data in classes]:
            raise ValueError(f"Class with ID {class_id} does not exist.")
        # make sure teacher_id is already in the list
        if teacher_id not in [teacher['id'] for teacher in self.load_teachers()]:
            raise ValueError(f"Teacher with ID {teacher_id} does not exist.")
        # if there is already an entry with class_id and teacher_id, do nothing. else add teacher_id to the list of teacher_ids
        for class_data in classes:
            if class_data['id'] == class_id:
                if teacher_id not in class_data['teacher_ids']:
                    class_data['teacher_ids'].append(teacher_id)
                    break
        # save the updated classes list to the file
        with open(self.classes_file, 'w', encoding='utf-8') as file:
            json.dump(classes, file, indent=4, ensure_ascii=False)

    def _add_teacher(self, teacher_name, password):
        # add a new teacher to the teachers list and save it to the file
        with open(self.teachers_file, 'r', encoding='utf-8') as file:
            teachers = json.load(file)
        # find the maximum teacher ID
        max_teacher_id = max([teacher['id'] for teacher in teachers], default=0)
        # create a new teacher dictionary
        # password show be base64 encoded before saving
        encoded_password = base64.b64encode(password.encode()).decode()
        new_teacher = {'id': max_teacher_id + 1, 'name': teacher_name, 'password': encoded_password}
        teachers.append(new_teacher)
        # save the updated teachers list to the file
        with open(self.teachers_file, 'w', encoding='utf-8') as file:
            json.dump(teachers, file, indent=4, ensure_ascii=False)

    def add_new_teacher(self, teacher_name, password):
        # validate the input
        if not teacher_name:
            raise ValueError("Teacher name cannot be empty.")
        if not password:
            raise ValueError("Password cannot be empty.")
        teachers = self.load_teachers()
        # make sure teacher_name is unique
        if any(teacher['name'] == teacher_name for teacher in teachers):
            raise ValueError(f"Teacher with name '{teacher_name}' already exists.")
        self._add_teacher(teacher_name, password)

    def add_new_class(self, class_name, assigned_teacher_id:int):
        # Load the current list of classes
        with open(self.classes_file, 'r', encoding='utf-8') as file:
            classes = json.load(file)

        # check if class name is not already present
        if any(class_data['name'] == class_name for class_data in classes):
            raise ValueError(f"Class with name '{class_name}' already exists.")

        # Find the maximum class ID
        max_class_id = max([class_data['id'] for class_data in classes], default=0)

        # Create a new class dictionary
        new_class = {
            'id': max_class_id + 1,
            'name': class_name,
            'teacher_ids': [assigned_teacher_id]
        }

        # Append the new class to the list
        classes.append(new_class)

        # Save the updated list of classes back to the file
        with open(self.classes_file, 'w', encoding='utf-8') as file:
            json.dump(classes, file, indent=4, ensure_ascii=False)

    def add_new_student(self, student_name: str, class_id: int, phone_number, parent_number, date_joined):

        if not student_name:
            raise ValueError("Student name cannot be empty.")
        student = self.get_student_by_name(student_name)
        if student:
            if student.get('active', True):
                raise ValueError(f"Student with name '{student_name}' already exists in the class.")
            else:
                self.update_student(student['id'], student_name, class_id, phone_number, parent_number, date_joined)
        else:
            # Find the maximum student ID
            with open(self.students_file, 'r', encoding='utf-8') as file:
                students = json.load(file)
            max_student_id = max([student['id'] for student in students], default=0)

            students.append({
                'id': max_student_id + 1,
                'name': student_name,
                'class_id': class_id,
                'phone': phone_number,
                'parent_phone': parent_number,
                'date_joined': date_joined
            })

            with open(self.students_file, 'w', encoding='utf-8') as file:
                json.dump(students, file, indent=4, ensure_ascii=False)

    def update_student(self, student_id, student_name, class_id, phone_number, parent_number, join_date):
        # Load the current list of students
        with open(self.students_file, 'r', encoding='utf-8') as file:
            students = json.load(file)

        # validation: if student name already exists with different id, raise error
        if any(student['name'] == student_name and student['id'] != student_id for student in students):
            raise ValueError(f"Student with name '{student_name}' already exists.")
        # Find the student to update by matching the student_id
        for student in students:
            if student['id'] == student_id:
                # Update the student details
                student['name'] = student_name
                student['class_id'] = class_id
                student['phone'] = phone_number
                student['parent_phone'] = parent_number
                student['date_joined'] = join_date
                student.pop('active', None)
                student.pop('inactive_date', None)
                break

        # Save the updated list of students back to the file
        with open(self.students_file, 'w', encoding='utf-8') as file:
            json.dump(students, file, indent=4, ensure_ascii=False)

    def delete_student(self, student_id):
        # Load the current list of students
        with open(self.students_file, 'r', encoding='utf-8') as file:
            students = json.load(file)

        # Find the student and set state: inactive
        for student in students:
            if student['id'] == student_id:
                student['active'] = False
                student['inactive_date'] = datetime.now().strftime('%Y-%m-%d')
                break

        # Save the updated list of students back to the file
        with open(self.students_file, 'w', encoding='utf-8') as file:
            json.dump(students, file, indent=4, ensure_ascii=False)


def count_fridays(year: str, month: str) -> int:
    year = int(year)
    month = int(month)
    
    # Get a list of all days in the month and their corresponding weekdays
    month_days = calendar.monthcalendar(year, month)
    
    # Count Fridays (weekday 4)
    friday_count = sum(1 for week in month_days if week[calendar.FRIDAY] != 0)
    
    return friday_count