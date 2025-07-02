// // filepath: /cleanbot-simulation/cleanbot-simulation/src/simulation.js
// import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.152.2/build/three.module.js';
// import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.152.2/examples/jsm/controls/OrbitControls.js';

// let scene, camera, renderer, robot, controls;
// let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;

// init();
// animate();

// function init() {
//   // Scene setup
//   scene = new THREE.Scene();
//   scene.background = new THREE.Color(0xa0d8f0); // light blue sky color

//   // Camera
//   camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
//   camera.position.set(0, 5, 10);

//   // Renderer
//   renderer = new THREE.WebGLRenderer({antialias: true});
//   renderer.setSize(window.innerWidth, 600);
//   document.getElementById('simulation-container').appendChild(renderer.domElement);

//   // Lighting
//   const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
//   scene.add(ambientLight);

//   const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
//   directionalLight.position.set(5, 10, 7);
//   scene.add(directionalLight);

//   // Ground (park/beach simulation)
//   const groundGeometry = new THREE.PlaneGeometry(50, 50);
//   const groundMaterial = new THREE.MeshLambertMaterial({color: 0x228B22}); // green grass color
//   const ground = new THREE.Mesh(groundGeometry, groundMaterial);
//   ground.rotation.x = - Math.PI / 2;
//   scene.add(ground);

//   // Simple robot model (a box + arm)
//   const robotGroup = new THREE.Group();

//   const bodyGeometry = new THREE.BoxGeometry(1, 1, 1);
//   const bodyMaterial = new THREE.MeshStandardMaterial({color: 0x5555ff});
//   const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
//   body.position.y = 0.5;
//   robotGroup.add(body);

//   const armGeometry = new THREE.BoxGeometry(0.2, 0.6, 0.2);
//   const armMaterial = new THREE.MeshStandardMaterial({color: 0xffaa00});
//   const arm = new THREE.Mesh(armGeometry, armMaterial);
//   arm.position.set(0.7, 1, 0);
//   robotGroup.add(arm);

//   robotGroup.position.set(0, 0, 0);
//   scene.add(robotGroup);
//   robot = robotGroup;

//   // Controls for camera orbit
//   controls = new OrbitControls(camera, renderer.domElement);
//   controls.target.set(0, 0.5, 0);
//   controls.update();

//   // Event listeners for movement
//   window.addEventListener('keydown', keyDown);
//   window.addEventListener('keyup', keyUp);
//   window.addEventListener('resize', onWindowResize);
// }

// function keyDown(event) {
//   switch(event.key.toLowerCase()) {
//     case 'w': moveForward = true; break;
//     case 's': moveBackward = true; break;
//     case 'a': moveLeft = true; break;
//     case 'd': moveRight = true; break;
//   }
// }

// function keyUp(event) {
//   switch(event.key.toLowerCase()) {
//     case 'w': moveForward = false; break;
//     case 's': moveBackward = false; break;
//     case 'a': moveLeft = false; break;
//     case 'd': moveRight = false; break;
//   }
// }

// function animate() {
//   requestAnimationFrame(animate);

//   // Move robot based on keys pressed
//   let speed = 0.1;

//   if(moveForward) robot.position.z -= speed;
//   if(moveBackward) robot.position.z += speed;
//   if(moveLeft) robot.position.x -= speed;
//   if(moveRight) robot.position.x += speed;

//   renderer.render(scene, camera);
// }
  
// function onWindowResize() {
//   camera.aspect = window.innerWidth / 600;
//   camera.updateProjectionMatrix();
//   renderer.setSize(window.innerWidth, 600);
// }