// AdminScript.js

const sidebar = document.querySelector('.admin-sidebar');
const toggleBtn = document.querySelector('.sidebar-toggle-btn');
const closeBtn = document.querySelector('.sidebar-close-btn');
const mainContent = document.querySelector('.main');

// Open sidebar
toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    mainContent.classList.toggle('shifted');
});

// Close sidebar
closeBtn.addEventListener('click', () => {
    sidebar.classList.remove('open');
    mainContent.classList.remove('shifted');
});

document.querySelectorAll('.flash-message').forEach(message => {
    message.addEventListener('animationend', () => {
        message.remove(); // Remove the flash message after the animation
    });
});
