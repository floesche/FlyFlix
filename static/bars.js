
import {Arena} from './Arena/Arena.js';



function main() {
    // Get a reference to the container element
    const container = document.querySelector('#scene-container');
  
    // 1. Create an instance of the World app
    const arena = new Arena(container);
  
    // 2. Render the scene
    // arena.render();
    arena.start();
  }

// call main to start the app
main();



// import { 
//     Clock, 
//     PerspectiveCamera, 
//     Scene, WebGLRenderer, 
//     PlaneBufferGeometry, 
//     MeshBasicMaterial, Mesh, 
//     DoubleSide} from '/static/vendor/three.module.js';


// let clock = new Clock();
// let delta = 0;
// // 30 fps
// let interval = 1 / 60;

// const scene = new Scene();
// //const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );
// const camera = new PerspectiveCamera(120, window.innerWidth / window.innerHeight, 1, 1000);
// // const camera = new THREE.OrthographicCamera( window.innerWidth / - 2, window.innerWidth / 2, window.innerHeight / 2, window.innerHeight / - 2, 1, 1000 );
// // const camera = new THREE.OrthographicCamera(-5, 5, -5, 5, 1, 1000 );

// const renderer = new WebGLRenderer();
// renderer.setSize(window.innerWidth, window.innerHeight);
// document.body.appendChild(renderer.domElement);

// const angle = 9; // in degree
// const radius = 35; // in 

// const width = Math.atan((angle / 2) * Math.PI / 180) * radius * 2;

// const geometry = new PlaneBufferGeometry(width, 150);
// const material = new MeshBasicMaterial({ color: 0x00ff00, side: DoubleSide });

// const bars = [];

// for (let x = 0; x < 360; x = x + 2 * angle) {
//     const bar = new Mesh(geometry, material);
//     bar.rotation.y = x * Math.PI / 180;

//     bar.position.x = Math.sin(x * Math.PI / 180) * radius;
//     bar.position.z = Math.cos(x * Math.PI / 180) * radius;

//     scene.add(bar);
//     bars.push(bar);
// }

// const animate = function () {
//     requestAnimationFrame(animate);

//     delta += clock.getDelta();

//     camera.rotation.y += 1 * Math.PI / 180;

//     bars.forEach((bar) => {
//         //bar.rotation.x += 0.01;
//     });

//     if (delta > interval) {
//         renderer.render(scene, camera);
//         delta = delta % interval;
//     }
// };

// window.addEventListener('resize', onWindowResize);

// // const gui = new GUI();
// // 	gui.add( params, 'enableWind' ).name( 'Enable wind' );
// // 	gui.add( params, 'showBall' ).name( 'Show ball' );
// // 	gui.add( params, 'togglePins' ).name( 'Toggle pins' );
// // 	//


// function onWindowResize() {
//     camera.aspect = window.innerWidth / window.innerHeight;
//     camera.updateProjectionMatrix();

//     renderer.setSize(window.innerWidth, window.innerHeight);
// }

// animate();