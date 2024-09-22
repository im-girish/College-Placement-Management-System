import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
from mysql.connector import Error
import PyPDF2
import re

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port="3307",
            user="root",
            password="Hegde@123",  # Replace with your MySQL password
            database="college_placement"
        )
        if connection.is_connected():
            print("Successfully connected to the database")
            return connection
    except Error as e:
        print(f"Error: '{e}'")
    return None

def insert_admin_user(first_name, last_name, email, password):
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            sql_insert_query = """
            INSERT INTO admin_users (first_name, last_name, email, password)
            VALUES (%s, %s, %s, %s)
            """
            insert_tuple = (first_name, last_name, email, password)
            cursor.execute(sql_insert_query, insert_tuple)
            connection.commit()
            print("Admin record inserted successfully")
            cursor.close()
        else:
            print("Failed to connect to the database")
    except Error as e:
        print(f"Error: '{e}'")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("Database connection closed")

def verify_admin_user(email, password):
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            sql_select_query = "SELECT * FROM admin_users WHERE email = %s AND password = %s"
            cursor.execute(sql_select_query, (email, password))
            record = cursor.fetchone()
            cursor.close()
            return bool(record)
    except Error as e:
        print(f"Error: '{e}'")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("Database connection closed")
    return False

@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Basic form validation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('admin_signup'))

        # Save admin user to the database
        insert_admin_user(first_name, last_name, email, password)
        flash('Admin Signup successful!', 'success')
        return redirect(url_for('index'))

    return render_template('admin_signup.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if verify_admin_user(email, password):
            session['admin_email'] = email
            return redirect(url_for('enter_requirements'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_email' in session:
        return render_template('admin_dashboard.html')
    else:
        return redirect(url_for('admin_login'))

def insert_user(first_name, last_name, email, password):
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            sql_insert_query = """
            INSERT INTO signup (first_name, last_name, email, password)
            VALUES (%s, %s, %s, %s)
            """
            insert_tuple = (first_name, last_name, email, password)
            cursor.execute(sql_insert_query, insert_tuple)
            connection.commit()
            print("Record inserted successfully")
            cursor.close()
        else:
            print("Failed to connect to the database")
    except Error as e:
        print(f"Error: '{e}'")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("Database connection closed")

def verify_user(email, password):
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            sql_select_query = "SELECT * FROM signup WHERE email = %s AND password = %s"
            cursor.execute(sql_select_query, (email, password))
            record = cursor.fetchone()
            cursor.close()
            return bool(record)
    except Error as e:
        print(f"Error: '{e}'")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("Database connection closed")
    return False

def insert_user_registration(student_name, username, password, email, class_name, sslc_marks, puc_marks, address, country, state, board, academic_performance, photo):
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            sql_insert_query = """
            INSERT INTO student_registration (student_name, username, password, email, class_name, sslc_marks, puc_marks, address, country, state, board, academic_performance, photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            insert_tuple = (student_name, username, password, email, class_name, sslc_marks, puc_marks, address, country, state, board, academic_performance, photo)
            cursor.execute(sql_insert_query, insert_tuple)
            connection.commit()
            print("Record inserted successfully")
            cursor.close()
        else:
            print("Failed to connect to the database")
    except Error as e:
        print(f"Error: '{e}'")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("Database connection closed")

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"An error occurred: {e}")
    return text

def match_resume_with_job_requirements(resume_text, job_requirements):
    matches = {
        "skills": [],
        "experience": [],
        "education": []
    }
    
    for skill in job_requirements["skills"]:
        if re.search(rf"\b{skill}\b", resume_text, re.IGNORECASE):
            matches["skills"].append(skill)
    
    for exp in job_requirements["experience"]:
        if re.search(rf"\b{exp}\b", resume_text, re.IGNORECASE):
            matches["experience"].append(exp)
    
    for edu in job_requirements["education"]:
        if re.search(rf"\b{edu}\b", resume_text, re.IGNORECASE):
            matches["education"].append(edu)
    
    return matches

def evaluate_match(matched_requirements, job_requirements):
    total_requirements = sum(len(v) for v in job_requirements.values())
    total_matches = sum(len(v) for v in matched_requirements.values())
    
    match_percentage = (total_matches / total_requirements) * 100
    return match_percentage

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Basic form validation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))

        # Save user to the database
        insert_user(first_name, last_name, email, password)
        flash('Signup successful!', 'success')
        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if verify_user(email, password):
            session['email'] = email
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/student_registration')
def student_registration():
    if 'email' in session:
        return render_template('student_registeration.html')
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Extracting form data
        STUDENT_USN = request.form['STUDENT_USN']
        FIRST_NAME = request.form['FIRST_NAME']
        LAST_NAME = request.form['LAST_NAME']
        DATE_OF_BIRTH = request.form['DATE_OF_BIRTH']
        EMAIL_ID = request.form['EMAIL_ID']
        SSLC_MARKS = float(request.form['SSLC_MARKS'])
        PUC_MARKS = float(request.form['PUC_MARKS'])
        BE_CGPA = float(request.form['BE_CGPA'])
        SKILLS = request.form['SKILLS']
        ACHIEVEMENTS = request.form.get('ACHIEVEMENTS', '')  # Optional field
        JOB_TYPE = request.form['JOB_TYPE']
        
        # Handling file uploads
        resume_file = request.files['RESUME']
        photo_file = request.files['PHOTO']
        
        resume_filename = resume_file.filename
        photo_filename = photo_file.filename
        
        resume_file.save(os.path.join(app.config['UPLOAD_FOLDER'], resume_filename))
        photo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        
        GENDER = request.form['GENDER']
        PHONE_NUMBER = request.form['PHONE_NUMBER']
        BRANCH = request.form['BRANCH']

        # SQL query to insert data
        sql_query = """
        INSERT INTO STUDENT_PROFILE(
            STUDENT_USN, FIRST_NAME, LAST_NAME, DATE_OF_BIRTH, EMAIL_ID, SSLC_MARKS, 
            PUC_MARKS, BE_CGPA, SKILLS, ACHIEVEMENTS, JOB_TYPE, RESUME, PHOTO, GENDER, PHONE_NUMBER, BRANCH
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (
            STUDENT_USN, FIRST_NAME, LAST_NAME, DATE_OF_BIRTH, EMAIL_ID, SSLC_MARKS, 
            PUC_MARKS, BE_CGPA, SKILLS, ACHIEVEMENTS, JOB_TYPE, resume_filename, photo_filename, 
            GENDER, PHONE_NUMBER, BRANCH
        )
        
        # Execute the query and commit the transaction
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(sql_query, data)
            connection.commit()  # Commit the transaction to save the changes
            cursor.close()
        
        return redirect(url_for('profile', student_usn=STUDENT_USN))
    
    except KeyError as e:
        # Handle the case where a key is missing
        return f"KeyError: Missing form field {e}"

    except Exception as e:
        # Handle any other exceptions
        return f"An error occurred: {e}"
    
#student after login
@app.route('/student_profile')
def student_profile():
    if 'email' in session:
        email = session['email']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM student_registration WHERE email = %s", (email,))
            student = cursor.fetchone()
            cursor.close()
            
            if not student:
                return "Student not found!"

            student_profile = {
                'student_name': student[0],
                'username': student[1],
                'password': student[2],
                'email': student[3],
                'class_name': student[4],
                'sslc_marks': student[5],
                'puc_marks': student[6],
                'address': student[7],
                'country': student[8],
                'state': student[9],
                'board': student[10],
                'academic_performance': student[11],
                'photo': student[12]
            }

            return render_template('student_profile.html', student=student_profile)
        
        return "Database connection failed"
    else:
        return redirect(url_for('login'))


@app.route('/profile/<student_usn>')
def profile(student_usn):
    # Query the database to retrieve student data
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM STUDENT_PROFILE WHERE STUDENT_USN = %s", (student_usn,))
        student = cursor.fetchone()
        cursor.close()
        
        if not student:
            return "Student not found!"

        student_profile = {
            'STUDENT_USN': student[0],
            'FIRST_NAME': student[1],
            'LAST_NAME': student[2],
            'DATE_OF_BIRTH': student[3],
            'EMAIL_ID': student[4],
            'SSLC_MARKS': student[5],
            'PUC_MARKS': student[6],
            'BE_CGPA': student[7],
            'SKILLS': student[8],
            'ACHIEVEMENTS': student[9],
            'JOB_TYPE': student[10],
            'RESUME': student[11],
            'PHOTO': student[12],
            'GENDER': student[13],
            'PHONE_NUMBER': student[14],
            'BRANCH': student[15]
        }

        return render_template('profile.html', student=student_profile)
    
    return "Database connection failed"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        file = request.files['resume']
        if file and file.filename.endswith('.pdf'):  # Check if the file is PDF
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            return redirect(url_for('index'))
    return render_template('upload_resume.html')

@app.route('/enter_requirements', methods=['GET', 'POST'])
def enter_requirements():
    if request.method == 'POST':
        skills = request.form.get('skills').split(',')
        experience = request.form.get('experience').split(',')
        education = request.form.get('education').split(',')
        job_requirements = {
            "skills": [skill.strip() for skill in skills],
            "experience": [exp.strip() for exp in experience],
            "education": [edu.strip() for edu in education]
        }
        return redirect(url_for('match_resumes', skills=skills, experience=experience, education=education))
    return render_template('enter_requirements.html')

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"An error occurred: {e}")
    return text

def match_resume_with_job_requirements(resume_text, job_requirements):
    matches = {
        "skills": [],
        "experience": [],
        "education": []
    }
    
    for skill in job_requirements["skills"]:
        if re.search(rf"\b{skill}\b", resume_text, re.IGNORECASE):
            matches["skills"].append(skill)
    
    for exp in job_requirements["experience"]:
        if re.search(rf"\b{exp}\b", resume_text, re.IGNORECASE):
            matches["experience"].append(exp)
    
    for edu in job_requirements["education"]:
        if re.search(rf"\b{edu}\b", resume_text, re.IGNORECASE):
            matches["education"].append(edu)
    
    return matches

def evaluate_match(matched_requirements, job_requirements):
    total_requirements = sum(len(v) for v in job_requirements.values())
    total_matches = sum(len(v) for v in matched_requirements.values())
    
    match_percentage = (total_matches / total_requirements) * 100
    return match_percentage

@app.route('/match_resumes')
def match_resumes():
    skills = request.args.getlist('skills')
    experience = request.args.getlist('experience')
    education = request.args.getlist('education')

    job_requirements = {
        "skills": skills,
        "experience": experience,
        "education": education
    }

    matches = []
    for file_name in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        
        # Check if the file is a PDF
        if file_name.endswith('.pdf'):
            resume_text = extract_text_from_pdf(file_path)
            matched_requirements = match_resume_with_job_requirements(resume_text, job_requirements)
            match_percentage = evaluate_match(matched_requirements, job_requirements)
            matches.append({
                "file_name": file_name,
                "match_percentage": match_percentage,
                "matched_skills": matched_requirements["skills"],
                "matched_experience": matched_requirements["experience"],
                "matched_education": matched_requirements["education"]
            })

    return render_template('match_resumes.html', matches=matches)



@app.route('/student_dashboard')
def student_dashboard():
    if 'email' in session:
        email = session['email']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT first_name FROM signup WHERE email = %s", (email,))
            student = cursor.fetchone()
            cursor.close()
            
            if not student:
                return "Student not found!"
            
            student_name = student[0]
            return render_template('student_dashboard.html', student_name=student_name)
        
        return "Database connection failed"
    else:
        return redirect(url_for('login'))

@app.route('/view_profile')
def view_profile():
    if 'email' in session:
        email = session['email']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM student_profile WHERE email_id = %s", (email,))
            student = cursor.fetchone()
            cursor.close()
            
            if not student:
                return "Student not found!"

            student_profile = {
                'STUDENT_USN': student[0],
                'FIRST_NAME': student[1],
                'LAST_NAME': student[2],
                'DOB': student[3],
                'email': student[4],
                'puc_marks': student[6],
                'sslc_marks': student[5],
                'cgpa': student[7],
                'skills': student[8],
                'achievements': student[9],
                
            }

            return render_template('view_profile.html', student=student_profile)
        
        return "Database connection failed"
    else:
        return redirect(url_for('login'))

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'email' in session:
        email = session['email']
        
        if request.method == 'POST':
            # Handle profile update logic here
            # Extract form data and update the database
            student_name = request.form['student_name']
            username = request.form['username']
            # Add other form fields as needed
            
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor()
                update_query = """
                UPDATE student_profile 
                SET  STUDENT_USN=%s, FIRST_NAME=%s, LAST_NAME=%s, DATE_OF_BIRTH=%s, EMAIL_ID=%s, SSLC_MARKS=%s, 
            PUC_MARKS=%s, BE_CGPA=%s, SKILLS=%s, ACHIEVEMENTS=%s, JOB_TYPE=%s, RESUME=%s, PHOTO=%s, GENDER=%s, PHONE_NUMBER=%s, BRANCH=%s
                """
                cursor.execute(update_query, (student_name, username, email))
                connection.commit()
                cursor.close()
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('student_dashboard'))
        
        # Fetch current profile data to pre-fill the form
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM student_profile WHERE email_id = %s", (email,))
            student = cursor.fetchone()
            cursor.close()
            
            if not student:
                return "Student not found!"

            student_profile = {
                'student_name': student[0],
                'username': student[1],
                'email': student[2],
                'class_name': student[3],
                'sslc_marks': student[4],
                'puc_marks': student[5],
                'address': student[6],
                'country': student[7],
                'state': student[8],
                'board': student[9],
                'academic_performance': student[10],
                'photo': student[11]
            }

            return render_template('student_registeration.html', student=student_profile)
        
        return "Database connection failed"
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
#for this code for login after he didnt successfully login then it show errorrs change this code