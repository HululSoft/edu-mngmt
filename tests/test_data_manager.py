import unittest
import json
import os
from src.data_manager import DataManager


class TestDataManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test data
        self.data_dir = 'test_data'
        os.makedirs(self.data_dir, exist_ok=True)

        # Create sample data files
        self.teachers_file = f"{self.data_dir}/teachers.json"
        self.classes_file = f"{self.data_dir}/classes.json"
        self.students_file = f"{self.data_dir}/students.json"
        self.scores_file = f"{self.data_dir}/scores.json"
        self.scores_labels_file = f"{self.data_dir}/scores_labels.json"

        self.sample_teachers = [
            {"id": 1, "name": "John Doe", "password": "password1"},
            {"id": 2, "name": "Jane Smith", "password": "password2"}
        ]
        self.sample_classes = [
            {"id": 1, "name": "Math", "teacher_ids": [1]},
            {"id": 2, "name": "Science", "teacher_ids": [2]}
        ]
        self.sample_students = [
            {"id": 1, "name": "Student A", "class_id": 1},
            {"id": 2, "name": "Student B", "class_id": 2}
        ]
        self.sample_scores = [
            {"student_id": 1, "lesson_date": "2023-01-01", "score": 90},
            {"student_id": 2, "lesson_date": "2023-01-01", "score": 85}
        ]
        self.sample_scores_labels = [
            {"name": "score", "description": "Test Score"}
        ]

        with open(self.teachers_file, 'w', encoding='utf-8') as file:
            json.dump(self.sample_teachers, file, indent=4)
        with open(self.classes_file, 'w', encoding='utf-8') as file:
            json.dump(self.sample_classes, file, indent=4)
        with open(self.students_file, 'w', encoding='utf-8') as file:
            json.dump(self.sample_students, file, indent=4)
        with open(self.scores_file, 'w', encoding='utf-8') as file:
            json.dump(self.sample_scores, file, indent=4)
        with open(self.scores_labels_file, 'w', encoding='utf-8') as file:
            json.dump(self.sample_scores_labels, file, indent=4)

        self.data_manager = DataManager(self.data_dir)

    def tearDown(self):
        # Remove the temporary directory and its contents
        for file in [self.teachers_file, self.classes_file, self.students_file, self.scores_file, self.scores_labels_file]:
            os.remove(file)
        os.rmdir(self.data_dir)

    def test_get_teacher_name(self):
        self.assertEqual(self.data_manager.get_teacher_name(1), "John Doe")
        self.assertEqual(self.data_manager.get_teacher_name(2), "Jane Smith")
        self.assertIsNone(self.data_manager.get_teacher_name(3))

    def test_get_class_by_id(self):
        self.assertEqual(self.data_manager.get_class_by_id(1)['name'], "Math")
        self.assertEqual(self.data_manager.get_class_by_id(2)['name'], "Science")
        self.assertIsNone(self.data_manager.get_class_by_id(3))

    def test_get_student_by_id(self):
        self.assertEqual(self.data_manager.get_student_by_id(1)['name'], "Student A")
        self.assertEqual(self.data_manager.get_student_by_id(2)['name'], "Student B")
        self.assertIsNone(self.data_manager.get_student_by_id(3))

    def test_get_students_by_class(self):
        self.assertEqual(len(self.data_manager.get_students_by_class(1)), 1)
        self.assertEqual(len(self.data_manager.get_students_by_class(2)), 1)
        self.assertEqual(len(self.data_manager.get_students_by_class(3)), 0)

    def test_get_classes_by_teacher(self):
        self.assertEqual(len(self.data_manager.get_classes_by_teacher(1)), 1)
        self.assertEqual(len(self.data_manager.get_classes_by_teacher(2)), 1)
        self.assertEqual(len(self.data_manager.get_classes_by_teacher(3)), 0)

    def test_assign_class_to_teacher(self):
        self.data_manager.assign_class_to_teacher(1, 2)
        self.assertIn(1, self.data_manager.get_class_by_id(2)['teacher_ids'])

    def test_unassign_class_from_teacher(self):
        self.data_manager.unassign_class_from_teacher(1, 1)
        self.assertNotIn(1, self.data_manager.get_class_by_id(1)['teacher_ids'])

    def test_update_student(self):
        self.data_manager.update_student(1, student_name="Student C", class_id=2, join_date="2023-01-01", phone_number="123-456-7890", parent_number="098-765-4321")
        student = self.data_manager.get_student_by_id(1)
        self.assertEqual(student['name'], "Student C")
        self.assertEqual(student['class_id'], 2)
        self.assertEqual(student['date_joined'], "2023-01-01")
        self.assertEqual(student['phone'], "123-456-7890")
        self.assertEqual(student['parent_phone'], "098-765-4321")

if __name__ == '__main__':
    unittest.main()