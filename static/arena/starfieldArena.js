import { createCamera } from './components/camera.js';
import { createScene } from './components/scene.js';

import { Spheres } from './components/spheres.js';

import { createRenderer } from './systems/renderer.js';
import { Resizer } from './systems/resizer.js';
import { Loop } from './systems/loop.js';

import { DataExchanger } from './systems/data_exchanger.js';
//import { DadaExchanger } from './systems/dada_exchanger.js';
import { Mask } from './components/mask.js';

import { Group, 
    MathUtils, 
    SphereGeometry, 
    MeshBasicMaterial, 
    Mesh, 
    BackSide } from '/static/vendor/three.module.js';

let camera;
let renderer;
let scene;
let loop;

let io;

/**
 * Representation of an experimental arena.
 */
class StarfieldArena {

    /**
     * Virtual representation of an arena. The arena consists of a scene, has a camera and a 
     * renderer and uses an external loop and re-sizer to respond to time and screen changes.
     * 
     * @constructor
     * @param {Element} container - The html element where the virtual representation of the arena
     *      is going to be presented
     */
    constructor(container, orientation=0) {
        camera = createCamera(orientation);
        scene = createScene();
        renderer = createRenderer();
        
        loop = new Loop(camera, scene, renderer);
        loop.updateables.push(camera);

        container.append(renderer.domElement);
        
        const spheres = new Spheres(10, 170);
        const masks = new Mask(0,0);
        scene.add(spheres);
        scene.add(masks);
        loop.updateables.push(spheres);
        // if (orientation < 180){
        //     io = new DadaExchanger(camera, scene, loop, spheres, masks);
        // } else {
        io = new DataExchanger(camera, scene, loop, spheres, masks);
        // }

        camera.loggable = io;
        loop.loggable = io;
        spheres.loggable = io;
        masks.loggable = io;

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