import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.152.2/build/three.module.js';
import * as CANNON from 'https://cdn.jsdelivr.net/npm/cannon-es@0.20.0/dist/cannon-es.js';

// Scene setup
let scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);

let camera = new THREE.PerspectiveCamera(75, 600/400, 0.1, 1000);
let renderer = new THREE.WebGLRenderer();
renderer.setSize(600, 400);
document.getElementById('simulation-container').appendChild(renderer.domElement);

// Lighting
let ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);
let directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(5, 10, 7);
scene.add(directionalLight);

// Cannon-es physics world
const world = new CANNON.World({
    gravity: new CANNON.Vec3(0, -9.82, 0)
});

// Ground (physics)
const groundBody = new CANNON.Body({
    type: CANNON.Body.STATIC,
    shape: new CANNON.Plane(),
    position: new CANNON.Vec3(0, 0, 0)
});
groundBody.quaternion.setFromEuler(-Math.PI / 2, 0, 0);
world.addBody(groundBody);

// Ground (visual)
let groundGeometry = new THREE.PlaneGeometry(50, 50);
let groundMaterial = new THREE.MeshLambertMaterial({color: 0x228B22});
let ground = new THREE.Mesh(groundGeometry, groundMaterial);
ground.rotation.x = -Math.PI / 2;
scene.add(ground);

// Robot (cube body)
let robotGeometry = new THREE.BoxGeometry(1, 1, 1);
let robotMaterial = new THREE.MeshStandardMaterial({color: 0x5555ff});
let robotMesh = new THREE.Mesh(robotGeometry, robotMaterial);
scene.add(robotMesh);

// Robot (physics body)
const robotShape = new CANNON.Box(new CANNON.Vec3(0.5, 0.5, 0.5));
const robotBody = new CANNON.Body({
    mass: 2,
    shape: robotShape,
    position: new CANNON.Vec3(0, 5, 0),
    material: new CANNON.Material({friction: 0.4, restitution: 0.1})
});
world.addBody(robotBody);

camera.position.set(0, 5, 10);
camera.lookAt(0, 0, 0);

// Controls
let move = {forward: false, backward: false, left: false, right: false, jump: false};
document.addEventListener('keydown', (e) => {
    if (e.key === 'w') move.forward = true;
    if (e.key === 's') move.backward = true;
    if (e.key === 'a') move.left = true;
    if (e.key === 'd') move.right = true;
    if (e.key === ' ' && Math.abs(robotBody.velocity.y) < 0.05) {
        robotBody.velocity.y = 5; // jump
    }
});
document.addEventListener('keyup', (e) => {
    if (e.key === 'w') move.forward = false;
    if (e.key === 's') move.backward = false;
    if (e.key === 'a') move.left = false;
    if (e.key === 'd') move.right = false;
});

// Animation loop
function animate() {
    requestAnimationFrame(animate);

    // Apply movement force
    let force = 10;
    if (move.forward) robotBody.applyForce(new CANNON.Vec3(0, 0, -force), robotBody.position);
    if (move.backward) robotBody.applyForce(new CANNON.Vec3(0, 0, force), robotBody.position);
    if (move.left) robotBody.applyForce(new CANNON.Vec3(-force, 0, 0), robotBody.position);
    if (move.right) robotBody.applyForce(new CANNON.Vec3(force, 0, 0), robotBody.position);

    world.fixedStep();

    // Sync Three.js mesh with Cannon-es body
    robotMesh.position.copy(robotBody.position);
    robotMesh.quaternion.copy(robotBody.quaternion);

    renderer.render(scene, camera);
}
animate();