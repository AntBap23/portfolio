document.addEventListener('DOMContentLoaded', () => {
    const root = document.documentElement;
    const themeToggleButtons = document.querySelectorAll('.theme-toggle');
    const nav = document.querySelector('.navbar');
    const navToggle = document.querySelector('.nav-toggle');
    const navPanel = document.querySelector('.nav-panel');
    const scrollToTopButton = document.getElementById('scrollToTop');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    document.querySelectorAll('.spotlight-card').forEach((card) => {
        card.addEventListener('pointermove', (event) => {
            const rect = card.getBoundingClientRect();
            const x = ((event.clientX - rect.left) / rect.width) * 100;
            const y = ((event.clientY - rect.top) / rect.height) * 100;

            card.style.setProperty('--mouse-x', `${x}%`);
            card.style.setProperty('--mouse-y', `${y}%`);
        });
    });

    const storage = {
        get(key) {
            try {
                return window.localStorage.getItem(key);
            } catch (error) {
                return null;
            }
        },
        set(key, value) {
            try {
                window.localStorage.setItem(key, value);
            } catch (error) {
                // Browsers can block localStorage in private or restricted contexts.
            }
        }
    };

    const applyTheme = (theme) => {
        root.dataset.theme = theme;
        storage.set('theme', theme);
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

    const savedTheme = storage.get('theme');
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
                behavior: prefersReducedMotion.matches ? 'auto' : 'smooth',
                block: 'start'
            });
            closeNavMenu();
        });
    });

    document.querySelectorAll('a[href]').forEach((link) => {
        link.addEventListener('click', () => {
            if (typeof window.gtag !== 'function') {
                return;
            }

            const href = link.getAttribute('href') || '';
            let eventName = '';

            if (href.includes('calendly.com')) {
                eventName = 'lead_click_calendly';
            } else if (href.startsWith('mailto:')) {
                eventName = 'lead_click_email';
            } else if (href.includes('linkedin.com')) {
                eventName = 'lead_click_linkedin';
            } else if (href.includes('kpi-dashboard-readiness-checklist.pdf')) {
                eventName = 'resource_click_kpi_checklist';
            }

            if (eventName) {
                const section = link.closest('section, nav, footer');
                window.gtag('event', eventName, {
                    link_url: href,
                    link_text: link.textContent.trim(),
                    link_location: section?.id || section?.className || 'unknown'
                });
            }
        });
    });

    const sections = document.querySelectorAll('section');
    root.classList.add('js-enabled');

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, {
            threshold: 0.14
        });

        sections.forEach((section) => observer.observe(section));
    } else {
        sections.forEach((section) => section.classList.add('animate-in'));
    }

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
                behavior: prefersReducedMotion.matches ? 'auto' : 'smooth'
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

// Website-to-inbox delivery. Keep user input available if the provider fails.
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('project-inquiry');
    if (!form) return;
    const service = form.elements.namedItem('service');
    const requested = new URLSearchParams(window.location.search).get('service');
    if ([...service.options].some(option => option.value === requested)) service.value = requested;
    const status = document.getElementById('inquiry-status');
    const draft = document.getElementById('inquiry-draft');
    const button = form.querySelector('button[type="submit"]');
    let submitting = false;

    const prepareFallback = (body, subject) => {
        draft.value = body;
        document.getElementById('inquiry-fallback').hidden = false;
        document.getElementById('inquiry-email-app').href = `mailto:bapanalytics00@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        document.getElementById('inquiry-gmail').href = `https://mail.google.com/mail/?view=cm&fs=1&to=bapanalytics00%40gmail.com&su=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    };
    form.addEventListener('submit', async event => {
        event.preventDefault();
        if (submitting || !form.reportValidity()) return;
        const serviceName = service.value ? service.options[service.selectedIndex].text : 'General inquiry';
        const subject = 'Consulting project inquiry: ' + serviceName;
        form.elements.namedItem('_subject').value = subject;
        const data = new FormData(form);
        const body = [
            ['Name', data.get('name')], ['Email', data.get('email')],
            ['Business challenge', data.get('challenge')],
            ['Organization', data.get('organization') || 'Not provided'],
            ['Service', serviceName],
            ['Desired deliverables', data.get('deliverables') || 'To be discussed'],
            ['Budget range', data.get('budget') || 'To be discussed'],
            ['Project timeline', data.get('timeline') || 'To be discussed'],
            ['Meeting preferences', data.get('preferences') || 'Not provided']
        ].map(([label, value]) => `${label}: ${String(value).trim()}`).join('\n\n');
        const controller = new AbortController();
        const timeout = window.setTimeout(() => controller.abort(), 20000);
        submitting = true;
        button.disabled = true;
        form.setAttribute('aria-busy', 'true');
        status.textContent = 'Sending your inquiry…';
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 'Accept': 'application/json' },
                body: data,
                signal: controller.signal
            });
            const result = await response.json();
            if (!response.ok || result.ok === false || (Array.isArray(result.errors) && result.errors.length)) {
                const messages = Array.isArray(result.errors)
                    ? result.errors.map(error => error.message).filter(message => typeof message === 'string').join(' ')
                    : '';
                throw new Error(messages || 'The form service could not accept the inquiry.');
            }
            status.textContent = 'Your inquiry was accepted by the form service. I’ll reply within two business days. No call needed.';
            document.getElementById('inquiry-fallback').hidden = true;
            form.reset();
            if (typeof window.gtag === 'function') window.gtag('event', 'project_inquiry_submitted', { service: data.get('service') || 'unspecified' });
        } catch (error) {
            prepareFallback(body, subject);
            const detail = error instanceof Error && error.name !== 'AbortError' && error.message !== 'Failed to fetch' ? ` ${error.message}` : '';
            status.textContent = 'We could not confirm submission. Your details are preserved below. Please copy your inquiry or open a draft in Gmail or your email app and send it to bapanalytics00@gmail.com. If you received a separate confirmation, avoid sending a duplicate.' + detail;
        } finally {
            window.clearTimeout(timeout);
            submitting = false;
            button.disabled = false;
            form.removeAttribute('aria-busy');
        }
    });
    document.getElementById('copy-inquiry').addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(draft.value);
            status.textContent = 'Draft copied. Paste it into an email to bapanalytics00@gmail.com and send it to submit your inquiry.';
        } catch {
            draft.focus();
            draft.select();
            status.textContent = 'Select and copy the draft, then email it to bapanalytics00@gmail.com.';
        }
    });
});
