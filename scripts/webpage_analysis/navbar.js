document.addEventListener("DOMContentLoaded", () => {
  const menuIcon = document.getElementById("menu-icon");
  const navLinks = document.getElementById("nav-links");
  const details = document.querySelectorAll("details");

  details.forEach((detail) => setMenuWidth(detail));

  function setMenuWidth(elem) {
    let leftPos = elem.getBoundingClientRect().left;
    let dropDownEl = elem.querySelector(".dropdown");
    if (dropDownEl) {
      dropDownEl.style.width = "calc(100vw - " + (leftPos + 20) + "px)";
    }
  }
  window.addEventListener("resize", () => {
    details.forEach((detail) => setMenuWidth(detail));
  });

  menuIcon.addEventListener("click", () => {
    navLinks.classList.toggle("active");
  });

  document.addEventListener("click", (event) => {
    const isClickInsideNav =
      navLinks.contains(event.target) || menuIcon.contains(event.target);
    if (!isClickInsideNav) {
      navLinks.classList.remove("active");
    }
    Array.from(document.querySelectorAll(".nav-item details")).forEach(
      (detailsElement) => {
        if (!detailsElement.contains(event.target)) {
          detailsElement.open = false;
        }
      }
    );
  });
});
