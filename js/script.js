// Case Study Modal Functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing modals...');
    
    // Get all case study buttons
    const caseStudyButtons = document.querySelectorAll('.btn-case-study');
    console.log('Found case study buttons:', caseStudyButtons.length);
    
    // Get all modals
    const modals = document.querySelectorAll('.modal');
    console.log('Found modals:', modals.length);
    
    // Get all close buttons
    const closeButtons = document.querySelectorAll('.modal-close');
    console.log('Found close buttons:', closeButtons.length);
    
    // Open modal function
    function openModal(modalId) {
        console.log('Opening modal:', modalId);
        const modal = document.getElementById(modalId);
        if (modal) {
            // Close all other modals first
            modals.forEach(m => {
                if (m !== modal) {
                    m.style.display = 'none';
                }
            });
            
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
            console.log('Modal opened successfully');
        } else {
            console.error('Modal not found:', modalId);
        }
    }
    
    // Close modal function
    function closeModal(modal) {
        console.log('Closing modal');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Restore scrolling
    }
    
    // Add click event listeners to case study buttons
    caseStudyButtons.forEach((button, index) => {
        console.log(`Adding listener to button ${index}:`, button);
        button.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Button clicked:', this);
            const agentType = this.getAttribute('data-agent');
            console.log('Agent type:', agentType);
            const modalId = `modal-${agentType}`;
            console.log('Modal ID:', modalId);
            openModal(modalId);
        });
    });
    
    // Add click event listeners to close buttons
    closeButtons.forEach((button, index) => {
        console.log(`Adding close listener to button ${index}:`, button);
        button.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Close button clicked');
            const modal = this.closest('.modal');
            if (modal) {
                closeModal(modal);
            }
        });
    });
    
    // Close modal when clicking outside of it
    modals.forEach((modal, index) => {
        console.log(`Adding outside click listener to modal ${index}:`, modal);
        modal.addEventListener('click', function(event) {
            if (event.target === this) {
                console.log('Clicked outside modal, closing');
                closeModal(this);
            }
        });
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            console.log('Escape key pressed');
            modals.forEach(modal => {
                if (modal.style.display === 'block') {
                    closeModal(modal);
                }
            });
        }
    });
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add animation to metric cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe metric cards
    const metricCards = document.querySelectorAll('.metric-card');
    metricCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
    
    console.log('Modal initialization complete');
    
    // Валидация всех контактных форм
    const contactForms = document.querySelectorAll('.contact-form, .detailed-form');
    contactForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateContactForm(this)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Валидация формы отзывов
    function validateTestimonialForm() {
        const name = document.getElementById('clientName').value.trim();
        const company = document.getElementById('companyName').value.trim();
        const email = document.getElementById('email').value.trim();
        const testimonial = document.getElementById('testimonialText').value.trim();
        const rating = document.querySelector('input[name="rating"]:checked');
        
        if (!name || name.length < 2) {
            alert('Пожалуйста, введите ваше имя (минимум 2 символа)');
            return false;
        }
        
        if (!company || company.length < 2) {
            alert('Пожалуйста, введите название компании (минимум 2 символа)');
            return false;
        }
        
        if (!email || !isValidEmail(email)) {
            alert('Пожалуйста, введите корректный email адрес');
            return false;
        }
        
        if (!testimonial || testimonial.length < 10) {
            alert('Пожалуйста, напишите отзыв (минимум 10 символов)');
            return false;
        }
        
        if (!rating) {
            alert('Пожалуйста, поставьте оценку');
            return false;
        }
        
        return true;
    }
    
    // Валидация email
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    // Валидация контактных форм
    function validateContactForm(form) {
        const name = form.querySelector('input[name="name"]')?.value.trim();
        const email = form.querySelector('input[name="email"]')?.value.trim();
        const message = form.querySelector('textarea[name="message"]')?.value.trim();
        
        if (!name || name.length < 2) {
            alert('Пожалуйста, введите ваше имя (минимум 2 символа)');
            return false;
        }
        
        if (!email || !isValidEmail(email)) {
            alert('Пожалуйста, введите корректный email адрес');
            return false;
        }
        
        if (!message || message.length < 10) {
            alert('Пожалуйста, напишите сообщение (минимум 10 символов)');
            return false;
        }
        
        return true;
    }

    // Testimonial form handling
    const testimonialForm = document.getElementById('testimonialForm');
    
    if (testimonialForm) {
        testimonialForm.addEventListener('submit', function(e) {
            // Базовая валидация перед отправкой
            if (!validateTestimonialForm()) {
                e.preventDefault();
                return false;
            }
            // Убираем preventDefault чтобы форма отправлялась через Formspree
            // e.preventDefault();
            
            // Get form data
            const formData = new FormData(testimonialForm);
            const testimonialData = {
                clientName: formData.get('clientName'),
                companyName: formData.get('companyName'),
                jobTitle: formData.get('jobTitle'),
                agentType: formData.get('agentType'),
                testimonialText: formData.get('testimonialText'),
                rating: formData.get('rating'),
                email: formData.get('email')
            };
            
            // Validate required fields
            if (!testimonialData.clientName || !testimonialData.companyName || 
                !testimonialData.jobTitle || !testimonialData.agentType || 
                !testimonialData.testimonialText || !testimonialData.rating || 
                !testimonialData.email) {
                alert('Please fill in all required fields.');
                return;
            }
            
            // Show success message
            alert('Thank you for your testimonial! We will review it and may contact you for verification before publishing.');
            
            // Add testimonial to the published section (for demo purposes)
            addTestimonialToPage(testimonialData);
            
            // Save to localStorage for persistence
            saveTestimonialToStorage(testimonialData);
            
            // Reset form
            testimonialForm.reset();
            
            // In a real implementation, you would send this data to your server
            console.log('Testimonial submitted:', testimonialData);
        });
    }
});

// Carousel state
let currentSlide = 0;
let testimonials = [];
let totalSlides = 0;

// Function to create testimonial card HTML
function createTestimonialCard(testimonialData) {
    // Generate stars based on rating
    const stars = '⭐'.repeat(parseInt(testimonialData.rating));
    
    return `
        <div class="testimonial-card">
            <div class="testimonial-content">
                <p>"${testimonialData.testimonialText}"</p>
            </div>
            <div class="testimonial-author">
                <div class="author-info">
                    <h4>${testimonialData.clientName}</h4>
                    <span>${testimonialData.jobTitle}, ${testimonialData.companyName}</span>
                </div>
                <div class="rating">${stars}</div>
            </div>
        </div>
    `;
}

// Function to update carousel
function updateCarousel() {
    const track = document.getElementById('testimonialsTrack');
    const dotsContainer = document.getElementById('carouselDots');
    
    if (!track || !dotsContainer) return;
    
    // Clear existing content
    track.innerHTML = '';
    dotsContainer.innerHTML = '';
    
    if (testimonials.length === 0) {
        // Show default testimonials if no user testimonials
        const defaultTestimonials = [
            {
                clientName: 'Sarah Chen',
                jobTitle: 'CEO',
                companyName: 'TechGear Store',
                testimonialText: 'The Product Management Agent saved us 4 hours daily. We went from manually updating 200+ products to fully automated price monitoring. ROI was 400% in the first month!',
                rating: 5
            },
            {
                clientName: 'Mike Rodriguez',
                jobTitle: 'Founder',
                companyName: 'FashionForward',
                testimonialText: 'Our Analytics Agent replaced a $800/month tool with custom reporting. Now we get better insights for $200/month support. The Python-based solution is incredibly flexible.',
                rating: 5
            },
            {
                clientName: 'Emma Thompson',
                jobTitle: 'Operations Manager',
                companyName: 'HomeDecor Plus',
                testimonialText: 'Customer support was overwhelming us with 50+ emails daily. The AI agent handles 80% of inquiries automatically, and our response time improved from 24h to 2 minutes.',
                rating: 5
            }
        ];
        
        testimonials = defaultTestimonials;
    }
    
    totalSlides = testimonials.length;
    
    // Reset to first slide
    currentSlide = 0;
    
    console.log('Carousel initialized:', { totalSlides, currentSlide, testimonials: testimonials.length });
    
    // Add testimonial cards to track
    testimonials.forEach((testimonial, index) => {
        const card = document.createElement('div');
        card.innerHTML = createTestimonialCard(testimonial);
        track.appendChild(card.firstElementChild);
    });
    
    // Create dots
    for (let i = 0; i < totalSlides; i++) {
        const dot = document.createElement('div');
        dot.className = `carousel-dot ${i === currentSlide ? 'active' : ''}`;
        dot.addEventListener('click', () => goToSlide(i));
        dotsContainer.appendChild(dot);
    }
    
    // Update carousel position
    updateCarouselPosition();
}

// Function to update carousel position
function updateCarouselPosition() {
    const track = document.getElementById('testimonialsTrack');
    if (!track) return;
    
    // Calculate the width of one card including gap
    const container = document.querySelector('.carousel-container');
    const containerWidth = container ? container.offsetWidth : 800;
    
    // Determine how many cards to show based on screen size
    let cardsToShow = 1;
    let cardWidth = 350;
    let gap = 24; // 1.5rem gap
    
    if (window.innerWidth >= 1920) {
        cardsToShow = 3;
        cardWidth = Math.min(400, (containerWidth - 100) / 3); // 3 cards with gaps
        gap = 40; // 2.5rem gap
    } else if (window.innerWidth >= 1440) {
        cardsToShow = 2;
        cardWidth = Math.min(380, (containerWidth - 60) / 2); // 2 cards with gap
        gap = 32; // 2rem gap
    } else if (window.innerWidth >= 1024) {
        cardsToShow = 2;
        cardWidth = Math.min(350, (containerWidth - 40) / 2); // 2 cards with gap
        gap = 24; // 1.5rem gap
    } else {
        cardWidth = Math.min(350, containerWidth - 40); // 1 card
        gap = 24; // 1.5rem gap
    }
    
    // Calculate transform to center the current slide
    const slideWidth = cardWidth + gap;
    
    // For single card view, center it properly
    if (cardsToShow === 1) {
        const centerOffset = (containerWidth - cardWidth) / 2;
        const translateX = -(currentSlide * slideWidth) + centerOffset;
        track.style.transform = `translateX(${translateX}px)`;
        console.log('Single card positioning:', { currentSlide, cardWidth, containerWidth, centerOffset, translateX });
    } else {
        // For multiple cards, center the group
        const totalCardsWidth = cardsToShow * cardWidth + (cardsToShow - 1) * gap;
        const centerOffset = (containerWidth - totalCardsWidth) / 2;
        const translateX = -(currentSlide * slideWidth) + centerOffset;
        track.style.transform = `translateX(${translateX}px)`;
        console.log('Multiple cards positioning:', { currentSlide, cardsToShow, cardWidth, containerWidth, centerOffset, translateX });
    }
    
    // Update dots - show fewer dots for better UX on large screens
    const dotsContainer = document.getElementById('carouselDots');
    if (dotsContainer) {
        const totalDots = Math.ceil(totalSlides / cardsToShow);
        dotsContainer.innerHTML = '';
        
        for (let i = 0; i < totalDots; i++) {
            const dot = document.createElement('div');
            dot.className = `carousel-dot ${i === Math.floor(currentSlide / cardsToShow) ? 'active' : ''}`;
            dot.addEventListener('click', () => goToSlide(i * cardsToShow));
            dotsContainer.appendChild(dot);
        }
    }
    
    // Update button states (no disabling for looping carousel)
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    // Remove disabled state for looping carousel
    if (prevBtn) prevBtn.disabled = false;
    if (nextBtn) nextBtn.disabled = false;
}

// Function to go to specific slide
function goToSlide(slideIndex) {
    if (slideIndex >= 0 && slideIndex < totalSlides) {
        currentSlide = slideIndex;
        updateCarouselPosition();
    }
}

// Function to go to next slide
function nextSlide() {
    const container = document.querySelector('.carousel-container');
    const containerWidth = container ? container.offsetWidth : 800;
    
    // Determine how many cards to show based on screen size
    let cardsToShow = 1;
    if (window.innerWidth >= 1920) {
        cardsToShow = 3;
    } else if (window.innerWidth >= 1440) {
        cardsToShow = 2;
    } else if (window.innerWidth >= 1024) {
        cardsToShow = 2;
    }
    
    if (currentSlide < totalSlides - cardsToShow) {
        currentSlide += cardsToShow;
    } else {
        // Loop back to first slide
        currentSlide = 0;
    }
    updateCarouselPosition();
}

// Function to go to previous slide
function prevSlide() {
    const container = document.querySelector('.carousel-container');
    const containerWidth = container ? container.offsetWidth : 800;
    
    // Determine how many cards to show based on screen size
    let cardsToShow = 1;
    if (window.innerWidth >= 1920) {
        cardsToShow = 3;
    } else if (window.innerWidth >= 1440) {
        cardsToShow = 2;
    } else if (window.innerWidth >= 1024) {
        cardsToShow = 2;
    }
    
    if (currentSlide >= cardsToShow) {
        currentSlide -= cardsToShow;
    } else {
        // Loop to last slide
        currentSlide = Math.max(0, totalSlides - cardsToShow);
    }
    updateCarouselPosition();
}

// Function to add testimonial to the page
function addTestimonialToPage(testimonialData) {
    // Add to beginning of testimonials array
    testimonials.unshift(testimonialData);
    
    // Update carousel
    updateCarousel();
    
    // Go to first slide to show new testimonial
    currentSlide = 0;
    updateCarouselPosition();
}

// Function to save testimonial to localStorage
function saveTestimonialToStorage(testimonialData) {
    try {
        // Get existing testimonials
        const existingTestimonials = JSON.parse(localStorage.getItem('testimonials') || '[]');
        
        // Add new testimonial with timestamp
        const newTestimonial = {
            ...testimonialData,
            id: Date.now(),
            timestamp: new Date().toISOString(),
            status: 'pending' // pending, approved, rejected
        };
        
        // Add to beginning of array
        existingTestimonials.unshift(newTestimonial);
        
        // Keep only last 50 testimonials to avoid storage bloat
        if (existingTestimonials.length > 50) {
            existingTestimonials.splice(50);
        }
        
        // Save back to localStorage
        localStorage.setItem('testimonials', JSON.stringify(existingTestimonials));
        
        console.log('Testimonial saved to localStorage:', newTestimonial);
    } catch (error) {
        console.error('Error saving testimonial to localStorage:', error);
    }
}

// Function to load testimonials from localStorage on page load
function loadTestimonialsFromStorage() {
    try {
        const savedTestimonials = JSON.parse(localStorage.getItem('testimonials') || '[]');
        
        // Filter only approved testimonials (for demo, we'll show all)
        const approvedTestimonials = savedTestimonials.filter(t => t.status === 'approved' || t.status === 'pending');
        
        // Set testimonials array
        testimonials = approvedTestimonials;
        
        // Update carousel
        updateCarousel();
        
        console.log('Loaded testimonials from localStorage:', approvedTestimonials.length);
    } catch (error) {
        console.error('Error loading testimonials from localStorage:', error);
    }
}

// Initialize carousel when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Load existing testimonials after a short delay to ensure DOM is ready
    setTimeout(() => {
        loadTestimonialsFromStorage();
        
        // Add event listeners for carousel controls
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', prevSlide);
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', nextSlide);
        }
        
        // Auto-advance carousel every 5 seconds
        setInterval(() => {
            if (totalSlides > 1) {
                nextSlide();
            }
        }, 5000);
        
        // Handle window resize
        window.addEventListener('resize', () => {
            updateCarouselPosition();
        });
    }, 100);
});