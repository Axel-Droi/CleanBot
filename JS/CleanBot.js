// document.addEventListener("DOMContentLoaded", () => {
//   // Fade in page on load
//   document.body.style.opacity = 0;
//   document.body.style.transition = "opacity 0.5s ease";
//   requestAnimationFrame(() => {
//     document.body.style.opacity = 1;
//   });

//   // Fade out before navigating away
//   const navLinks = document.querySelectorAll("nav a");
//   navLinks.forEach(link => {
//     link.addEventListener("click", (e) => {
//       e.preventDefault();
//       const href = link.getAttribute("href");
//       document.body.style.opacity = 0;
//       setTimeout(() => {
//         window.location.href = href;
//       }, 500); // Match fade duration
//     });
//   });

//   // Nav show/hide on scroll
//   let lastScrollTop = 0;
//   const nav = document.querySelector("nav");
//   let ticking = false;

//   window.addEventListener("scroll", () => {
//     if (!ticking) {
//       window.requestAnimationFrame(() => {
//         let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

//         if (scrollTop > lastScrollTop && scrollTop > 100) {
//           // Scroll down — hide nav
//           nav.style.opacity = "0";
//           nav.style.transform = "translateY(-20px)";
//           nav.style.pointerEvents = "none"; // disable clicks when hidden
//         } else {
//           // Scroll up — show nav
//           nav.style.opacity = "1";
//           nav.style.transform = "translateY(0)";
//           nav.style.pointerEvents = "auto";
//         }

//         lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
//         ticking = false;
//       });
//       ticking = true;
//     }
//   });
//   var opacity = 0;
//         var intervalID = 0;
//         window.onload = fadeIn;
        
//         function fadeIn() {
//             setInterval(show, 200);
//         }
        
//         // function show() {
//         //     var body = document.getElementById("body");
//         //     opacity = Number(window.getComputedStyle(body)
//         //                     .getPropertyValue("opacity"));
//         //     if (opacity < 1) {
//         //         opacity = opacity + 0.1;
//         //         body.style.opacity = opacity
//         //     } else {
//         //         clearInterval(intervalID);
//         //     }
//         // }
// });


document.addEventListener("DOMContentLoaded", () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('show');
      } else {
        entry.target.classList.remove('show');
      }
    });
  });

  const hiddenElements = document.querySelectorAll('.hidden');
  hiddenElements.forEach((el) => observer.observe(el));
});
