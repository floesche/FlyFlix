
import { createScene } from './arena/components/scene.js';
import { createStarfieldCamera } from './arena/components/starfield_camera.js';
import { ExperimentControl } from './arena/systems/experiment_control.js';
import { FullScreener } from './arena/systems/full_screener.js';
import { createRenderer } from './arena/systems/renderer.js';
import { Resizer } from './arena/systems/resizer.js';
import { Group, 
    MathUtils, 
    SphereGeometry, 
    MeshBasicMaterial, 
    Mesh,
    PerspectiveCamera,
    Scene,
    Color,
    WebGLRenderer,
    BoxGeometry,
} from '/static/vendor/three.module.js';

let scene;
let camera;
let renderer;
const sphereCount = 5;
let spheres = [];

function main(){

    //creating the scene, camera, and renderer
    scene = createScene();
    camera = createStarfieldCamera();
    renderer = createRenderer();
    renderer.setSize( window.innerWidth, window.innerHeight );

    // define the container and add the renderer
    const container = document.querySelector('#scene-container');
    container.append( renderer.domElement );

    // create a sphere
    const geometry = new SphereGeometry( 1, 32, 16 );
    const material = new MeshBasicMaterial( { color: 0x00ff00 } );

    for ( let i=0; i<sphereCount; i++){
        let sphereMesh = new Mesh( geometry, material );
        sphereMesh.position.x = -6 + 3*i;
        spheres.push(sphereMesh);
        scene.add(sphereMesh);
    }

    camera.position.z = 10;

    function animate() {
	    requestAnimationFrame( animate );
        for (let k=0; k<spheres.length; k++){
            spheres[k].position.x += 0.01;
        }
        //sphere.rotation.x += 0.01;
        //sphere.rotation.y += 0.01;
	    renderer.render( scene, camera );
    }

    //const fullScreenButton = new FullScreener(container);
    //const experimentController = new ExperimentControl(container);

    const resizer = new Resizer(container, camera, renderer);

    animate();
}

main();