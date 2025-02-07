// Function to toggle parcel details visibility
function toggleDetails(deliveryId) {
    const details = document.getElementById(deliveryId);
    const arrow = details.previousElementSibling.querySelector('.arrow');
    details.classList.toggle('open');
    arrow.classList.toggle('open');
  }
  
  // Function to search deliveries by date
  function searchByDate() {
    const searchDate = document.getElementById('searchDate').value;
    if (!searchDate) {
      alert('Please select a date to search.');
      return;
    }
  
    const deliveryGroups = document.querySelectorAll('.delivery-group');
    let found = false;
  
    deliveryGroups.forEach(group => {
      const deliveryDate = group.querySelector('h3').textContent.split(', ')[1];
      if (deliveryDate === searchDate) {
        group.style.display = 'block'; // Show matching group
        found = true;
      } else {
        group.style.display = 'none'; // Hide non-matching groups
      }
    });
  
    if (!found) {
      alert('No deliveries found for the selected date.');
    }
  }
  
  // Function to save the collected status for multiple parcels
  function saveCollectedStatus(deliveryId) {
    const checkboxes = document.querySelectorAll(`#${deliveryId} input[type="checkbox"]`);
    let collectedParcels = [];
  
    checkboxes.forEach(checkbox => {
      if (checkbox.checked) {
        collectedParcels.push(checkbox.id.split('-')[1]);
      }
    });
  
    if (collectedParcels.length > 0) {
      alert(`Parcels ${collectedParcels.join(', ')} marked as collected and saved.`);
      // Here you can add logic to save the status to a database or backend
    } else {
      alert('No parcels marked as collected.');
    }
  }
  
  // Function to view parcel managers
  function viewParcelManager() {
    alert('Viewing Parcel Managers...');
    // Here you can add logic to display parcel managers (e.g., open a modal or redirect to a new page)
  }