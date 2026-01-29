document.addEventListener('DOMContentLoaded', () => {
    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            // Handle Home button (scroll to top)
            if (href === '#' || href === '#top') {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
                return;
            }
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form submission handling
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Add your form submission logic here
            console.log('Form submitted');
        });
    }

    // Optional: Add animation on scroll
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe all sections
    document.querySelectorAll('section').forEach(section => {
        observer.observe(section);
    });

    // Add typing effect to hero section
    const heroText = document.querySelector('.hero-text h1');
    if (heroText) {
        const text = heroText.textContent;
        heroText.textContent = '';
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                heroText.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        };
        typeWriter();
    }

    // Add active state to navigation links
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.nav-links a');

    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            if (window.pageYOffset >= sectionTop - 60) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href').substring(1) === current) {
                link.classList.add('active');
            }
        });
    });

    // Dropdown navigation (Profile menu)
    const navDropdown = document.querySelector('.nav-dropdown');
    const navDropdownButton = document.querySelector('.nav-link-button');
    if (navDropdown && navDropdownButton) {
        navDropdownButton.addEventListener('click', (e) => {
            e.stopPropagation();
            navDropdown.classList.toggle('open');
        });

        document.addEventListener('click', () => {
            navDropdown.classList.remove('open');
        });
    }

    // Experience selector
    const experienceSelect = document.getElementById('experience-select');
    const experienceCards = document.querySelectorAll('.experience-card');
    if (experienceSelect && experienceCards.length) {
        const updateExperience = () => {
            const value = experienceSelect.value;
            experienceCards.forEach(card => {
                card.style.display = card.getAttribute('data-experience') === value ? 'block' : 'none';
            });
        };
        experienceSelect.addEventListener('change', updateExperience);
        updateExperience();
    }

    // Scroll to top functionality
    const scrollToTopButton = document.getElementById('scrollToTop');

    // Show button when user scrolls down 200px
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 200) {
            scrollToTopButton.classList.add('visible');
        } else {
            scrollToTopButton.classList.remove('visible');
        }
    });

    // Smooth scroll to top when button is clicked
    scrollToTopButton.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // Gallery modal (for competitions / extras)
    const galleryModal = document.getElementById('gallery-modal');
    if (galleryModal) {
        const overlay = galleryModal.querySelector('.gallery-overlay');
        const imgEl = galleryModal.querySelector('.gallery-current-image');
        const captionEl = galleryModal.querySelector('.gallery-caption');
        const closeBtn = galleryModal.querySelector('.gallery-close');
        const nextBtn = galleryModal.querySelector('.gallery-next');
        const prevBtn = galleryModal.querySelector('.gallery-prev');

        let galleryImages = [];
        let galleryIndex = 0;

        const showImage = (idx) => {
            if (!galleryImages || galleryImages.length === 0) return;
            galleryIndex = (idx + galleryImages.length) % galleryImages.length;
            imgEl.src = galleryImages[galleryIndex].src;
            imgEl.alt = galleryImages[galleryIndex].alt || '';
            captionEl.textContent = galleryImages[galleryIndex].alt || '';
        };

        const openGallery = (images, start = 0) => {
            galleryImages = images;
            showImage(start);
            galleryModal.style.display = 'flex';
            galleryModal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
        };

        const closeGallery = () => {
            galleryModal.style.display = 'none';
            galleryModal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
            imgEl.src = '';
            captionEl.textContent = '';
            galleryImages = [];
            galleryIndex = 0;
        };

        // Wire buttons on page
        document.querySelectorAll('.view-gallery').forEach(button => {
            button.addEventListener('click', (e) => {
                // find nearest card (competitions extra-card, project-info, or research-card)
                const card = button.closest('.extra-card') || button.closest('.project-info') || button.closest('.research-card');
                if (!card) return;
                // collect images: visible hero image and hidden gallery-images imgs
                const imgs = [];
                const mainImg = card.querySelector('.project-image img');
                if (mainImg && mainImg.src) imgs.push({ src: mainImg.src, alt: mainImg.alt || '' });
                const hidden = card.querySelectorAll('.gallery-images img');
                hidden.forEach(i => {
                    if (i.src) imgs.push({ src: i.src, alt: i.alt || '' });
                });
                if (imgs.length === 0) return;
                openGallery(imgs, 0);
            });
        });

        closeBtn.addEventListener('click', closeGallery);
        overlay.addEventListener('click', closeGallery);
        nextBtn.addEventListener('click', () => showImage(galleryIndex + 1));
        prevBtn.addEventListener('click', () => showImage(galleryIndex - 1));

        document.addEventListener('keydown', (e) => {
            if (galleryModal.style.display === 'none' || galleryModal.getAttribute('aria-hidden') === 'true') return;
            if (e.key === 'Escape') closeGallery();
            if (e.key === 'ArrowRight') showImage(galleryIndex + 1);
            if (e.key === 'ArrowLeft') showImage(galleryIndex - 1);
        });
    }
});
