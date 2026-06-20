/**
 * NeuroRAG Authentication Experience — Ambient Motion & Cinematic Refinement
 * Shared Javascript for login.html and signup.html
 */

(function() {
  document.addEventListener('DOMContentLoaded', () => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // 1. Initialize Page-Exit / Tab Link Transitions
    initTransitions();

    // 2. Initialize Neural Background Canvas (Left Editorial Panel)
    const canvas = document.getElementById('auth-canvas');
    if (canvas && !prefersReducedMotion) {
      initNeuralCanvas(canvas);
    }

    // 3. Entrance Choreography & Tagline Typewriter Sequence
    initEntranceSequence(prefersReducedMotion);

    // 4. Initialize SVG Logo Reveal animation
    initLogoReveal();
  });

  /**
   * Staged Entrance Choreography
   */
  function initEntranceSequence(prefersReducedMotion) {
    const logo = document.querySelector('.auth-logo');
    const wordmark = document.querySelector('.auth-wordmark');
    const tagline = document.querySelector('.auth-tagline');
    const taglineContainer = document.querySelector('.auth-tagline-container');
    const formContainer = document.querySelector('.auth-form-container');
    const fields = document.querySelectorAll('.auth-field-wrapper');
    const submitWrapper = document.querySelector('.auth-submit-wrapper');

    if (prefersReducedMotion) {
      // Reduced motion: show all elements instantly
      if (logo) logo.classList.add('entered');
      if (wordmark) wordmark.classList.add('entered');
      if (tagline) {
        tagline.textContent = "A clinical reference assistant for the 51-chapter neurology handbook.";
      }
      if (taglineContainer) taglineContainer.classList.add('entered');
      if (formContainer) formContainer.classList.add('entered');
      fields.forEach(f => f.classList.add('entered'));
      if (submitWrapper) submitWrapper.classList.add('entered');
      return;
    }

    // Timeline staged triggers (T = 0 logo starts)
    if (logo) {
      logo.classList.add('entered');
    }

    // Stage 2: Wordmark (T = 150ms)
    setTimeout(() => {
      if (wordmark) wordmark.classList.add('entered');
    }, 150);

    // Stage 3: Tagline Typing (T = 400ms after load)
    setTimeout(() => {
      if (taglineContainer) taglineContainer.classList.add('entered');
      if (tagline) {
        initTypewriter(tagline);
      }
    }, 400);

    // Stage 4: Form Container (T = 600ms)
    setTimeout(() => {
      if (formContainer) formContainer.classList.add('entered');
    }, 600);

    // Stage 5: Fields Stagger (T = 800ms + 80ms increments)
    setTimeout(() => {
      fields.forEach((field, index) => {
        setTimeout(() => {
          field.classList.add('entered');
        }, index * 80);
      });
    }, 800);

    // Stage 6: Submit Button Last
    const buttonStaggerDelay = 800 + (fields.length * 80) + 80;
    setTimeout(() => {
      if (submitWrapper) submitWrapper.classList.add('entered');
    }, buttonStaggerDelay);
  }

  /**
   * Editorial Tagline Typewriter
   */
  function initTypewriter(el) {
    const text = "A clinical reference assistant for the 51-chapter neurology handbook.";
    el.textContent = "";
    el.classList.add('auth-typing');

    let startTime = null;
    let charIndex = 0;

    function type(timestamp) {
      if (!startTime) startTime = timestamp;
      const progress = timestamp - startTime;
      const expectedChars = Math.floor(progress / 30); // ~30ms per character

      if (expectedChars > charIndex) {
        charIndex = Math.min(expectedChars, text.length);
        el.textContent = text.slice(0, charIndex);
      }

      if (charIndex < text.length) {
        requestAnimationFrame(type);
      } else {
        el.classList.remove('auth-typing');
      }
    }

    requestAnimationFrame(type);
  }

  /**
   * Ambient Neural Canvas system on the left editorial panel
   */
  function initNeuralCanvas(canvas) {
    const ctx = canvas.getContext('2d');
    let width = 0;
    let height = 0;
    let nodes = [];
    let animationFrameId = null;

    // Get dynamic accent rgb color from CSS design token
    const computedStyle = getComputedStyle(document.documentElement);
    const accentRgb = computedStyle.getPropertyValue('--color-accent-rgb').trim() || '59, 158, 232';

    // Battery Optimization: pause animation when page is out of focus
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') {
        animationFrameId = requestAnimationFrame(loop);
      } else {
        cancelAnimationFrame(animationFrameId);
      }
    });

    // Resize handling
    function resize() {
      if (!canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.offsetWidth;
      height = canvas.height = canvas.parentElement.offsetHeight;
      initNodes();
    }

    function initNodes() {
      // Determine count responsively: desktop (60), tablet (45), mobile (25-30)
      let targetCount = 60;
      if (window.innerWidth < 600) {
        targetCount = 28;
      } else if (window.innerWidth < 900) {
        targetCount = 45;
      }

      nodes = [];
      for (let i = 0; i < targetCount; i++) {
        // Random speed between 0.1 and 0.3 px/frame
        const speed = 0.1 + Math.random() * 0.2;
        const angle = Math.random() * Math.PI * 2;
        
        nodes.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed,
          radius: 1.5 + Math.random() * 1.0 // subtle node size
        });
      }
    }

    function loop() {
      if (document.visibilityState === 'hidden') return;
      
      ctx.clearRect(0, 0, width, height);

      // 1. Draw Connection Lines
      ctx.lineWidth = 0.8;
      const connectionRadius = 150;

      for (let i = 0; i < nodes.length; i++) {
        const n1 = nodes[i];
        for (let j = i + 1; j < nodes.length; j++) {
          const n2 = nodes[j];
          const dx = n2.x - n1.x;
          const dy = n2.y - n1.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < connectionRadius) {
            // Distance-based opacity: linear fade out to 0 at 150px
            // Maximum visibility 10% (0.1)
            const alpha = (1 - dist / connectionRadius) * 0.1;
            ctx.strokeStyle = `rgba(${accentRgb}, ${alpha})`;
            ctx.beginPath();
            ctx.moveTo(n1.x, n1.y);
            ctx.lineTo(n2.x, n2.y);
            ctx.stroke();
          }
        }
      }

      // 2. Update and Draw Nodes
      for (let i = 0; i < nodes.length; i++) {
        const node = nodes[i];
        
        // Drift position
        node.x += node.vx;
        node.y += node.vy;

        // Wrap around boundaries
        if (node.x < 0) node.x = width;
        if (node.x > width) node.x = 0;
        if (node.y < 0) node.y = height;
        if (node.y > height) node.y = 0;

        // Nodes appearance: accent color, 15-20% opacity
        ctx.fillStyle = `rgba(${accentRgb}, 0.18)`;
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        ctx.fill();
      }

      animationFrameId = requestAnimationFrame(loop);
    }

    window.addEventListener('resize', resize);
    resize();
    animationFrameId = requestAnimationFrame(loop);
  }

  /**
   * Intercept Login/Signup tab links for smooth page exit transitions
   */
  function initTransitions() {
    const authLinks = document.querySelectorAll('a[href="/login"], a[href="/signup"]');
    authLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        // Skip transition if navigating to current page
        if (link.getAttribute('href') === window.location.pathname) return;

        e.preventDefault();
        const targetUrl = link.getAttribute('href');

        const rightCol = document.querySelector('.flex-1.flex.flex-col.justify-center');
        if (rightCol && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
          rightCol.classList.add('auth-right-panel-transition');
          setTimeout(() => {
            window.location.href = targetUrl;
          }, 150); // Match 150ms fade-out spec
        } else {
          window.location.href = targetUrl;
        }
      });
    });
  }

  /**
   * Submit Button Loading State Setup Override (Hooks into inline scripts)
   */
  window.setupSubmitLoading = function(formId, buttonId, btnTextId, spinnerId) {
    const btn = document.getElementById(buttonId);
    const textEl = document.getElementById(btnTextId);
    const spinnerEl = document.getElementById(spinnerId);
    let originalWidth = '';

    if (!btn || !textEl || !spinnerEl) return;

    // Override the global setLoading called by inline template form handlers
    window.setLoading = function(isLoading) {
      btn.disabled = isLoading;
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      if (isLoading) {
        if (prefersReducedMotion) {
          textEl.classList.add('invisible');
          spinnerEl.classList.remove('hidden');
          spinnerEl.style.opacity = '1';
          return;
        }

        // Lock button size before transition to avoid layout jumps
        originalWidth = btn.getBoundingClientRect().width + 'px';
        btn.style.width = originalWidth;
        btn.style.minWidth = originalWidth;
        
        // Force reflow
        btn.offsetHeight;

        // 1. Text fades out (150ms duration)
        textEl.style.opacity = '0';
        textEl.style.transition = 'opacity 150ms var(--apple-ease)';

        // 2 & 3. Button transitions to pill loading state
        btn.classList.add('loading-state');
        btn.style.minWidth = '40px';
        btn.style.width = '40px';
        btn.style.borderRadius = '20px'; // circular loading shape

        // 4. Spinner fades in
        spinnerEl.classList.remove('hidden');
        spinnerEl.style.opacity = '0';
        setTimeout(() => {
          if (btn.classList.contains('loading-state')) {
            spinnerEl.style.opacity = '1';
            spinnerEl.style.transition = 'opacity 150ms var(--apple-ease)';
          }
        }, 150);
      } else {
        if (prefersReducedMotion) {
          textEl.classList.remove('invisible');
          spinnerEl.classList.add('hidden');
          return;
        }

        // Restore normal button state
        btn.classList.remove('loading-state');
        btn.style.width = originalWidth;
        btn.style.minWidth = originalWidth;
        btn.style.borderRadius = '';

        // Spinner fades out
        spinnerEl.style.opacity = '0';
        spinnerEl.style.transition = 'opacity 150ms var(--apple-ease)';

        setTimeout(() => {
          if (!btn.classList.contains('loading-state')) {
            spinnerEl.classList.add('hidden');
            
            // Text fades in
            textEl.style.opacity = '1';
            textEl.style.transition = 'opacity 150ms var(--apple-ease)';

            // Clean up sizing overrides after layout completion
            setTimeout(() => {
              if (!btn.classList.contains('loading-state')) {
                btn.style.width = '';
                btn.style.minWidth = '';
              }
            }, 300);
          }
        }, 150);
      }
    };
  };

  /**
   * Measure path lengths and trigger SVG stroke-draw animation
   */
  function initLogoReveal() {
    const animatedLogos = document.querySelectorAll('.logo-reveal-animate');
    animatedLogos.forEach(logo => {
      const paths = logo.querySelectorAll('.logo-path');
      paths.forEach(path => {
        try {
          const length = path.getTotalLength();
          path.style.setProperty('--logo-path-length', length);
        } catch (e) {
          path.style.setProperty('--logo-path-length', '100');
        }
      });
      // Trigger animation in next frame
      requestAnimationFrame(() => {
        logo.classList.add('start-reveal');
      });
    });
  }

})();
