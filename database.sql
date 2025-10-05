-- Step 1: Create a new schema
CREATE SCHEMA school_management;

-- Step 2: Create the teachers table
CREATE TABLE school_management.teachers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password TEXT NOT NULL, -- Assuming the passwords are stored as encoded strings
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

-- Step 3: Create the classes table
CREATE TABLE school_management.classes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Step 4: Create the class_teachers junction table
CREATE TABLE school_management.class_teachers (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL REFERENCES school_management.classes(id) ON DELETE CASCADE,
    teacher_id INTEGER NOT NULL REFERENCES school_management.teachers(id) ON DELETE CASCADE
);

-- Step 5: Create the students table
CREATE TABLE school_management.students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    class_id INTEGER NOT NULL REFERENCES school_management.classes(id) ON DELETE CASCADE,
    active BOOLEAN DEFAULT TRUE,
    inactive_date DATE
);

-- Step 6: Insert data into the teachers table
INSERT INTO school_management.teachers (id, name, password, is_admin) VALUES
(1, 'عمر بدران', 'U2FsYWhFZGxpbjEyMzQ=', TRUE),
(3, 'عدي بدران', 'U2FsYWhFZGxpbjEyMzQ=', FALSE),
(4, 'محمود خربط', 'U2FsYWhFZGxpbjEyMzQ=', FALSE),
(5, 'منير ناصر', 'U2FsYWhFZGxpbjEyMzQ=', FALSE),
(6, 'أسامة زيدان', 'U2FsYWhFZGxpbjEyMzQ=', FALSE);

-- Step 7: Insert data into the classes table
INSERT INTO school_management.classes (id, name) VALUES
(1, 'تاسع - عاشر'),
(2, 'السابع والثامن'),
(3, 'ثالث - رابع'),
(4, 'خامس - سادس'),
(5, 'الحادي عشر - الثاني عشر');

-- Step 8: Insert data into the class_teachers table
INSERT INTO school_management.class_teachers (class_id, teacher_id) VALUES
(1, 1),
(2, 3),
(3, 4),
(4, 5),
(5, 6);

-- Step 9: Insert data into the students table
INSERT INTO school_management.students (id, name, class_id, active, inactive_date) VALUES
(1, 'عمر منهل غانم', 1, TRUE, NULL),
(2, 'احمد منهل غانم', 1, TRUE, NULL),
(3, 'اسيد عامر قطاب', 1, TRUE, NULL),
(4, 'ايهم عامر قطاب', 1, TRUE, NULL),
(5, 'سيف زكي حرز الله', 1, TRUE, NULL),
(6, 'عبد الله سامي زيدان', 1, TRUE, NULL),
(7, 'يحيى عايد غانم', 1, TRUE, NULL),
(8, 'كريم كمال خربط', 1, TRUE, NULL),
(9, 'حسني محمد قطاوي', 1, TRUE, NULL),
(10, 'كريم مراد دقة', 1, TRUE, NULL),
(11, 'احمد خليلية', 1, TRUE, NULL),
(12, 'آدم محمد قطاوي', 2, TRUE, NULL),
(13, 'محمد فايق قطاوي', 2, TRUE, NULL),
(14, 'أمير فادي قطاوي', 2, TRUE, NULL),
(15, 'عبدالله شادي قطاوي', 2, TRUE, NULL),
(16, 'عبادة عبدالعزيز زيدان', 2, TRUE, NULL),
(17, 'وسيم علاء زيدان', 2, TRUE, NULL),
(18, 'سلطان معتز زيدان', 2, TRUE, NULL),
(19, 'ورد لواء أبو ياسين', 2, TRUE, NULL),
(20, 'رويد خالد خطيب', 2, TRUE, NULL),
(21, 'يمان إيهاب بدران', 2, TRUE, NULL),
(22, 'أيسم كامل زيدان', 2, TRUE, NULL),
(23, 'طالب جديد', 2, FALSE, '2024-12-10'),
(24, 'مسلم محمود عمر', 3, TRUE, NULL),
(25, 'يامن عبدالعزيز زيدان', 3, TRUE, NULL),
(26, 'احمد عامر قطاب', 3, TRUE, NULL),
(27, 'منير يوسف غانم', 3, TRUE, NULL),
(28, 'مسلم موفق عمر', 3, TRUE, NULL),
(29, 'احمد محمد دقة', 3, TRUE, NULL),
(30, 'كنان سامر عمر', 3, TRUE, NULL),
(31, 'ادم علاء صابر', 3, TRUE, NULL),
(32, 'عفيف محمود ابو بكر', 3, TRUE, NULL),
(33, 'جود محمد دقة', 3, TRUE, NULL),
(34, 'يحيى ضياء قطاوي', 3, TRUE, NULL),
(35, 'هاشم ماهر غانم', 3, TRUE, NULL),
(36, 'قيس علاء زيدان', 3, TRUE, NULL),
(37, 'رجائي منار دقة', 3, TRUE, NULL),
(38, 'كنان ساهر حرز الله', 3, TRUE, NULL),
(39, 'سند هاني قطاوي', 3, TRUE, NULL),
(40, 'صلاح الدين زكي ياسين', 3, TRUE, NULL),
(41, 'عصام فراس زيدان', 3, TRUE, NULL),
(42, 'ادم امجد غنايم', 3, TRUE, NULL),
(43, 'محمد ياسين', 5, TRUE, NULL),
(44, 'رافع ياسين', 5, TRUE, NULL),
(45, 'امير دقة', 5, TRUE, NULL),
(46, 'سند عمر', 5, TRUE, NULL),
(47, 'ابراهيم غانم', 5, TRUE, NULL),
(48, 'محمد مجادلة', 5, TRUE, NULL),
(49, 'عمر ابو خليل', 5, TRUE, NULL),
(50, 'حمزة ناصر', 5, TRUE, NULL),
(51, 'عبد الرحمن زيدان', 5, TRUE, NULL),
(52, 'كريم يعقوب', 5, TRUE, NULL),
(53, 'حاتم ابو خليل', 5, TRUE, NULL),
(54, 'راني زيدان', 5, TRUE, NULL);

CREATE TABLE school_management.scores (
    id SERIAL PRIMARY KEY,              -- Unique identifier for the score record
    student_id INTEGER NOT NULL,        -- Foreign key referencing the student
    lesson_date DATE NOT NULL,          -- Date of the lesson
    criteria_id INTEGER NOT NULL,       -- Foreign key referencing the criteria
    value BOOLEAN NOT NULL DEFAULT FALSE, -- Value for the criterion
    CONSTRAINT fk_student FOREIGN KEY (student_id) REFERENCES school_management.students (id) ON DELETE CASCADE,
    CONSTRAINT fk_criteria FOREIGN KEY (criteria_id) REFERENCES school_management.criteria (id) ON DELETE CASCADE
);

CREATE TABLE school_management.criteria (
    id SERIAL PRIMARY KEY,         -- Unique identifier for each criterion
    name VARCHAR(100) NOT NULL,    -- Internal name of the criterion
    label VARCHAR(255) NOT NULL    -- Arabic label for the criterion
);

-- Insert the data into the table
INSERT INTO school_management.criteria (id, name, label) VALUES
(1, 'attendance', 'الحضور'),
(2, 'time', 'الالتزام بالوقت'),
(3, 'uniform', 'اللباس الموحد'),
(4, 'participate', 'المشاركة');


SELECT setval('school_management.teachers_id_seq', (SELECT MAX(id) FROM school_management.teachers));
SELECT setval('school_management.students_id_seq', (SELECT MAX(id) FROM school_management.students));
SELECT setval('school_management.classes_id_seq', (SELECT MAX(id) FROM school_management.classes));
SELECT setval('scores_id_seq', (SELECT MAX(id) FROM scores) + 1);
SELECT setval('lesson_info_id_seq', (SELECT MAX(id) FROM lesson_info) + 1);