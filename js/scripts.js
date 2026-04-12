document.addEventListener('DOMContentLoaded', () => {
    const root = document.documentElement;
    const themeToggleButtons = document.querySelectorAll('.theme-toggle');
    const nav = document.querySelector('.navbar');
    const navToggle = document.querySelector('.nav-toggle');
    const navPanel = document.querySelector('.nav-panel');
    const scrollToTopButton = document.getElementById('scrollToTop');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

    const applyTheme = (theme) => {
        root.dataset.theme = theme;
        window.localStorage.setItem('theme', theme);
        themeToggleButtons.forEach((button) => {
            const icon = button.querySelector('i');
            const label = button.querySelector('.sr-only, .theme-toggle-text');
            const nextTheme = theme === 'dark' ? 'light' : 'dark';

            button.setAttribute('aria-label', `Switch to ${nextTheme} mode`);
            button.setAttribute('title', `Switch to ${nextTheme} mode`);

            if (icon) {
                icon.classList.toggle('fa-moon', theme === 'dark');
                icon.classList.toggle('fa-sun', theme !== 'dark');
            }

            if (label) {
                label.textContent = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
            }
        });
    };

    const savedTheme = window.localStorage.getItem('theme');
    applyTheme(savedTheme || (prefersDark.matches ? 'dark' : 'light'));

    themeToggleButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const nextTheme = root.dataset.theme === 'dark' ? 'light' : 'dark';
            applyTheme(nextTheme);
        });
    });

    if (!savedTheme) {
        prefersDark.addEventListener('change', (event) => {
            applyTheme(event.matches ? 'dark' : 'light');
        });
    }

    const closeNavMenu = () => {
        if (!navPanel || !navToggle) {
            return;
        }

        navPanel.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
    };

    if (navToggle && navPanel) {
        navToggle.addEventListener('click', () => {
            const isOpen = navPanel.classList.toggle('open');
            navToggle.setAttribute('aria-expanded', String(isOpen));
        });

        navPanel.querySelectorAll('a').forEach((link) => {
            link.addEventListener('click', closeNavMenu);
        });
    }

    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener('click', (event) => {
            const href = anchor.getAttribute('href');
            if (!href || href === '#') {
                return;
            }

            const target = document.querySelector(href);
            if (!target) {
                return;
            }

            event.preventDefault();
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
            closeNavMenu();
        });
    });

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, {
        threshold: 0.14
    });

    document.querySelectorAll('section').forEach((section) => observer.observe(section));

    const homeSections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-links a[href]');

    const updateActiveLinks = () => {
        const currentPath = window.location.pathname.replace(/index\.html$/, '');
        let currentSection = '';

        homeSections.forEach((section) => {
            const offset = section.offsetTop - 120;
            if (window.scrollY >= offset) {
                currentSection = section.id;
            }
        });

        navLinks.forEach((link) => {
            const href = link.getAttribute('href');
            const isHashLink = href.startsWith('#');
            const normalizedHref = new URL(href, window.location.href).pathname.replace(/index\.html$/, '');
            const matchesPath = !isHashLink && normalizedHref === currentPath;
            const matchesSection = isHashLink && href.slice(1) === currentSection;

            link.classList.toggle('active', matchesPath || matchesSection);
        });
    };

    const onScroll = () => {
        if (nav) {
            nav.classList.toggle('nav-scrolled', window.scrollY > 24);
        }

        if (scrollToTopButton) {
            scrollToTopButton.classList.toggle('visible', window.scrollY > 260);
        }

        updateActiveLinks();
    };

    window.addEventListener('scroll', onScroll);
    updateActiveLinks();
    onScroll();

    if (scrollToTopButton) {
        scrollToTopButton.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    const experienceSelect = document.getElementById('experience-select');
    const experienceCards = document.querySelectorAll('.experience-card[data-experience]');

    if (experienceSelect && experienceCards.length) {
        const updateExperience = () => {
            const selectedValue = experienceSelect.value;
            experienceCards.forEach((card) => {
                card.style.display = card.getAttribute('data-experience') === selectedValue ? 'block' : 'none';
            });
        };

        experienceSelect.addEventListener('change', updateExperience);
        updateExperience();
    }

    const galleryModal = document.getElementById('gallery-modal');

    if (galleryModal) {
        const overlay = galleryModal.querySelector('.gallery-overlay');
        const image = galleryModal.querySelector('.gallery-current-image');
        const caption = galleryModal.querySelector('.gallery-caption');
        const closeButton = galleryModal.querySelector('.gallery-close');
        const nextButton = galleryModal.querySelector('.gallery-next');
        const prevButton = galleryModal.querySelector('.gallery-prev');

        let galleryImages = [];
        let currentIndex = 0;

        const showImage = (index) => {
            if (!galleryImages.length) {
                return;
            }

            currentIndex = (index + galleryImages.length) % galleryImages.length;
            image.src = galleryImages[currentIndex].src;
            image.alt = galleryImages[currentIndex].alt || '';
            caption.textContent = galleryImages[currentIndex].alt || '';
        };

        const closeGallery = () => {
            galleryModal.style.display = 'none';
            galleryModal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
            galleryImages = [];
            currentIndex = 0;
            image.src = '';
            caption.textContent = '';
        };

        const openGallery = (images, startIndex = 0) => {
            if (!images.length) {
                return;
            }

            galleryImages = images;
            showImage(startIndex);
            galleryModal.style.display = 'flex';
            galleryModal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
        };

        document.querySelectorAll('.view-gallery').forEach((button) => {
            button.addEventListener('click', () => {
                const card = button.closest('.extra-card') || button.closest('.research-card') || button.closest('.project-info');
                if (!card) {
                    return;
                }

                const images = [];
                const primaryImage = card.querySelector('.project-image img');
                if (primaryImage && primaryImage.src) {
                    images.push({
                        src: primaryImage.src,
                        alt: primaryImage.alt || ''
                    });
                }

                card.querySelectorAll('.gallery-images img').forEach((galleryImage) => {
                    if (galleryImage.src) {
                        images.push({
                            src: galleryImage.src,
                            alt: galleryImage.alt || ''
                        });
                    }
                });

                openGallery(images);
            });
        });

        closeButton?.addEventListener('click', closeGallery);
        overlay?.addEventListener('click', closeGallery);
        nextButton?.addEventListener('click', () => showImage(currentIndex + 1));
        prevButton?.addEventListener('click', () => showImage(currentIndex - 1));

        document.addEventListener('keydown', (event) => {
            if (galleryModal.getAttribute('aria-hidden') !== 'false') {
                return;
            }

            if (event.key === 'Escape') {
                closeGallery();
            }

            if (event.key === 'ArrowRight') {
                showImage(currentIndex + 1);
            }

            if (event.key === 'ArrowLeft') {
                showImage(currentIndex - 1);
            }
        });
    }
});
