import { createStarfieldCamera } from './arena/components/starfield_camera.js';
import { createScene } from './components/scene.js';
import { createRenderer } from './systems/renderer.js';
import { StarfieldLoop } from './systems/starfield_loop.js';
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

let camera;
let renderer;
let scene;
let loop;
let sphere;

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
        camera = createStarfieldCamera();
        scene = createScene();
        renderer = createRenderer();
        loop = new StarfieldLoop(camera, scene, renderer);

        container.append( renderer.domElement );

        //create sphere
        const geometry = new SphereGeometry(1, 32, 16);
        const material = new MeshBasicMaterial( { color: 0x00ff00 } );
        sphere = new Mesh(geometry, material);
        scene.add( sphere );

        camera.position.z = 5;
    }

    /**
     * temp method for animation of the arena - will be replaced
     */
    animate() {
        requestAnimationFrame( animate );
        sphere.rotation.x += 0.01;
        sphere.rotation.y += 0.01;
        renderer.render( scene, camera );
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