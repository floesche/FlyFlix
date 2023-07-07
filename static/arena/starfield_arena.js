
import { createScene } from './components/scene.js';
import { createStarfieldCamera } from './components/starfield_camera.js';
import { ExperimentControl } from './systems/experiment_control.js';
import { FullScreener } from './systems/full_screener.js';
import { createRenderer } from './systems/renderer.js';
import { Resizer } from './systems/resizer.js';
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
import { createSpheres } from './components/spheres.js';


let scene;
let camera;
let renderer;
let io;
const sphereCount = 500;
const sphereRadius = 0.1;
const sphereGroup = new Group();
let spheres;

class StarfieldArena {

    constructor(container){
        //creating the scene, camera, and renderer
        scene = createScene();
        camera = createStarfieldCamera();
        renderer = createRenderer();

        // add the renderer
        container.append( renderer.domElement );

        // create a group of spheres
        spheres = createSpheres(sphereCount, sphereRadius);
        scene.add(spheres);

        //camera.position.z = 20;
        
        const resizer = new Resizer(container, camera, renderer);
    }
    
    
    start() {
        renderer.setAnimationLoop(() => {
            this.tick()
            renderer.render( scene, camera );
        });
    }

    tick(){
        spheres.rotateX(-0.01);
    }


    /**
     * (private)
     * Function that takes in a center point (x0, y0, z0) and a radius 
     * and returns a random point on the sphere surrounding the point with that radius
     * taken from https://stackoverflow.com/questions/5531827/random-point-on-a-given-sphere answer from user Neil Lamoureux
     * 
    */
    _randomSpherePoint(x0,y0,z0,radius){
        var u = Math.random();
        var v = Math.random();
        var theta = 2 * Math.PI * u;
        var phi = Math.acos(2 * v - 1);
        var x = x0 + (radius * Math.sin(phi) * Math.cos(theta));
        var y = y0 + (radius * Math.sin(phi) * Math.sin(theta));
        var z = z0 + (radius * Math.cos(phi));
        return [x,y,z];
    }
}


export { StarfieldArena };
