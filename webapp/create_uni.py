from webapp import create_app, db
from webapp.models import University

app = create_app()

def create_university(university_id, university_name, contact, location):
    with app.app_context():
        # Check if the university already exists
        existing_uni = University.query.filter_by(University_ID=university_id).first()
        
        if existing_uni:
            print(f"University with ID {university_id} already exists.")
            return
        
        # Create the new university record
        university = University(
            University_ID=university_id,
            University_Name=university_name,
            University_Contact=contact,
            University_Location=location
        )

        db.session.add(university)
        db.session.commit()

        print(f"University {university_name} created successfully.")
