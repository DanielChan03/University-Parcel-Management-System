// Sidebar functionality
const sidebar = document.querySelector('.sidebar');
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

// Parcel tracking button functionality
document.getElementById("track-btn").addEventListener("click", function () {
    const trackingNumber = document.getElementById("tracking-input").value;
    if (trackingNumber) {
        alert(`Tracking number ${trackingNumber} is being processed.`);
    } else {
        alert("Please enter a tracking number.");
    }
});

// Carousel functionality
const track = document.querySelector('.carousel-track');
const slides = Array.from(track.children);
const dotsNav = document.querySelector('.carousel-nav');
const dots = Array.from(dotsNav.children);

const slideWidth = slides[0].getBoundingClientRect().width;

// Arrange slides next to each other
slides.forEach((slide, index) => {
    slide.style.left = `${index * 100}%`;
});

// Function to move to a specific slide
const moveToSlide = (track, currentSlide, targetSlide) => {
    track.style.transform = `translateX(-${targetSlide.style.left})`;
    currentSlide.classList.remove('current-slide');
    targetSlide.classList.add('current-slide');
};

// Function to update the dots
const updateDots = (currentDot, targetDot) => {
    currentDot.classList.remove('current-dot');
    targetDot.classList.add('current-dot');
};

// Function to handle dot navigation
dotsNav.addEventListener('click', e => {
    const targetDot = e.target.closest('button'); // Get the clicked dot

    if (!targetDot) return;

    const currentSlide = track.querySelector('.current-slide');
    const currentDot = dotsNav.querySelector('.current-dot');
    const targetIndex = dots.findIndex(dot => dot === targetDot); // Get the index of the clicked dot
    const targetSlide = slides[targetIndex]; // Find the corresponding slide

    moveToSlide(track, currentSlide, targetSlide); // Move to the selected slide
    updateDots(currentDot, targetDot); // Update the active dot
});

// Auto-roll functionality
let slideIndex = 0;
setInterval(() => {
    const currentSlide = track.querySelector('.current-slide');
    const currentDot = dotsNav.querySelector('.current-dot');
    slideIndex = (slideIndex + 1) % slides.length; // Loop back to the first slide after the last
    const targetSlide = slides[slideIndex];
    const targetDot = dots[slideIndex];

    moveToSlide(track, currentSlide, targetSlide);
    updateDots(currentDot, targetDot);
}, 3000);
