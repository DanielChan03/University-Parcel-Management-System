from flask import Blueprint, render_template
from flask_login import current_user, login_required
from webapp.models import Delivery, Parcel
from sqlalchemy.orm import joinedload

view_manager_list_bp = Blueprint('view_manager_list', __name__)

#View Parcel Manager List
@view_manager_list_bp.route('/view-managers',methods =['GET'])
@login_required
def courierViewManagerList():

     # Get the currently logged-in courier's ID
    current_courier_id = current_user.get_id()  # Assuming `current_user` is the logged-in courier


    deliveries = Delivery.query.filter_by(Courier_ID=current_courier_id).all()
    delivery_ids = [delivery.Delivery_ID for delivery in deliveries]

    # Query the Parcel table and join with ParcelManager for Send and Receive Managers
    parcels = Parcel.query.options(
        joinedload(Parcel.send_manager),  # Eager load the send manager
        joinedload(Parcel.receive_manager)  # Eager load the receive manager
    ).filter(Parcel.Delivery_ID.in_(delivery_ids)).order_by(Parcel.Parcel_ID.asc()).all()

    # Prepare the data to pass to the template
    parcel_data = []
    for parcel in parcels:
        parcel_info = {
            'Parcel_ID': parcel.Parcel_ID,
            'Send_Manager_ID': parcel.Send_Manager_ID,
            'Send_Manager_Name': parcel.send_manager.Manager_Name if parcel.send_manager else 'N/A',
            'Send_Manager_Email': parcel.send_manager.Manager_Email if parcel.send_manager else 'N/A',
            'Send_Manager_Contact': parcel.send_manager.Manager_Contact if parcel.send_manager else 'N/A',
            'Send_Manager_Branch': parcel.send_manager.Manager_Work_Branch if parcel.send_manager else 'N/A',
            'Receive_Manager_ID': parcel.Receive_Manager_ID,
            'Receive_Manager_Name': parcel.receive_manager.Manager_Name if parcel.receive_manager else 'N/A',
            'Receive_Manager_Email': parcel.receive_manager.Manager_Email if parcel.receive_manager else 'N/A',
            'Receive_Manager_Contact': parcel.receive_manager.Manager_Contact if parcel.receive_manager else 'N/A',
            'Receive_Manager_Branch': parcel.receive_manager.Manager_Work_Branch if parcel.receive_manager else 'N/A',
        }
        parcel_data.append(parcel_info)
    
    return render_template('Courier/CourierViewManagerList.html',parcels = parcel_data)
