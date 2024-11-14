const toggle = document.querySelector(".toggle");
const menu = document.querySelector(".menu");
const items = document.querySelectorAll(".item");

/* Toggle mobile menu */
function toggleMenu() {
  if (menu.classList.contains("active")) {
    menu.classList.remove("active");
    toggle.querySelector("a").innerHTML = "<i class='fas fa-bars'></i>";
  } else {
    menu.classList.add("active");
    toggle.querySelector("a").innerHTML = "<i class='fas fa-times'></i>";
  }
}

/* Activate Submenu */
function toggleItem() {
  if (this.classList.contains("submenu-active")) {
    this.classList.remove("submenu-active");
  } else if (menu.querySelector(".submenu-active")) {
    menu.querySelector(".submenu-active").classList.remove("submenu-active");
    this.classList.add("submenu-active");
  } else {
    this.classList.add("submenu-active");
  }
}

/* Close Submenu From Anywhere */
function closeSubmenu(e) {
  if (menu.querySelector(".submenu-active")) {
    let isClickInside = menu
      .querySelector(".submenu-active")
      .contains(e.target);

    if (!isClickInside && menu.querySelector(".submenu-active")) {
      menu.querySelector(".submenu-active").classList.remove("submenu-active");
    }
  }
}
/* Event Listeners */
toggle.addEventListener("click", toggleMenu, false);
for (let item of items) {
  if (item.querySelector(".submenu")) {
    item.addEventListener("click", toggleItem, false);
  }
  item.addEventListener("keypress", toggleItem, false);
}
document.addEventListener("click", closeSubmenu, false);

document.addEventListener('DOMContentLoaded', function () {
  const elements = document.querySelectorAll('.animate-on-scroll');

  function handleScroll() {
      elements.forEach(element => {
          const rect = element.getBoundingClientRect();

          // Si el elemento está en la vista, agregar la clase 'visible'
          if (rect.top < window.innerHeight * 0.8 && rect.bottom > 0) {
              element.classList.add('visible');
          } else {
              // Si el elemento está fuera de la vista, quitar la clase 'visible'
              element.classList.remove('visible');
          }
      });
  }

  window.addEventListener('scroll', handleScroll);
  handleScroll(); // Llama a la función al cargar la página para los elementos visibles inicialmente
});
