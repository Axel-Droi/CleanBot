// window.addEventListener('DOMContentLoaded', () => {
//   const robot = document.getElementById('robot');
//   const container = document.getElementById('simulation-container');

//   const step = 10; // pixels per key press

//   // Parse initial position from style or set default
//   let topPos = parseInt(robot.style.top, 10) || 175;
//   let leftPos = parseInt(robot.style.left, 10) || 275;

//   // Update the robot's position on screen
//   function updatePosition() {
//     robot.style.top = topPos + 'px';
//     robot.style.left = leftPos + 'px';
//   }

//   // Focus the container to ensure it receives keyboard input
//   container.focus();

//   window.addEventListener('keydown', (event) => {
//     const key = event.key.toLowerCase();

//     switch (key) {
//       case 'w':
//       case 'arrowup':
//         if (topPos - step >= 0) topPos -= step;
//         break;
//       case 's':
//       case 'arrowdown':
//         if (topPos + step <= container.clientHeight - robot.clientHeight) topPos += step;
//         break;
//       case 'a':
//       case 'arrowleft':
//         if (leftPos - step >= 0) leftPos -= step;
//         break;
//       case 'd':
//       case 'arrowright':
//         if (leftPos + step <= container.clientWidth - robot.clientWidth) leftPos += step;
//         break;
//       default:
//         return; // Ignore other keys
//     }

//     updatePosition();

//     event.preventDefault(); // prevent default scrolling
//   });
// });
