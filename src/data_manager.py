import base64
import calendar
import json
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from models import Class, Teacher, ClassTeacher, Student, Score, Criteria


class DataManager:
    def __init__(self,db_session):
        self.db_session = db_session

    def load_score_labels(self):
        """
        Load score labels and metadata from the database.
        """
        criteria = self.db_session.query(Criteria).all()
        return [
            {
                "id": criterion.id,
                "name": criterion.name,
                "label": criterion.label
            }
            for criterion in criteria
        ]

    def get_teacher_name(self, teacher_id):
        """
        Get the teacher's name by their ID from the database.
        """
        # Query the database for the teacher's name
        teacher = self.db_session.query(Teacher).filter(Teacher.id == teacher_id).first()
        return teacher.name if teacher else None
    
    def get_class_by_id(self, class_id):
        """
        Get class data by class ID from the database.
        """
        # Query the database for the class
        class_data = self.db_session.query(Class).filter(Class.id == class_id).first()
        return {'id': class_data.id, 'name': class_data.name} if class_data else None
    
        

    def get_student_by_id(self, student_id):
        """
        Get a student by their ID from the database.
        """
        student = self.db_session.query(Student).filter_by(id=student_id).first()
        if student:
            return {
                'id': student.id,
                'name': student.name,
                'class_id': student.class_id,
                'active': student.active,
                'phone': student.phone,
                'parent_phone': student.parent_phone,
                'date_joined': student.date_joined.isoformat() if student.date_joined else None,
                'inactive_date': student.inactive_date.isoformat() if student.inactive_date else None
            }
        return None
    
    def get_student_by_name(self, student_name):
        """
        Get a student by their name from the database.
        """
        # Query the database for a student with the given name
        student = self.db_session.query(Student).filter_by(name=student_name).first()
        if student:
            return {
                'id': student.id,
                'name': student.name,
                'class_id': student.class_id,
                'phone': student.phone,
                'parent_phone': student.parent_phone,
                'date_joined': student.date_joined.isoformat() if student.date_joined else None,
                'active': student.active,
                'inactive_date': student.inactive_date.isoformat() if student.inactive_date else None
            }
        return None
    
    def get_students_by_class(self, class_id):
        """
        Get all active students for a specific class ID from the database.
        """
        # Query the database for students in the given class and filter by active status
        class_students = (
            self.db_session.query(Student)
            .filter(Student.class_id == class_id, Student.active == True)
            .all()
        )

        # Convert the query results into a list of dictionaries
        return [
            {
                'id': student.id,
                'name': student.name,
                'class_id': student.class_id,
                'active': student.active,
                'inactive_date': student.inactive_date
            }
            for student in class_students
        ]
        
    def get_classes_by_teacher(self, teacher_id):
        """
        Get classes by teacher ID from the database.
        """
        # Query the database to fetch classes associated with the teacher
        teacher_classes = (
            self.db_session.query(Class)
            .join(ClassTeacher, Class.id == ClassTeacher.class_id)
            .filter(ClassTeacher.teacher_id == teacher_id)
            .all()
        )
        return [{'id': cls.id, 'name': cls.name} for cls in teacher_classes]
        
    def get_teacher_by_name(self, teacher_name):
        """
        Get a teacher by their name from the database.
        """
        # Query the database for a teacher with the given name
        teacher = self.db_session.query(Teacher).filter_by(name=teacher_name).first()
        if teacher:
            return {
                'id': teacher.id,
                'name': teacher.name,
                'password': teacher.password  # Include only safe fields
            }
        return None
        
    def get_scores_by_student_and_month(self, student_id, month, year):
        """
        Get scores for a specific student and month from the database.

        Args:
            student_id (int): The ID of the student.
            month (int): The month for which scores are retrieved.
            year (int): The year for which scores are retrieved.

        Returns:
            list: A list of dictionaries containing scores grouped by date and criterion.
        """
        try:
            # Calculate the start and end dates for the given month
            month_start = datetime(year, month, 1).date()
            if month == 12:
                month_end = datetime(year + 1, 1, 1).date()
            else:
                month_end = datetime(year, month + 1, 1).date()

            # Query the database for scores in the given range
            scores_query = (
                self.db_session.query(Score)
                .filter(
                    Score.student_id == student_id,
                    Score.lesson_date >= month_start,
                    Score.lesson_date < month_end
                )
                .join(Criteria)  # Join with the Criteria table to fetch criterion details
            )

            # Group scores by lesson_date for structured output
            scores_by_date = {}
            for score in scores_query.all():
                lesson_date = score.lesson_date.isoformat()
                if lesson_date not in scores_by_date:
                    scores_by_date[lesson_date] = {
                        "lesson_date": lesson_date,
                        "scores": []
                    }
                scores_by_date[lesson_date]["scores"].append({
                    "criteria_name": score.criteria.name,
                    "criteria_label": score.criteria.label,
                    "value": score.value
                })

            # Convert grouped scores into a list
            return list(scores_by_date.values())
        except SQLAlchemyError as e:
            return {"status": "error", "message": str(e)}


    def get_scores_by_date(self, lesson_date, class_id, include_adjacent_dates=False):
        """
        Get scores for all students in a class on a specific lesson date.
        Optionally include scores for adjacent dates.

        Args:
            lesson_date (str): The date of the lesson in 'YYYY-MM-DD' format.
            class_id (int): The ID of the class.
            include_adjacent_dates (bool): Whether to include previous and next lesson dates.

        Returns:
            dict: A dictionary containing scores for all students and optional adjacent dates.
        """
        try:
            # Convert string date to a datetime object
            lesson_date_obj = datetime.strptime(lesson_date, '%Y-%m-%d').date()

            # Step 1: Fetch all active students in the class using the helper function
            students = self.get_students_by_class(class_id)
            student_ids = [student['id'] for student in students]

            # Step 2: Query all scores for the specified students and date
            scores_query = (
                self.db_session.query(Score)
                .filter(
                    Score.student_id.in_(student_ids),
                    Score.lesson_date == lesson_date_obj
                )
                .join(Criteria)  # Join with Criteria to fetch criterion metadata
            )

            # Step 3: Group scores by student and lesson date, and flatten scores structure
            scores_by_student = {}
            for score in scores_query.all():
                student_id = score.student_id
                if student_id not in scores_by_student:
                    scores_by_student[student_id] = {
                        "student_id": student_id,
                        "student_name": next(
                            (student['name'] for student in students if student['id'] == student_id),
                            "Unknown"
                        ),
                        "lesson_date": lesson_date_obj.isoformat(),
                        "scores": {}
                    }

                # Add each criterion as a separate key in the 'scores' dictionary
                scores_by_student[student_id]["scores"][score.criteria.name] = score.value

            # Flatten the results into a list
            scores = list(scores_by_student.values())

            # Step 4: Include adjacent dates if required
            if include_adjacent_dates:
                # Query distinct lesson dates for the class
                all_dates_query = (
                    self.db_session.query(Score.lesson_date)
                    .filter(Score.student_id.in_(student_ids))
                    .distinct()
                    .order_by(Score.lesson_date)
                )
                all_dates = [row.lesson_date for row in all_dates_query.all()]
                previous_date = next_date = None

                # Locate the current lesson_date in the sorted list
                if lesson_date_obj not in all_dates:
                    all_dates.append(lesson_date_obj)
                    all_dates.sort()
                lesson_date_index = all_dates.index(lesson_date_obj)
                if lesson_date_index > 0:
                    previous_date = all_dates[lesson_date_index - 1].isoformat()
                if lesson_date_index + 1 < len(all_dates):
                    next_date = all_dates[lesson_date_index + 1].isoformat()

                return {
                    "scores": scores,
                    "previous_date": previous_date,
                    "next_date": next_date,
                }

            # Step 5: Return scores for the specific date only
            return {"scores": scores}

        except SQLAlchemyError as e:
            return {"status": "error", "message": str(e)}


    def save_score(self, score_data):
        """
        Save scores for a student on a specific lesson date with optimized search and bulk operations.

        Args:
            score_data (dict): A dictionary containing:
                - student_id (int): The ID of the student.
                - lesson_date (date): The date of the lesson.
                - Any additional keys representing criteria names with boolean values (e.g., 'attendance', 'time', etc.).
        """
        try:
            student_id = score_data.get('student_id')
            lesson_date = score_data.get('lesson_date')

            # Validate required fields
            if not student_id or not lesson_date:
                return {"status": "error", "message": "Missing required fields: student_id or lesson_date"}

            # Extract dynamic criteria from the score_data (everything except student_id, lesson_date, class_id)
            scores = {
                key: value
                for key, value in score_data.items()
                if key not in ['student_id', 'lesson_date', 'class_id']
            }

            # Fetch the criteria from the database (e.g., attendance, uniform, etc.)
            criteria_map = {c.name: c.id for c in self.db_session.query(Criteria).all()}

            # Fetch all existing scores for the student and lesson_date in one query to avoid multiple lookups
            existing_scores_query = (
                self.db_session.query(Score)
                .filter(Score.student_id == student_id, Score.lesson_date == lesson_date)
                .all()
            )

            # Create a map of existing scores with (criteria_id, student_id, lesson_date) as key
            existing_scores_map = {
                (score.criteria_id, score.student_id, score.lesson_date): score
                for score in existing_scores_query
            }

            # Prepare the list for bulk insertions/updates
            scores_to_insert = []
            scores_to_update = []

            # Iterate over the provided scores for each criterion and decide whether to insert or update
            for criterion_name, value in scores.items():
                criteria_id = criteria_map.get(criterion_name)
                if not criteria_id:
                    # Skip if the criterion is not defined in the database
                    continue

                # Check if a score already exists for the student, lesson_date, and criteria
                existing_score = existing_scores_map.get((criteria_id, student_id, lesson_date))

                if existing_score:
                    # If the score exists, update its value
                    existing_score.value = value
                    scores_to_update.append(existing_score)
                else:
                    # Otherwise, create a new score for insertion
                    new_score = Score(
                        student_id=student_id,
                        lesson_date=lesson_date,
                        criteria_id=criteria_id,
                        value=value
                    )
                    scores_to_insert.append(new_score)

            # Perform batch insert and update
            if scores_to_update:
                self.db_session.bulk_save_objects(scores_to_update)  # Bulk update
            if scores_to_insert:
                self.db_session.bulk_save_objects(scores_to_insert)  # Bulk insert

            # Commit all the changes to the database
            self.db_session.commit()

            return {"status": "success", "message": "Scores saved successfully"}

        except SQLAlchemyError as e:
            # Handle any database errors and rollback the transaction
            self.db_session.rollback()
            return {"status": "error", "message": str(e)}


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
        """
        Load all teachers from the database, excluding their passwords.
        """
        teachers = self.db_session.query(Teacher).all()
        return [
            {
                'id': teacher.id,
                'name': teacher.name
            }
            for teacher in teachers
        ]

    def get_teachers_with_assigned_classes(self):
        """
        Retrieve a list of teachers with their assigned classes.

        Args:
            db_session: SQLAlchemy database session.

        Returns:
            List of dictionaries, each containing a teacher's ID, name, and their assigned classes.
        """
        # Query all teachers and their relationships with classes
        teachers_with_classes = self.db_session.query(Teacher).all()

        result = []
        for teacher in teachers_with_classes:
            assigned_classes = [
                {
                    'id': class_teacher.class_.id,
                    'name': class_teacher.class_.name
                }
                for class_teacher in teacher.class_teachers
            ]
            result.append({
                'teacher_id': teacher.id,
                'teacher_name': teacher.name,
                'assigned_classes': assigned_classes
            })

        return result


    def load_classes(self):
        """
        Load all classes from the database.
        """
        classes = self.db_session.query(Class).all()
        return [{'id': class_.id, 'name': class_.name} for class_ in classes]


    def unassign_class_from_teacher(self, teacher_id, class_id):
        """
        Unassign a class from a teacher by removing the relationship from the database.
        """
        try:
            # Query the database to find the class-teacher relationship
            class_teacher = (
                self.db_session.query(ClassTeacher)
                .filter_by(teacher_id=teacher_id, class_id=class_id)
                .first()
            )

            if class_teacher:
                # Remove the relationship if it exists
                self.db_session.delete(class_teacher)
                self.db_session.commit()
                return {"status": "success", "message": f"Class {class_id} unassigned from teacher {teacher_id}."}
            else:
                return {"status": "not_found", "message": f"Teacher {teacher_id} is not assigned to class {class_id}."}
        except SQLAlchemyError as e:
            self.db_session.rollback()  # Rollback transaction in case of an error
            return {"status": "error", "message": f"Database error: {str(e)}"}


    def assign_class_to_teacher(self, teacher_id, class_id):
        """
        Assign a class to a teacher by adding the relationship in the database.
        """
        try:
            # Validate that the class exists
            class_exists = self.db_session.query(Class).filter_by(id=class_id).first()
            if not class_exists:
                raise ValueError(f"Class with ID {class_id} does not exist.")

            # Validate that the teacher exists
            teacher_exists = self.db_session.query(Teacher).filter_by(id=teacher_id).first()
            if not teacher_exists:
                raise ValueError(f"Teacher with ID {teacher_id} does not exist.")

            # Check if the relationship already exists
            existing_relationship = (
                self.db_session.query(ClassTeacher)
                .filter_by(teacher_id=teacher_id, class_id=class_id)
                .first()
            )
            if existing_relationship:
                return {"status": "exists", "message": f"Teacher {teacher_id} is already assigned to class {class_id}."}

            # Add the new relationship
            new_relationship = ClassTeacher(teacher_id=teacher_id, class_id=class_id)
            self.db_session.add(new_relationship)
            self.db_session.commit()

            return {"status": "success", "message": f"Class {class_id} successfully assigned to teacher {teacher_id}."}
        except ValueError as e:
            self.db_session.rollback()
            return {"status": "error", "message": str(e)}
        except SQLAlchemyError as e:
            self.db_session.rollback()
            return {"status": "error", "message": f"Database error: {str(e)}"}


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
        """
        Add a new teacher to the database.
        """
        if not teacher_name:
            raise ValueError("Teacher name cannot be empty.")
        if not password:
            raise ValueError("Password cannot be empty.")

        # Check if teacher name is unique
        existing_teacher = self.db_session.query(Teacher).filter_by(name=teacher_name).first()
        if existing_teacher:
            raise ValueError(f"Teacher with name '{teacher_name}' already exists.")

        # Base64 encode the password
        encoded_password = base64.b64encode(password.encode()).decode()

        try:
            # Create a new teacher and add to the database
            new_teacher = Teacher(name=teacher_name, password=encoded_password)
            self.db_session.add(new_teacher)
            self.db_session.commit()
            return {"status": "success", "message": f"Teacher '{teacher_name}' added successfully."}
        except SQLAlchemyError as e:
            self.db_session.rollback()
            return {"status": "error", "message": f"Database error: {str(e)}"}

    def add_new_class(self, class_name, assigned_teacher_id):
        """
        Add a new class to the database and assign it to a teacher.
        """
        if not class_name:
            raise ValueError("Class name cannot be empty.")

        # Check if class name is unique
        existing_class = self.db_session.query(Class).filter_by(name=class_name).first()
        if existing_class:
            raise ValueError(f"Class with name '{class_name}' already exists.")

        # Check if the teacher exists
        teacher_exists = self.db_session.query(Teacher).filter_by(id=assigned_teacher_id).first()
        if not teacher_exists:
            raise ValueError(f"Teacher with ID '{assigned_teacher_id}' does not exist.")

        try:
            # Create a new class and add to the database
            new_class = Class(name=class_name)
            self.db_session.add(new_class)
            self.db_session.flush()  # Get the new class ID

            # Assign the teacher to the class
            new_class_teacher = ClassTeacher(teacher_id=assigned_teacher_id, class_id=new_class.id)
            self.db_session.add(new_class_teacher)
            self.db_session.commit()
            return {"status": "success", "message": f"Class '{class_name}' added successfully and assigned to teacher {assigned_teacher_id}."}
        except SQLAlchemyError as e:
            self.db_session.rollback()
            return {"status": "error", "message": f"Database error: {str(e)}"}

    
    def add_new_student(self, student_name: str, class_id: int, phone_number, parent_number, date_joined):
        """
        Add a new student to the database or update the record if the student already exists but is inactive.
        """
        if not student_name:
            raise ValueError("Student name cannot be empty.")

        # Check if a student with the given name already exists
        existing_student = self.db_session.query(Student).filter_by(name=student_name).first()

        try:
            if existing_student:
                if existing_student.active:
                    raise ValueError(f"Student with name '{student_name}' already exists in the class.")
                else:
                    # Update the existing student record
                    existing_student.class_id = class_id
                    existing_student.phone = phone_number
                    existing_student.parent_phone = parent_number
                    existing_student.date_joined = date_joined
                    existing_student.active = True
                    existing_student.inactive_date = None
                    self.db_session.commit()
                    return {"status": "success", "message": f"Student '{student_name}' reactivated and updated."}
            else:
                # Add a new student record
                new_student = Student(
                    name=student_name,
                    class_id=class_id,
                    phone=phone_number,
                    parent_phone=parent_number,
                    date_joined=date_joined,
                    active=True
                )
                self.db_session.add(new_student)
                self.db_session.commit()
                return {"status": "success", "message": f"Student '{student_name}' added successfully."}
        except SQLAlchemyError as e:
            self.db_session.rollback()  # Rollback transaction in case of error
            return {"status": "error", "message": f"Database error: {str(e)}"}
        
    def update_student(self, student_id, student_name, class_id, phone_number, parent_number, join_date):
        """
        Update a student's details in the database.
        """
        try:
            # Validate: Check if a student with the same name but a different ID exists
            existing_student = (
                self.db_session.query(Student)
                .filter(Student.name == student_name, Student.id != student_id)
                .first()
            )
            if existing_student:
                raise ValueError(f"Student with name '{student_name}' already exists.")

            # Find the student to update
            student = self.db_session.query(Student).filter_by(id=student_id).first()
            if not student:
                raise ValueError(f"Student with ID '{student_id}' does not exist.")

            # Update the student details
            student.name = student_name
            student.class_id = class_id
            student.phone = phone_number
            student.parent_phone = parent_number
            student.date_joined = join_date
            student.active = True  # Optional: Remove if active status is not relevant
            
            # Commit the changes to the database
            self.db_session.commit()
            return {"status": "success", "message": f"Student '{student_name}' updated successfully."}
        except ValueError as e:
            self.db_session.rollback()  # Rollback transaction in case of a validation error
            return {"status": "error", "message": str(e)}
        except SQLAlchemyError as e:
            self.db_session.rollback()  # Rollback transaction in case of a database error
            return {"status": "error", "message": f"Database error: {str(e)}"}


    def delete_student(self, student_id):
        """
        Mark a student as inactive in the database.
        """
        try:
            # Find the student by ID
            student = self.db_session.query(Student).filter_by(id=student_id).first()
            if not student:
                return {"status": "error", "message": f"Student with ID {student_id} does not exist."}

            # Update the student's active status and set the inactive date
            student.active = False
            student.inactive_date = datetime.now()
            self.db_session.commit()

            return {"status": "success", "message": f"Student with ID {student_id} marked as inactive."}
        except SQLAlchemyError as e:
            self.db_session.rollback()  # Rollback transaction in case of error
            return {"status": "error", "message": f"Database error: {str(e)}"}

def count_fridays(year: str, month: str) -> int:
    year = int(year)
    month = int(month)
    
    # Get a list of all days in the month and their corresponding weekdays
    month_days = calendar.monthcalendar(year, month)
    
    # Count Fridays (weekday 4)
    friday_count = sum(1 for week in month_days if week[calendar.FRIDAY] != 0)
    
    return friday_count