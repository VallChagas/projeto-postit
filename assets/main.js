/*=============== PAGE INITIALIZATION ===============*/
document.addEventListener("DOMContentLoaded", () => {
  initHeader();
  initMobileMenu();
  initReveal();
  initImageFallbacks();
  initReminderPreview();
});

/*=============== HEADER SCROLL ===============*/
function initHeader() {
  const header = document.querySelector("#site-header");

  if (!header) {
    return;
  }

  const updateHeader = () => {
    header.classList.toggle("is-scrolled", window.scrollY > 8);
  };

  updateHeader();
  window.addEventListener("scroll", updateHeader, { passive: true });
}

/*=============== MOBILE NAVIGATION ===============*/
function initMobileMenu() {
  const toggle = document.querySelector(".menu-toggle");
  const navigation = document.querySelector("#primary-navigation");

  if (!toggle || !navigation) {
    return;
  }

  const closeMenu = () => {
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open navigation menu");
    navigation.classList.remove("is-open");
  };

  toggle.addEventListener("click", () => {
    const isOpen = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!isOpen));
    toggle.setAttribute("aria-label", isOpen ? "Open navigation menu" : "Close navigation menu");
    navigation.classList.toggle("is-open", !isOpen);
  });

  navigation.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeMenu();
    }
  });

  document.addEventListener("click", (event) => {
    if (!navigation.contains(event.target) && !toggle.contains(event.target)) {
      closeMenu();
    }
  });
}

/*=============== SCROLL REVEAL ===============*/
function initReveal() {
  const elements = Array.from(document.querySelectorAll("[data-reveal]"));
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reducedMotion || !("IntersectionObserver" in window)) {
    elements.forEach((element) => element.classList.add("is-visible"));
    return;
  }

  const siblingsByParent = new Map();
  elements.forEach((element) => {
    const siblings = siblingsByParent.get(element.parentElement) || [];
    siblings.push(element);
    siblingsByParent.set(element.parentElement, siblings);
  });

  siblingsByParent.forEach((siblings) => {
    siblings.forEach((element, index) => {
      element.style.transitionDelay = `${Math.min(index * 80, 320)}ms`;
    });
  });

  const observer = new IntersectionObserver((entries, currentObserver) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        currentObserver.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.12,
    rootMargin: "0px 0px -40px 0px"
  });

  elements.forEach((element) => observer.observe(element));
}

/*=============== IMAGE FALLBACKS ===============*/
function initImageFallbacks() {
  document.querySelectorAll("img").forEach((image) => {
    const showImage = () => image.classList.add("is-loaded");
    const hideBrokenImage = () => {
      image.hidden = true;
      image.setAttribute("aria-hidden", "true");
      const fallback = image.parentElement.querySelector(".image-placeholder");
      if (fallback) {
        fallback.hidden = false;
      }
    };

    image.addEventListener("load", showImage, { once: true });
    image.addEventListener("error", hideBrokenImage, { once: true });

    if (image.complete && image.naturalWidth > 0) {
      showImage();
    } else if (image.complete && image.naturalWidth === 0) {
      hideBrokenImage();
    }
  });
}

/*=============== REMINDER PREVIEW ===============*/
function initReminderPreview() {
  const select = document.querySelector("#reminder-example");
  const button = document.querySelector("#preview-button");
  const output = document.querySelector("#demo-output");
  const status = document.querySelector("#demo-status");
  const stage = document.querySelector("#demo-stage");
  const character = document.querySelector("#demo-character");
  const bubble = document.querySelector("#demo-bubble");

  if (!select || !button || !output || !status || !stage || !character || !bubble) {
    return;
  }

  const examples = {
    stretch: "Take a short stretch break",
    water: "Drink a glass of water",
    focus: "Return to your reading"
  };

  button.addEventListener("click", () => {
    const title = examples[select.value];

    if (!title) {
      status.textContent = "ERROR";
      status.className = "status-badge is-error";
      output.textContent = "This reminder example is not available. Please choose another option.";
      return;
    }

    bubble.textContent = title;
    character.setAttribute("aria-hidden", "false");
    stage.classList.remove("is-active");
    void stage.offsetWidth;
    stage.classList.add("is-active");

    const preview = {
      title,
      scheduled_for: "Today, 10:30",
      storage: "Browser preview only — not saved",
      action: "Mark complete or close the desktop post-it"
    };

    status.textContent = "OK";
    status.className = "status-badge is-ok";
    output.textContent = JSON.stringify(preview, null, 2);
  });
}
