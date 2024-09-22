use college_placement;
select * from student_profile;
CREATE TABLE IF NOT EXISTS signup (
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);
truncate student_profile;
select * from signup;
CREATE TABLE admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100)
);
UPDATE student_profile 
                SET  STUDENT_USN=%s, FIRST_NAME=%s, LAST_NAME=%s, DATE_OF_BIRTH=%s, EMAIL_ID=%s, SSLC_MARKS=%s, 
            PUC_MARKS=%s, BE_CGPA=%s, SKILLS=%s, ACHIEVEMENTS=%s, JOB_TYPE=%s, RESUME=%s, PHOTO=%s, GENDER=%s, PHONE_NUMBER=%s, BRANCH=%s
drop table admin_users;
select * from admin_users;