from webapp import create_app, db
from webapp.models import Admin
from werkzeug.security import generate_password_hash

app = create_app()

def create_admin(email, name, plain_password, university_id, contact):
    with app.app_context():
        existing_admin = Admin.query.filter_by(Admin_Email=email).first()
        
        if existing_admin:
            print(f"Admin with email {email} already exists.")
            return
        
        hashed_password = generate_password_hash(plain_password, method='pbkdf2:sha256')

        # Generate a unique Admin_ID
        admin_id = Admin.generate_admin_id()

        admin = Admin(
            Admin_ID=admin_id,  # Use the generated ID
            Admin_Email=email,
            Admin_Name=name,
            Admin_Password=hashed_password,
            University_ID=university_id,
            Admin_Contact=contact
        )

        db.session.add(admin)
        db.session.commit()

        print(f"Admin account for {name} created successfully.")