// ========================================
// DropoutWatch - Interactive JavaScript
// ========================================

// Navbar scroll effect
const navbar = document.getElementById('navbar');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll > 100) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }

    lastScroll = currentScroll;
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));

        if (target) {
            const offsetTop = target.offsetTop - 80;
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    });
});

// Mobile menu toggle
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navLinks = document.querySelector('.nav-links');

mobileMenuBtn?.addEventListener('click', () => {
    navLinks.classList.toggle('active');
    mobileMenuBtn.textContent = navLinks.classList.contains('active') ? '✕' : '☰';
});

// Intersection Observer for scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all feature cards, stat cards, and step cards
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll(
        '.feature-card, .stat-card, .step-card, .tech-badge'
    );

    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// Contact form handling
const contactForm = document.getElementById('contactForm');

contactForm?.addEventListener('submit', (e) => {
    e.preventDefault();

    // Get form data
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        organization: document.getElementById('organization').value,
        role: document.getElementById('role').value,
        message: document.getElementById('message').value
    };

    // Simulate form submission
    console.log('Form submitted:', formData);

    // Show success message
    const submitBtn = contactForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = '✓ Request Sent!';
    submitBtn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';

    // Reset form
    setTimeout(() => {
        contactForm.reset();
        submitBtn.textContent = originalText;
        submitBtn.style.background = '';
    }, 3000);
});

// Dashboard demo interactivity
const dashboardPreview = document.querySelector('.dashboard-preview');

if (dashboardPreview) {
    // Add hover effect to show it's interactive
    dashboardPreview.style.cursor = 'pointer';

    dashboardPreview.addEventListener('click', () => {
        // Could open a modal or full-screen view
        console.log('Dashboard clicked - could open interactive demo');
    });
}

// Simulate real-time data updates (for demo purposes)
function simulateDataUpdate() {
    const statNumbers = document.querySelectorAll('.stat-number');

    statNumbers.forEach(stat => {
        if (!stat.textContent.includes('%') && !stat.textContent.includes('+')) {
            return;
        }

        // Add subtle pulse animation
        stat.style.animation = 'pulse 2s ease-in-out infinite';
    });
}

// Add pulse animation keyframe if not already in CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
`;
document.head.appendChild(style);

// Initialize data simulation
setTimeout(simulateDataUpdate, 1000);

// Parallax effect for hero section
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroImage = document.querySelector('.hero-image');

    if (heroImage && scrolled < window.innerHeight) {
        heroImage.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
});

// Add active state to navigation links based on scroll position
const sections = document.querySelectorAll('section[id]');
const navItems = document.querySelectorAll('.nav-links a');

window.addEventListener('scroll', () => {
    let current = '';

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;

        if (window.pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });

    navItems.forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('href') === `#${current}`) {
            item.classList.add('active');
        }
    });
});

// Add CSS for active nav link
const navStyle = document.createElement('style');
navStyle.textContent = `
    .nav-links a.active {
        color: var(--primary-light);
    }
    
    .nav-links a.active::after {
        width: 100%;
    }
    
    @media (max-width: 968px) {
        .nav-links.active {
            display: flex;
            flex-direction: column;
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: rgba(15, 23, 42, 0.98);
            backdrop-filter: blur(20px);
            padding: 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: var(--shadow-lg);
        }
    }
`;
document.head.appendChild(navStyle);

// Feature card hover effects with additional interactivity
document.querySelectorAll('.feature-card').forEach(card => {
    card.addEventListener('mouseenter', function () {
        this.style.transition = 'all 0.3s ease';
    });

    card.addEventListener('mouseleave', function () {
        this.style.transform = '';
    });
});

// Risk badge animation on hover
document.querySelectorAll('.risk-badge').forEach(badge => {
    badge.addEventListener('mouseenter', function () {
        this.style.transform = 'scale(1.1)';
        this.style.transition = 'transform 0.2s ease';
    });

    card.addEventListener('mouseleave', function () {
        this.style.transform = 'scale(1)';
    });
});

// Log page load
console.log('DropoutWatch initialized successfully');
console.log('Using AI and Data to Keep Students on Track');
