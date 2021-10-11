// FIXME: To be deleted?
import { PlaneBufferGeometry, Mesh, MeshBasicMaterial, DoubleSide} from '/static/vendor/three.module.js';

function createCube() {

  const angle = 9; // in degree
  const radius = 0.1525; // in 

  const width = Math.atan((angle / 2) * Math.PI / 180) * radius * 2;

  // const geometry = new BoxBufferGeometry(4, 2, 2);
  const geometry = new PlaneBufferGeometry(width, 1)
  const material = new MeshBasicMaterial({ color: 0x00ff00, side: DoubleSide });
  const cube = new Mesh(geometry, material);
  cube.position.set(0, 0, -0.15);
  return cube;
}

export { createCube };

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