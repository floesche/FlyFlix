
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


let scene;
let camera;
let renderer;
let io;
const sphereCount = 500;

class StarfieldArena {

    constructor(container){
        //creating the scene, camera, and renderer
        scene = createScene();
        camera = createStarfieldCamera();
        renderer = createRenderer();

        // add the renderer
        container.append( renderer.domElement );

        // create spheres
        const geometry = new SphereGeometry( .1, 32, 16 );
        const material = new MeshBasicMaterial( { color: 0x00ff00 } );
        
        const sphereGroup = new Group();
    
        for ( let i=0; i<sphereCount; i++){
            let sphereMesh = new Mesh( geometry, material );
            let positions = this.randomSpherePoint(0,0,0, 10);
            sphereMesh.position.x = positions[0];
            sphereMesh.position.y = positions[1];
            sphereMesh.position.z = positions[2];
            sphereGroup.add(sphereMesh);
        }

        scene.add(sphereGroup);
        //loop.updateables.push(sphereGroup);

        camera.position.z = 20;
        
        const resizer = new Resizer(container, camera, renderer);
    }
    
    
    start() {
        renderer.setAnimationLoop(() => {
            renderer.render( scene, camera );
        });
    }


    /**
     * Function that takes in a center point and a radius 
     * and returns a random point on the sphere surrounding the point
     * taken from https://stackoverflow.com/questions/5531827/random-point-on-a-given-sphere answer from user Neil Lamoureux
     * 
    */
    randomSpherePoint(x0,y0,z0,radius){
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
