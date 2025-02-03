from webapp import create_app
from webapp.create_admin import create_admin
from webapp.create_manager import create_parcel_manager
from webapp.create_studentStaff import create_student_staff
from webapp.create_uni import create_university
import random

app = create_app()

students = [
    {"name": "Ali bin Aman", "email": "ali.ahmad@mmu.edu.my", "contact": "+6012-3456789", "university_id": "UNI010", "password": "password123"},
    {"name": "Siti binti Mohd", "email": "siti.mohd@mmu.edu.my", "contact": "+6013-4567890", "university_id": "UNI010", "password": "password123"},
    {"name": "Tan Wei Ling", "email": "tan.weiling@mmu.edu.my", "contact": "+6014-5678901", "university_id": "UNI010", "password": "password123"},
    {"name": "Rajesh a/l Kumar", "email": "rajesh.kumar@mmu.edu.my", "contact": "+6015-6789012", "university_id": "UNI010", "password": "password123"},
    {"name": "Nurul Huda binti Ismail", "email": "nurul.huda@mmu.edu.my", "contact": "+6016-7890123", "university_id": "UNI010", "password": "password123"},
    {"name": "Lim Chen Yee", "email": "lim.chenyee@mmu.edu.my", "contact": "+6017-8901234", "university_id": "UNI010", "password": "password123"},
    {"name": "Muhammad bin Ali", "email": "muhammad.ali@mmu.edu.my", "contact": "+6018-9012345", "university_id": "UNI010", "password": "password123"},
    {"name": "Chong Mei Ling", "email": "chong.meiling@mmu.edu.my", "contact": "+6019-0123456", "university_id": "UNI010", "password": "password123"},
    {"name": "Ahmad bin Hassan", "email": "ahmad.hassan@mmu.edu.my", "contact": "+6011-1234567", "university_id": "UNI010", "password": "password123"},
    {"name": "Lee Wei Jian", "email": "lee.weijian@mmu.edu.my", "contact": "+6010-2345678", "university_id": "UNI010", "password": "password123"},
    {"name": "Nurul Syafiqah binti Azman", "email": "nurul.syafiqah@mmu.edu.my", "contact": "+6012-3456789", "university_id": "UNI010", "password": "password123"},
    {"name": "Kumar a/l Raj", "email": "kumar.raj@mmu.edu.my", "contact": "+6013-4567890", "university_id": "UNI010", "password": "password123"}
]

# Create student accounts for each student
for student in students:
    create_student_staff(
        email=student["email"],
        name=student["name"],
        plain_password=student["password"],
        contact=student["contact"],
        user_type="Student",  # All users are students
        university_id=student["university_id"]
    )

if __name__ == '__main__':
    app.run()
    