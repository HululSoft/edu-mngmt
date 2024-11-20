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
        
    def get_students_by_class(self, class_id):
        # Load students data from the students JSON file
        with open(self.students_file, 'r',encoding='utf-8') as file:
            students = json.load(file)
        
        # Filter and return the list of students that match the class_id
        class_students = [student for student in students if student['class_id'] == class_id]
        return class_students
        
    def get_classes_by_teacher(self, teacher_id):
        # Load classes data from the classes JSON file
        with open(self.classes_file, 'r',encoding='utf-8') as file:
            classes = json.load(file)
        
        # Filter and return the list of classes that match the teacher_id
        teacher_classes = [class_data for class_data in classes if class_data['teacher_id'] == teacher_id]
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
        next_month = month_start.replace(month=month_start.month % 12 + 1)
        month_end = next_month.replace(day=1)

        return [
            score for score in scores
            if score['student_id'] == student_id and
               month_start <= datetime.strptime(score['lesson_date'], "%Y-%m-%d") < month_end
        ]

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
        
        # Create a dictionary for quick lookup by (student_id, lesson_date)
        scores_dict = {(score['student_id'], score['lesson_date']): score for score in scores}
        
        # Add or replace the score in the dictionary
        key = (score_data['student_id'], score_data['lesson_date'])
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
        
    
    

def count_fridays(year: str, month: str) -> int:
    year = int(year)
    month = int(month)
    
    # Get a list of all days in the month and their corresponding weekdays
    month_days = calendar.monthcalendar(year, month)
    
    # Count Fridays (weekday 4)
    friday_count = sum(1 for week in month_days if week[calendar.FRIDAY] != 0)
    
    return friday_count