
-- Step 1: Create Database
CREATE EXTENSION dblink;

DO
$do$
BEGIN
   IF EXISTS (SELECT FROM pg_database WHERE datname = 'school_management') THEN
      RAISE NOTICE 'Database already exists';  -- optional
   ELSE
      PERFORM dblink_exec('dbname=' || current_database()  -- current db
                        , 'CREATE DATABASE school_management');
   END IF;
END
$do$;

-- Step 2: Create the teachers table
CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL -- Assuming the passwords are stored as encoded strings
);

-- Step 3: Create the classes table
CREATE TABLE IF NOT EXISTS classes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Step 4: Create the class_teachers junction table
CREATE TABLE IF NOT EXISTS class_teachers (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE
);

-- Step 5: Create the students table
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    active BOOLEAN DEFAULT TRUE,
    inactive_date DATE, 
	phone VARCHAR(16) DEFAULT NULL,
	parent_phone VARCHAR(16) DEFAULT NULL,
	date_joined  DATE
);

CREATE TABLE IF NOT EXISTS criteria (
    id SERIAL PRIMARY KEY,         -- Unique identifier for each criterion
    name VARCHAR(100) NOT NULL,    -- Internal name of the criterion
    label VARCHAR(255) NOT NULL    -- Arabic label for the criterion
);

CREATE TABLE IF NOT EXISTS scores (
    id SERIAL PRIMARY KEY,              -- Unique identifier for the score record
    student_id INTEGER NOT NULL,        -- Foreign key referencing the student
    lesson_date DATE NOT NULL,          -- Date of the lesson
    criteria_id INTEGER NOT NULL,       -- Foreign key referencing the criteria
    value BOOLEAN NOT NULL DEFAULT FALSE, -- Value for the criterion
	notes TEXT,
    CONSTRAINT fk_student FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    CONSTRAINT fk_criteria FOREIGN KEY (criteria_id) REFERENCES criteria (id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS lesson_info (
    id SERIAL PRIMARY KEY,              -- Unique identifier for the score record
    class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    lesson_date DATE NOT NULL,          -- Date of the lesson
    lesson_subject TEXT,
    lesson_activity TEXT
);

SELECT setval('teachers_id_seq', (SELECT MAX(id) FROM teachers));
SELECT setval('students_id_seq', (SELECT MAX(id) FROM students));
SELECT setval('classes_id_seq', (SELECT MAX(id) FROM classes));

-- Fill Data
INSERT INTO teachers ("id", "name", "password", "username") VALUES ('1', 'عمر بدران', 'MTIz', 'omarb'), ('3', 'عدي بدران', 'MTIz', 'odaib'), ('4', 'محمود خربط', 'MTIz', 'mahmoudk'), ('5', 'منير ناصر', 'MTIz', 'munirn'), ('6', 'أسامة زيدان', 'MTIz', 'osamaz'), ('11', 'خلود عمر', 'MTIz', 'kholodomar'), ('12', 'نداء زيدان', 'MTIz', 'nedaazedan'), ('13', 'ميسم عمر', 'MTIz', 'maisamomar'), ('14', 'سجود عمر', 'MTIz', 'sojoodomar'), ('15', 'رنا أبو سارة', 'MTIz', 'ranaabusara'), ('16', 'إسراء غانم', 'MTIz', 'israaganem'), ('17', 'ساجدة عمر', 'MTIz', 'sajidaomar'), ('18', 'منى عويسات', 'MTIz', 'monaowesat'), ('19', 'شيماء غانم', 'MTIz', 'shaimaganem'), ('20', 'هيام أبو سارة', 'MTIz', 'hiyamabusara'), ('21', 'إسراء أبو ياسين', 'MTIz', 'israaabuyasin'), ('22', 'بيان وتد', 'MTIz', 'bayanwatad');
INSERT INTO criteria ("id", "name", "label") VALUES ('1', 'attendance', 'الحضور'), ('2', 'time', 'الالتزام بالوقت'), ('3', 'uniform', 'اللباس الموحد'), ('4', 'participate', 'المشاركة');
INSERT INTO classes ("id", "name") VALUES ('1', 'تاسع - عاشر'), ('2', 'السابع والثامن'), ('3', 'ثالث - رابع'), ('4', 'خامس - سادس'), ('5', 'الحادي عشر - الثاني عشر'), ('6', 'بستان - إناث'), ('7', 'أول - إناث'), ('8', 'ثاني - إناث'), ('9', 'ثالث رابع اناث'), ('10', 'خامس اناث'), ('11', 'إعدادي إناث'), ('12', 'ثانوي إناث'), ('13', 'أول ثاني ذكور');

INSERT INTO class_teachers ("id", "class_id", "teacher_id") VALUES ('1', '1', '1'), ('2', '2', '3'), ('3', '3', '4'), ('4', '4', '5'), ('5', '5', '6'), ('6', '5', '1'), ('7', '6', '11'), ('8', '6', '12'), ('9', '7', '13'), ('10', '8', '14'), ('11', '9', '15'), ('12', '10', '16'), ('13', '10', '17'), ('14', '11', '18'), ('15', '12', '19'), ('16', '12', '20'), ('17', '13', '21'), ('18', '13', '22'), ('19', '12', '22'), ('20', '11', '22'), ('21', '10', '22'), ('22', '9', '22'), ('23', '8', '22'), ('24', '7', '22'), ('25', '6', '22'), ('26', '7', '5'), ('27', '8', '5'), ('28', '9', '5'), ('29', '10', '5'), ('30', '11', '5'), ('31', '12', '5'), ('32', '13', '5');

INSERT INTO students ("id", "name", "class_id", "active", "inactive_date", "phone", "parent_phone", "date_joined") VALUES ('1', 'عمر منهل غانم', '1', 'true', null, null, null, null), ('2', 'احمد منهل غانم', '1', 'true', null, null, null, null), ('3', 'اسيد عامر قطاب', '1', 'true', null, null, null, null), ('4', 'ايهم عامر قطاب', '1', 'true', null, null, null, null), ('5', 'سيف زكي حرز الله', '1', 'true', null, null, null, null), ('6', 'عبد الله سامي زيدان', '1', 'true', null, null, null, null), ('7', 'يحيى عايد غانم', '1', 'true', null, null, null, null), ('8', 'كريم كمال خربط', '1', 'true', null, null, null, null), ('9', 'حسني محمد قطاوي', '1', 'true', null, null, null, null), ('10', 'كريم مراد دقة', '1', 'true', null, null, null, null), ('11', 'احمد خليلية', '1', 'true', null, null, null, null), ('12', 'آدم محمد3 قطاوي', '2', null, null, null, null, null), ('13', 'محمد فايق 4vقطاوي', '2', 'false', '2024-12-14', null, null, null), ('14', 'أمير فادي قطاوي', '2', 'true', null, null, null, null), ('15', 'عبدالله شادي قطاوي', '2', 'true', null, null, null, null), ('16', 'عبادة عبدالعزيز زيدان', '2', 'true', null, null, null, null), ('17', 'وسيم علاء زيدان', '2', 'true', null, null, null, null), ('18', 'سلطان معتز زيدان', '2', 'true', null, null, null, null), ('19', 'ورد لواء أبو ياسين', '2', 'true', null, null, null, null), ('20', 'رويد خالد خطيب', '2', 'true', null, null, null, null), ('21', 'يمان إيهاب بدران', '2', 'true', null, null, null, null), ('22', 'أيسم كامل زيدان', '2', 'false', '2024-12-14', null, null, null), ('23', 'طالب جديد', '2', 'false', '2024-12-10', null, null, null), ('24', 'مسلم محمود عمر', '3', 'true', null, null, null, null), ('25', 'يامن عبدالعزيز زيدان', '3', 'true', null, null, null, null), ('26', 'احمد عامر قطاب', '3', 'true', null, null, null, null), ('27', 'منير يوسف غانم', '3', 'true', null, null, null, null), ('28', 'مسلم موفق عمر', '3', 'true', null, null, null, null), ('29', 'احمد محمد دقة', '3', 'true', null, null, null, null), ('30', 'كنان سامر عمر', '3', 'true', null, null, null, null), ('31', 'ادم علاء صابر', '3', 'true', null, null, null, null), ('32', 'عفيف محمود ابو بكر', '3', 'true', null, null, null, null), ('33', 'جود محمد دقة', '3', 'true', null, null, null, null), ('34', 'يحيى ضياء قطاوي', '3', 'true', null, null, null, null), ('35', 'هاشم ماهر غانم', '3', 'true', null, null, null, null), ('36', 'قيس علاء زيدان', '3', 'true', null, null, null, null), ('37', 'رجائي منار دقة', '3', 'true', null, null, null, null), ('38', 'كنان ساهر حرز الله', '3', 'true', null, null, null, null), ('39', 'سند هاني قطاوي', '3', 'true', null, null, null, null), ('40', 'صلاح الدين زكي ياسين', '3', 'true', null, null, null, null), ('41', 'عصام فراس زيدان', '3', 'true', null, null, null, null), ('42', 'ادم امجد غنايم', '3', 'true', null, null, null, null), ('43', 'محمد ياسين', '5', 'true', null, null, null, null), ('44', 'رافع ياسين', '5', 'true', null, null, null, null), ('45', 'امير دقة', '5', 'true', null, null, null, null), ('46', 'سند عمر', '5', 'true', null, null, null, null), ('47', 'ابراهيم غانم', '5', 'true', null, null, null, null), ('48', 'محمد مجادلة', '5', 'true', null, null, null, null), ('49', 'عمر ابو خليل', '5', 'true', null, null, null, null), ('50', 'حمزة ناصر', '5', 'true', null, null, null, null), ('51', 'عبد الرحمن زيدان', '5', 'true', null, null, null, null), ('52', 'كريم يعقوب', '5', 'true', null, null, null, null), ('53', 'حاتم ابو خليل', '5', 'true', null, null, null, null), ('54', 'راني زيدان', '5', 'true', null, null, null, null), ('55', 'يزن دقة', '2', 'false', '2024-12-14', '0503137653', '0503137653', '2024-12-14'), ('56', 'عطوان دلو', '6', 'true', null, '0503137653', '0503137653', '2024-12-13'), ('57', 'عمر بدران', '1', 'true', null, '0503137653', '0503137653', '2024-12-17'), ('58', 'مؤمن كامل زيدان', '4', 'true', null, null, null, null), ('59', 'عقل علاء زيدان', '4', 'true', null, null, null, null), ('60', 'آدم مفيد دقة', '4', 'true', null, null, null, null), ('61', 'كريم جعفر عمر', '4', 'true', null, null, null, null), ('62', 'جود عبد اللطيف زيدان', '4', 'true', null, null, null, null), ('63', 'عمر حسين عمر', '4', 'true', null, null, null, null), ('64', 'مؤمن ايهاب غانم', '4', 'true', null, null, null, null), ('65', 'قيصر محمود غانم', '4', 'true', null, null, null, null), ('66', 'حسن شادي عمر', '4', 'true', null, null, null, null), ('67', 'عبادة مهند ياسين', '4', 'true', null, null, null, null), ('68', 'محمد عايد غانم', '4', 'true', null, null, null, null), ('69', 'عبد الرحمن عادل زيدان', '4', 'true', null, null, null, null);
INSERT INTO teachers ("id", "name", "password", "username") VALUES ('1', 'عمر بدران', 'MTIz', 'omarb'), ('3', 'عدي بدران', 'MTIz', 'odaib'), ('4', 'محمود خربط', 'MTIz', 'mahmoudk'), ('5', 'منير ناصر', 'MTIz', 'munirn'), ('6', 'أسامة زيدان', 'MTIz', 'osamaz'), ('11', 'خلود عمر', 'MTIz', 'kholodomar'), ('12', 'نداء زيدان', 'MTIz', 'nedaazedan'), ('13', 'ميسم عمر', 'MTIz', 'maisamomar'), ('14', 'سجود عمر', 'MTIz', 'sojoodomar'), ('15', 'رنا أبو سارة', 'MTIz', 'ranaabusara'), ('16', 'إسراء غانم', 'MTIz', 'israaganem'), ('17', 'ساجدة عمر', 'MTIz', 'sajidaomar'), ('18', 'منى عويسات', 'MTIz', 'monaowesat'), ('19', 'شيماء غانم', 'MTIz', 'shaimaganem'), ('20', 'هيام أبو سارة', 'MTIz', 'hiyamabusara'), ('21', 'إسراء أبو ياسين', 'MTIz', 'israaabuyasin'), ('22', 'بيان وتد', 'MTIz', 'bayanwatad');
INSERT INTO scores ("id", "student_id", "lesson_date", "criteria_id", "value", "notes") VALUES ('3404', '55', '2024-12-13', '1', 'true', null), ('3405', '55', '2024-12-13', '2', 'true', null), ('3406', '55', '2024-12-13', '3', 'false', null), ('3407', '55', '2024-12-13', '4', 'true', null), ('3408', '56', '2024-12-13', '1', 'true', null), ('3409', '56', '2024-12-13', '2', 'true', null), ('3410', '56', '2024-12-13', '3', 'false', null), ('3411', '56', '2024-12-13', '4', 'false', null), ('3412', '57', '2024-12-13', '1', 'true', null), ('3413', '57', '2024-12-13', '2', 'true', null), ('3414', '57', '2024-12-13', '3', 'true', null), ('3415', '57', '2024-12-13', '4', 'false', null), ('3416', '58', '2024-12-13', '1', 'true', null), ('3417', '58', '2024-12-13', '2', 'true', null), ('3418', '58', '2024-12-13', '3', 'true', null), ('3419', '58', '2024-12-13', '4', 'false', null), ('3420', '59', '2024-12-13', '1', 'true', null), ('3421', '59', '2024-12-13', '2', 'true', null), ('3422', '59', '2024-12-13', '3', 'false', null), ('3423', '59', '2024-12-13', '4', 'false', null), ('3424', '60', '2024-12-13', '1', 'true', null), ('3425', '60', '2024-12-13', '2', 'true', null), ('3426', '60', '2024-12-13', '3', 'false', null), ('3427', '60', '2024-12-13', '4', 'false', null), ('3428', '61', '2024-12-13', '1', 'true', null), ('3429', '61', '2024-12-13', '2', 'true', null), ('3430', '61', '2024-12-13', '3', 'false', null), ('3431', '61', '2024-12-13', '4', 'false', null), ('3432', '62', '2024-12-13', '1', 'true', null), ('3433', '62', '2024-12-13', '2', 'true', null), ('3434', '62', '2024-12-13', '3', 'true', null), ('3435', '62', '2024-12-13', '4', 'false', null), ('3436', '63', '2024-12-13', '1', 'true', null), ('3437', '63', '2024-12-13', '2', 'true', null), ('3438', '63', '2024-12-13', '3', 'false', null), ('3439', '63', '2024-12-13', '4', 'false', null), ('3440', '64', '2024-12-13', '1', 'true', null), ('3441', '64', '2024-12-13', '2', 'false', null), ('3442', '64', '2024-12-13', '3', 'true', null), ('3443', '64', '2024-12-13', '4', 'false', null), ('3444', '65', '2024-12-13', '1', 'false', null), ('3445', '65', '2024-12-13', '2', 'false', null), ('3446', '65', '2024-12-13', '3', 'false', null), ('3447', '65', '2024-12-13', '4', 'false', null), ('3448', '24', '2024-12-13', '1', 'true', null), ('3449', '24', '2024-12-13', '2', 'true', null), ('3450', '24', '2024-12-13', '3', 'false', null), ('3451', '24', '2024-12-13', '4', 'true', null), ('3452', '25', '2024-12-13', '1', 'true', null), ('3453', '25', '2024-12-13', '2', 'true', null), ('3454', '25', '2024-12-13', '3', 'true', null), ('3455', '25', '2024-12-13', '4', 'false', null), ('3456', '26', '2024-12-13', '1', 'false', null), ('3457', '26', '2024-12-13', '2', 'false', null), ('3458', '26', '2024-12-13', '3', 'false', null), ('3459', '26', '2024-12-13', '4', 'false', null), ('3460', '27', '2024-12-13', '1', 'false', null), ('3461', '27', '2024-12-13', '2', 'false', null), ('3462', '27', '2024-12-13', '3', 'false', null), ('3463', '27', '2024-12-13', '4', 'false', null), ('3464', '28', '2024-12-13', '1', 'true', null), ('3465', '28', '2024-12-13', '2', 'true', null), ('3466', '28', '2024-12-13', '3', 'true', null), ('3467', '28', '2024-12-13', '4', 'false', null), ('3468', '29', '2024-12-13', '1', 'true', null), ('3469', '29', '2024-12-13', '2', 'true', null), ('3470', '29', '2024-12-13', '3', 'true', null), ('3471', '29', '2024-12-13', '4', 'false', null), ('3472', '30', '2024-12-13', '1', 'false', null), ('3473', '30', '2024-12-13', '2', 'false', null), ('3474', '30', '2024-12-13', '3', 'false', null), ('3475', '30', '2024-12-13', '4', 'false', null), ('3476', '31', '2024-12-13', '1', 'true', null), ('3477', '31', '2024-12-13', '2', 'false', null), ('3478', '31', '2024-12-13', '3', 'false', null), ('3479', '31', '2024-12-13', '4', 'false', null), ('3480', '32', '2024-12-13', '1', 'true', null), ('3481', '32', '2024-12-13', '2', 'true', null), ('3482', '32', '2024-12-13', '3', 'true', null), ('3483', '32', '2024-12-13', '4', 'true', null), ('3484', '33', '2024-12-13', '1', 'false', null), ('3485', '33', '2024-12-13', '2', 'false', null), ('3486', '33', '2024-12-13', '3', 'false', null), ('3487', '33', '2024-12-13', '4', 'false', null), ('3488', '34', '2024-12-13', '1', 'false', null), ('3489', '34', '2024-12-13', '2', 'false', null), ('3490', '34', '2024-12-13', '3', 'false', null), ('3491', '34', '2024-12-13', '4', 'false', null), ('3492', '35', '2024-12-13', '1', 'true', null), ('3493', '35', '2024-12-13', '2', 'true', null), ('3494', '35', '2024-12-13', '3', 'true', null), ('3495', '35', '2024-12-13', '4', 'true', null), ('3496', '36', '2024-12-13', '1', 'true', null), ('3497', '36', '2024-12-13', '2', 'true', null), ('3498', '36', '2024-12-13', '3', 'true', null), ('3499', '36', '2024-12-13', '4', 'false', null), ('3500', '37', '2024-12-13', '1', 'false', null), ('3501', '37', '2024-12-13', '2', 'false', null), ('3502', '37', '2024-12-13', '3', 'false', null), ('3503', '37', '2024-12-13', '4', 'false', null);

INSERT INTO lesson_info ("id", "class_id", "lesson_date", "lesson_subject", "lesson_activity") VALUES ('25', '4', '2025-02-14', '111111', ''), ('29', '5', '2025-02-28', 'احكام الطهارة/الاستعداد لرمضان', ''), ('30', '5', '2025-03-07', 'رحلة الأقصى', ''), ('31', '4', '2025-03-07', 'رمضان - اخلاق وحكم تتعلق برمضان', ''), ('32', '4', '2025-02-28', 'رمضان، اكثر شيء تحبه في رمضان. تذكير بالمسابقة', ''), ('33', '4', '2025-02-21', ' ', ''), ('34', '3', '2025-03-07', 'القران', ''), ('35', '2', '2025-03-07', 'رمضان شهر القرءلن', 'فعالية اعرف السورة او "هل سورتي .."'), ('36', '2', '2025-02-28', ' أحكام الصيام للجيل الإعدادي', ''), ('37', '4', '2025-03-21', 'اداب الصيام', 'مسابقة كاهوت'), ('38', '3', '2025-03-14', 'افطار رمضان ', ''), ('39', '3', '2025-03-21', 'الاخلاق', ''), ('40', '2', '2025-03-21', 'رمضان شهر التغيير', ''), ('41', '2', '2025-03-28', 'حسن الخلق', ''), ('42', '4', '2025-03-28', 'الله يختار زمانا دون زمان … رمضان مثالا', 'توزيع عيدية، وهدية من المركز'), ('43', '3', '2025-04-11', 'اداب الذهاب الى المسجد', ''), ('44', '4', '2025-04-11', 'الاخوة في الله', ''), ('45', '4', '2025-04-18', 'ذكر الله وانواعه والتفكر في خلق الله', 'حفظ وتذكر احاديث وايات عن الذكر');
