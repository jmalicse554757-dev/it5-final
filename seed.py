import sys
print("Starting seed...", flush=True)
sys.stdout.flush()

from app import create_app, db, bcrypt
from app.models.user import User
from app.models.strand import Strand
from app.models.section import Section
from app.models.student import Student
from app.models.enrollment import Enrollment
from datetime import datetime, date

print("Imports done...", flush=True)

app = create_app()

with app.app_context():
    print("Dropping tables...", flush=True)
    db.drop_all()
    db.create_all()
    print("Tables created!", flush=True)

    # USERS
    users = [
        User(
            username='admin',
            password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            role='admin',
            full_name='Administrator',
            is_active=True
        ),
        User(
            username='staff',
            password_hash=bcrypt.generate_password_hash('staff123').decode('utf-8'),
            role='staff',
            full_name='Staff User',
            is_active=True
        ),
        User(
            username='student',
            password_hash=bcrypt.generate_password_hash('student123').decode('utf-8'),
            role='student',
            full_name='Sample Student',
            is_active=True
        ),
    ]
    db.session.add_all(users)
    db.session.commit()
    print("Users seeded!", flush=True)

    # STRANDS
    strands = [
        Strand(code='STEM', full_name='Science, Technology, Engineering & Math'),
        Strand(code='ABM', full_name='Accountancy, Business & Management'),
        Strand(code='HUMSS', full_name='Humanities & Social Sciences'),
        Strand(code='TVL', full_name='Technical-Vocational-Livelihood'),
        Strand(code='GAS', full_name='General Academic Strand'),
    ]
    db.session.add_all(strands)
    db.session.commit()
    print("Strands seeded!", flush=True)

    stem = Strand.query.filter_by(code='STEM').first()
    abm = Strand.query.filter_by(code='ABM').first()
    humss = Strand.query.filter_by(code='HUMSS').first()
    tvl = Strand.query.filter_by(code='TVL').first()
    gas = Strand.query.filter_by(code='GAS').first()

    # SECTIONS
    sections = [
        Section(name='Einstein', strand_id=stem.id, grade_level='11', max_capacity=40),
        Section(name='Newton', strand_id=stem.id, grade_level='11', max_capacity=40),
        Section(name='Curie', strand_id=stem.id, grade_level='12', max_capacity=40),
        Section(name='Bonifacio', strand_id=abm.id, grade_level='11', max_capacity=40),
        Section(name='Rizal', strand_id=abm.id, grade_level='11', max_capacity=40),
        Section(name='Mabini', strand_id=abm.id, grade_level='12', max_capacity=40),
        Section(name='Dagohoy', strand_id=humss.id, grade_level='11', max_capacity=40),
        Section(name='Silang', strand_id=humss.id, grade_level='12', max_capacity=40),
        Section(name='Lapu-Lapu', strand_id=tvl.id, grade_level='11', max_capacity=40),
        Section(name='Del Pilar', strand_id=tvl.id, grade_level='12', max_capacity=40),
        Section(name='Luna', strand_id=gas.id, grade_level='11', max_capacity=40),
        Section(name='Burgos', strand_id=gas.id, grade_level='12', max_capacity=40),
    ]
    db.session.add_all(sections)
    db.session.commit()
    print("Sections seeded!", flush=True)

    einstein = Section.query.filter_by(name='Einstein').first()
    bonifacio = Section.query.filter_by(name='Bonifacio').first()
    dagohoy = Section.query.filter_by(name='Dagohoy').first()
    lapu = Section.query.filter_by(name='Lapu-Lapu').first()
    luna = Section.query.filter_by(name='Luna').first()

    # STUDENTS
    students = [
        Student(
            lrn='123456789012',
            last_name='Dela Cruz',
            first_name='Juan',
            middle_name='Santos',
            date_of_birth=date(2008, 3, 15),
            sex='Male',
            contact_number='09123456789',
            email='juan@email.com',
            address='123 Rizal St., Davao City',
            guardian_name='Maria Dela Cruz',
            guardian_relationship='Parent',
            guardian_contact='09987654321',
            guardian_occupation='Teacher'
        ),
        Student(
            lrn='123456789013',
            last_name='Andres',
            first_name='Maria',
            middle_name='Reyes',
            date_of_birth=date(2008, 6, 20),
            sex='Female',
            contact_number='09234567890',
            email='maria@email.com',
            address='456 Mabini St., Davao City',
            guardian_name='Jose Andres',
            guardian_relationship='Parent',
            guardian_contact='09876543210',
            guardian_occupation='Engineer'
        ),
        Student(
            lrn='123456789014',
            last_name='Reyes',
            first_name='Karl',
            middle_name='Mendoza',
            date_of_birth=date(2007, 9, 10),
            sex='Male',
            contact_number='09345678901',
            email='karl@email.com',
            address='789 Bonifacio St., Davao City',
            guardian_name='Ana Reyes',
            guardian_relationship='Parent',
            guardian_contact='09765432109',
            guardian_occupation='Nurse'
        ),
        Student(
            lrn='123456789015',
            last_name='Lim',
            first_name='Sofia',
            middle_name='Garcia',
            date_of_birth=date(2008, 1, 5),
            sex='Female',
            contact_number='09456789012',
            email='sofia@email.com',
            address='321 Luna St., Davao City',
            guardian_name='Robert Lim',
            guardian_relationship='Parent',
            guardian_contact='09654321098',
            guardian_occupation='Doctor'
        ),
        Student(
            lrn='123456789016',
            last_name='Torres',
            first_name='Ben',
            middle_name='Aquino',
            date_of_birth=date(2007, 12, 25),
            sex='Male',
            contact_number='09567890123',
            email='ben@email.com',
            address='654 Burgos St., Davao City',
            guardian_name='Lily Torres',
            guardian_relationship='Parent',
            guardian_contact='09543210987',
            guardian_occupation='Businessman'
        ),
    ]
    db.session.add_all(students)
    db.session.commit()
    print("Students seeded!", flush=True)

    juan = Student.query.filter_by(lrn='123456789012').first()
    maria = Student.query.filter_by(lrn='123456789013').first()
    karl = Student.query.filter_by(lrn='123456789014').first()
    sofia = Student.query.filter_by(lrn='123456789015').first()
    ben = Student.query.filter_by(lrn='123456789016').first()

    # ENROLLMENTS
    enrollments = [
        Enrollment(
            student_id=juan.id,
            strand_id=stem.id,
            section_id=einstein.id,
            status='enrolled',
            date_enrolled=datetime.utcnow(),
            school_year='2024-2025'
        ),
        Enrollment(
            student_id=maria.id,
            strand_id=humss.id,
            section_id=dagohoy.id,
            status='pending',
            school_year='2024-2025'
        ),
        Enrollment(
            student_id=karl.id,
            strand_id=abm.id,
            section_id=bonifacio.id,
            status='enrolled',
            date_enrolled=datetime.utcnow(),
            school_year='2024-2025'
        ),
        Enrollment(
            student_id=sofia.id,
            strand_id=tvl.id,
            section_id=lapu.id,
            status='rejected',
            school_year='2024-2025'
        ),
        Enrollment(
            student_id=ben.id,
            strand_id=gas.id,
            section_id=luna.id,
            status='enrolled',
            date_enrolled=datetime.utcnow(),
            school_year='2024-2025'
        ),
    ]
    db.session.add_all(enrollments)
    db.session.commit()
    print("Enrollments seeded!", flush=True)

    print("", flush=True)
    print("Database seeded successfully!", flush=True)
    print("Login credentials:", flush=True)
    print("  Admin   -> username: admin   | password: admin123", flush=True)
    print("  Staff   -> username: staff   | password: staff123", flush=True)
    print("  Student -> username: student | password: student123", flush=True)