from webapp import create_app, db
from webapp.models import StudentStaff, University
from werkzeug.security import generate_password_hash

# Create the Flask app and app context
app = create_app()

# Create the Student/Staff account function
def create_student_staff(email, name, plain_password, contact, user_type, university_id):
    with app.app_context():  # Ensure the app context is active
        
        # Check if a Student/Staff with the given email already exists
        existing_user = StudentStaff.query.filter_by(User_Email=email).first()
        
        if existing_user:
            print(f"Student/Staff with email {email} already exists.")
            return  # Early exit if the user already exists

        # Check if the University exists
        university = University.query.get(university_id)
        if not university:
            print(f"University with ID {university_id} does not exist.")
            return  # Early exit if the university does not exist

        # Hash the password
        hashed_password = generate_password_hash(plain_password, method='pbkdf2:sha256')

        # Generate a unique User ID
        user_id = StudentStaff.generate_user_id(user_type)

        # Create the StudentStaff object
        user = StudentStaff(
            User_ID=user_id,
            University_ID=university_id,
            User_Type=user_type,
            User_Name=name,
            User_Email=email,
            User_Password=hashed_password,
            User_Contact=contact,
            Login_Status="Inactive"  # Default status
        )

        # Add the user to the session and commit
        db.session.add(user)
        db.session.commit()

        print(f"Student/Staff account for {name} created successfully with User ID: {user_id}.")