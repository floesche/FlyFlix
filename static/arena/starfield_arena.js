
import { createScene } from './components/scene.js';
import { createStarfieldCamera } from './components/starfield_camera.js';
import { createRenderer } from './systems/renderer.js';
import { Resizer } from './systems/resizer.js';
import { Spheres } from './components/spheres.js';
import { Loop } from './systems/loop.js';


let scene;
let camera;
let renderer;
let io;
let loop;
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

        //loop to animate the scene
        loop = new Loop(camera, scene, renderer);

        // add the renderer
        container.append( renderer.domElement );

        // create an object made up of a group of spheres;
        spheres = new Spheres(sphereCount, sphereRadius, shellRadius);
        scene.add(spheres);
        loop.updateables.push(spheres);
        
        const resizer = new Resizer(container, camera, renderer);
    }
    
    
    /**
     * Render the arena.
     * 
     */
    render() {
        renderer.render(scene, camera);
    }

    /**
     * Start the animation of the arena.
     */
    start() {
        loop.start();
    }

    /**
     * Stop the animation of the arena.
     */
    stop() {
        loop.stop();
    }

}


export { StarfieldArena };
