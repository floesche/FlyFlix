import { FullScreener } from './arena/systems/full_screener.js';
import { ExperimentControl } from './arena/systems/experiment_control.js';

import { 
    Scene,
    Color,
    SphereGeometry,
    MeshStandardMaterial,
    Mesh, 
    PerspectiveCamera,
    WebGLRenderer,
    PointLight,
    } from '/static/vendor/three.module.js';
import { MeshStandardMaterial, PerspectiveCamera, PointLight, SphereGeometry, WebGLRenderer } from './vendor/three.module.js';


/**
 * Create the experiment in the client, inside the HTML-ID `scene-container`. Supplement to the 
 *    `three-container-bars.html` template file.
 */
function main() {
   
    //Scene
    const scene = new Scene();
    scene.background = new Color(0x0000FF);

    //Create a sphere
    const geometry = new SphereGeometry(3, 64, 32);
    const material = new MeshStandardMaterial({
        color: "#00ff83",
    });
    const mesh = new Mesh(geometry, material);
    scene.add(mesh);

    //Light
    const light = new PointLight(0xffffff, 1, 100);
    light.position.set(0,10,10);
    scene.add(light);

    //Camera
    const camera = new PerspectiveCamera(45, 800 / 600); // change angle
    camera.position.z = 20;
    scene.add(camera);

    //Renderer
    const canvas = document.getElementById("mycanvas");
    const renderer = new WebGLRenderer({canvas});
    document.getElementById('mycanvas').appendChild(renderer.domElement);
    renderer.setSize(800, 600);
    renderer.render(scene, camera);

}

main();
