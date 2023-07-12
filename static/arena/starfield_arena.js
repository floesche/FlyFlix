
import { createScene } from './components/scene.js';
import { createStarfieldCamera } from './components/starfield_camera.js';
import { createRenderer } from './systems/renderer.js';
import { Resizer } from './systems/resizer.js';
import { Spheres } from './components/spheres.js';


let scene;
let camera;
let renderer;
let io;
const sphereCount = 500;
const sphereRadius = .5;
const shellRadius = 20;
let spheres;

class StarfieldArena {

    constructor(container){
        //creating the scene, camera, and renderer
        scene = createScene();
        camera = createStarfieldCamera();
        renderer = createRenderer();

        // add the renderer
        container.append( renderer.domElement );

        // create a group of spheres;
        spheres = new Spheres(sphereCount, sphereRadius, shellRadius);
        scene.add(spheres);

        //camera.position.z = 20;
        
        const resizer = new Resizer(container, camera, renderer);
    }
    
    
    start() {
        renderer.setAnimationLoop(() => {
            //this.tick()
            renderer.render( scene, camera );
        });
    }

    tick(){
        spheres.rotateX(-0.01);
    }

}


export { StarfieldArena };
