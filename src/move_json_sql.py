# read json data from /Users/i311821/Documents/students_data_27_12_2024.json
# it has "scores" key with array of scores, each of which looks like this:
# {
#     "attendance": true,
#     "class_id": 4,
#     "lesson_date": "2024-12-13",
#     "participate": true,
#     "student_id": 55,
#     "time": true,
#     "uniform": false
# }

# for each score, create an sql insert statement into scores table:
# insert into scores (student_id, lesson_date(date), criteria_id(int), value(bool)) values (55, '2024-12-13', 1, true);
# where criteria_id is 1 for attendance, 2 for time, 3 for uniform, 4 for participate

import json

schema_name = 'students_management'

def move_scores_sql():
    with open('/Users/i311821/Documents/students_data_27_12_2024.json') as f:
        data = json.load(f)
        scores = data['scores']
        print(len(scores))
        for score in scores:
            student_id = score['student_id']
            lesson_date = score['lesson_date']
            attendance = score['attendance']
            time = score['time']
            uniform = score['uniform']
            participate = score['participate']
            print(f"insert into {schema_name}.scores (student_id, lesson_date, criteria_id, value) values ({student_id}, '{lesson_date}', 1, {attendance});")
            print(f"insert into {schema_name}.scores (student_id, lesson_date, criteria_id, value) values ({student_id}, '{lesson_date}', 2, {time});")
            print(f"insert into {schema_name}.scores (student_id, lesson_date, criteria_id, value) values ({student_id}, '{lesson_date}', 3, {uniform});")
            print(f"insert into {schema_name}.scores (student_id, lesson_date, criteria_id, value) values ({student_id}, '{lesson_date}', 4, {participate});")


def move_students_json():
    with open('/Users/i311821/Documents/students_data_27_12_2024.json') as f:
        # each student looks like this:
        # {
        #     "class_id": 3,
        #     "id": 31,
        #     "name": "\u0627\u062f\u0645 \u0639\u0644\u0627\u0621 \u0635\u0627\u0628\u0631"
        # }
        data = json.load(f)
        students = data['students']
        print(len(students))
        for student in students:
            student_id = student['id']
            student_name = student['name']
            class_id = student['class_id']
            print(f"insert into {schema_name}.students (id, name, class_id) values ({student_id}, '{student_name}', {class_id});")

move_scores_sql()
#move_students_json()