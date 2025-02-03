from webapp import create_app, db
from webapp.models import Courier
from werkzeug.security import generate_password_hash

# Create the Flask app and app context
app = create_app()

# Create the courier account function
def create_courier(courier_id, name, email, plain_password, contact):
    with app.app_context():  # Ensure the app context is active
        
        # Check if a courier with the given ID or email already exists
        existing_courier = Courier.query.filter((Courier.Courier_ID == courier_id) | (Courier.Courier_Email == email)).first()
        
        if existing_courier:
            print(f"Courier with ID {courier_id} or email {email} already exists.")
            return  # Early exit if the courier already exists
        
        # Hash the password
        hashed_password = generate_password_hash(plain_password, method='pbkdf2:sha256')

        # Create the Courier object
        courier = Courier(
            Courier_ID=courier_id,
            Courier_Name=name,
            Courier_Email=email,
            Courier_Password=hashed_password,
            Courier_Contact=contact
        )

        # Add the courier to the session and commit
        db.session.add(courier)
        db.session.commit()

        print(f"Courier account for {name} created successfully.")
