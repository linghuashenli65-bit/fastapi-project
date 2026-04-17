-- 学生管理系统数据库初始化脚本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS student_management_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE student_management_system;

-- 1. 用户表（基于 fastapi-users）
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    email VARCHAR(320) UNIQUE NOT NULL COMMENT '邮箱',
    hashed_password VARCHAR(1024) NOT NULL COMMENT '加密密码',
    is_active BOOLEAN DEFAULT TRUE NOT NULL COMMENT '是否激活',
    is_superuser BOOLEAN DEFAULT FALSE NOT NULL COMMENT '是否超级管理员',
    is_verified BOOLEAN DEFAULT FALSE NOT NULL COMMENT '是否已验证',
    username VARCHAR(50) UNIQUE COMMENT '用户名',
    full_name VARCHAR(100) COMMENT '全名',
    phone VARCHAR(20) COMMENT '电话',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00' COMMENT '软删除时间',
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_deleted_at (deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 序号生成表
CREATE TABLE IF NOT EXISTS sequence (
    seq_name VARCHAR(50) PRIMARY KEY COMMENT '序列名称',
    current_val INT DEFAULT 0 COMMENT '当前已使用的最大值'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='序号生成辅助表';

-- 2. 班级信息表
CREATE TABLE IF NOT EXISTS class (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    class_no VARCHAR(50) UNIQUE NOT NULL COMMENT '班级编号，格式：YYMMDD+3位序号',
    class_name VARCHAR(100) NOT NULL COMMENT '班级名称',
    start_date DATE COMMENT '开课日期',
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00' COMMENT '软删除时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_class_no (class_no),
    INDEX idx_class_name (class_name),
    INDEX idx_deleted_at (deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='班级信息表';

-- 3. 教师信息表
CREATE TABLE IF NOT EXISTS teacher (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    teacher_no VARCHAR(50) UNIQUE NOT NULL COMMENT '教师编号，格式：YYMM+5位序号',
    name VARCHAR(50) NOT NULL COMMENT '教师姓名',
    gender CHAR(1) CHECK (gender IN ('M', 'F')) COMMENT '性别：M-男 F-女',
    phone VARCHAR(20) COMMENT '电话',
    title VARCHAR(50) COMMENT '职称',
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00' COMMENT '软删除时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_teacher_no (teacher_no),
    INDEX idx_name (name),
    INDEX idx_deleted_at (deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教师信息表';

-- 4. 教师带班历史表
CREATE TABLE IF NOT EXISTS teacher_class (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    teacher_no VARCHAR(50) NOT NULL COMMENT '教师编号，外键引用 teacher.teacher_no',
    class_no VARCHAR(50) NOT NULL COMMENT '班级编号，外键引用 class.class_no',
    role ENUM('head_teacher', 'course_teacher', 'assistant') NOT NULL COMMENT '教师角色：班主任/讲师/助教',
    start_date DATE NOT NULL COMMENT '开始带班日期',
    end_date DATE COMMENT '结束带班日期',
    is_current TINYINT DEFAULT 0 COMMENT '是否当前带班',
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00' COMMENT '软删除时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (teacher_no) REFERENCES teacher(teacher_no) ON DELETE CASCADE,
    FOREIGN KEY (class_no) REFERENCES class(class_no) ON DELETE CASCADE,
    INDEX idx_teacher_no (teacher_no),
    INDEX idx_class_no (class_no),
    INDEX idx_is_current (is_current),
    INDEX idx_deleted_at (deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教师带班历史表';

-- 5. 学生基本信息表
CREATE TABLE IF NOT EXISTS student (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    student_no VARCHAR(50) UNIQUE NOT NULL COMMENT '学号，格式：YYMM+5位序号',
    name VARCHAR(50) NOT NULL COMMENT '学生姓名',
    gender CHAR(1) CHECK (gender IN ('M', 'F')) COMMENT '性别：M-男 F-女',
    birth_date DATE COMMENT '出生日期',
    birthplace VARCHAR(100) COMMENT '籍贯',
    graduated_school VARCHAR(100) COMMENT '毕业院校',
    major VARCHAR(100) COMMENT '专业',
    enrollment_date DATE COMMENT '入学日期',
    graduation_date DATE COMMENT '毕业时间',
    education TINYINT CHECK (education IN (1, 2, 3, 4, 5)) COMMENT '学历：1-高中 2-大专 3-本科 4-硕士 5-博士',
    consultant_no VARCHAR(50) COMMENT '顾问编号，外键引用 teacher.teacher_no',
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00' COMMENT '软删除时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (consultant_no) REFERENCES teacher(teacher_no) ON DELETE SET NULL,
    INDEX idx_student_no (student_no),
    INDEX idx_name (name),
    INDEX idx_major (major),
    INDEX idx_deleted_at (deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生基本信息表';

-- 6. 学生班级归属历史表
CREATE TABLE IF NOT EXISTS student_class (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    student_no VARCHAR(50) NOT NULL COMMENT '学号，外键引用 student.student_no',
    class_no VARCHAR(50) NOT NULL COMMENT '班级编号，外键引用 class.class_no',
    start_date DATE NOT NULL COMMENT '进入该班级的日期',
    end_date DATE COMMENT '离开该班级的日期',
    is_current TINYINT DEFAULT 0 COMMENT '是否当前班级',
    reason VARCHAR(50) COMMENT '变动原因：normal/demotion/transfer',
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00' COMMENT '软删除时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (student_no) REFERENCES student(student_no) ON DELETE CASCADE,
    FOREIGN KEY (class_no) REFERENCES class(class_no) ON DELETE CASCADE,
    INDEX idx_student_no (student_no),
    INDEX idx_class_no (class_no),
    INDEX idx_is_current (is_current),
    INDEX idx_deleted_at (deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生班级归属历史表';

-- 7. 学生考核成绩表
CREATE TABLE IF NOT EXISTS score (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    student_no VARCHAR(50) NOT NULL COMMENT '学号，外键引用 student.student_no',
    class_no VARCHAR(50) NOT NULL COMMENT '班级编号，外键引用 class.class_no',
    start_date DATE NOT NULL COMMENT '对应 student_class 的进入日期',
    exam_sequence INT NOT NULL COMMENT '考核序次',
    exam_date DATE NOT NULL COMMENT '考试日期',
    score DECIMAL(5,2) CHECK (score >= 0 AND score <= 100) COMMENT '成绩',
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00' COMMENT '软删除时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (student_no) REFERENCES student(student_no) ON DELETE CASCADE,
    FOREIGN KEY (class_no) REFERENCES class(class_no) ON DELETE CASCADE,
    INDEX idx_student_no (student_no),
    INDEX idx_class_no (class_no),
    INDEX idx_exam_date (exam_date),
    INDEX idx_deleted_at (deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生考核成绩表';

-- 8. 学生offer与就业信息表
CREATE TABLE IF NOT EXISTS employment (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    student_no VARCHAR(50) NOT NULL COMMENT '学号，外键引用 student.student_no',
    company_name VARCHAR(100) NOT NULL COMMENT '公司名称',
    job_title VARCHAR(100) NOT NULL COMMENT '职位名称',
    salary INT NOT NULL COMMENT '薪资，单位千元/月',
    offer_date DATE COMMENT 'offer下发时间',
    employment_start_date DATE COMMENT '实际入职时间',
    record_type ENUM('offer', 'employment') NOT NULL COMMENT '记录类型',
    is_current TINYINT DEFAULT 0 COMMENT '是否当前就业，仅employment类型有效',
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00' COMMENT '软删除时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (student_no) REFERENCES student(student_no) ON DELETE CASCADE,
    INDEX idx_student_no (student_no),
    INDEX idx_company_name (company_name),
    INDEX idx_offer_date (offer_date),
    INDEX idx_record_type (record_type),
    INDEX idx_is_current (is_current),
    INDEX idx_deleted_at (deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生offer与就业信息表';

-- 初始化示例数据（可选）
-- 注释掉以下内容以避免在测试时自动插入数据

-- INSERT INTO teacher (teacher_no, name, gender, phone, title) VALUES
-- ('250100001', '张老师', 'M', '13800138000', '讲师'),
-- ('250100002', '李老师', 'F', '13800138001', '副教授'),
-- ('250100003', '王老师', 'M', '13800138002', '教授');

-- INSERT INTO class (class_no, class_name, start_date) VALUES
-- ('240101001', 'Java2401', '2024-01-01'),
-- ('240201001', 'Python2401', '2024-02-01'),
-- ('240301001', '前端2401', '2024-03-01');

-- INSERT INTO student (student_no, name, gender, enrollment_date, education) VALUES
-- ('240100001', '张三', 'M', '2024-01-01', 3),
-- ('240100002', '李四', 'F', '2024-01-01', 3),
-- ('240100003', '王五', 'M', '2024-01-01', 2);

-- INSERT INTO student_class (student_no, class_no, start_date, is_current) VALUES
-- ('240100001', '240101001', '2024-01-01', 1),
-- ('240100002', '240101001', '2024-01-01', 1),
-- ('240100003', '240101001', '2024-01-01', 1);

-- INSERT INTO score (student_no, class_no, start_date, exam_sequence, exam_date, score) VALUES
-- ('240100001', '240101001', '2024-01-01', 1, '2024-01-15', 85.5),
-- ('240100002', '240101001', '2024-01-01', 1, '2024-01-15', 92.0),
-- ('240100003', '240101001', '2024-01-01', 1, '2024-01-15', 78.5);

-- INSERT INTO employment (student_no, company_name, job_title, salary, offer_date, record_type) VALUES
-- ('240100001', '阿里巴巴', 'Java开发工程师', 20, '2024-03-01', 'offer'),
-- ('240100002', '腾讯', 'Python开发工程师', 18, '2024-03-05', 'offer');
