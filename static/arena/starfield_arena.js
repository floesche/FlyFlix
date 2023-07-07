
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
const sphereRadius = 0.1;
const sphereGroup = new Group();

class StarfieldArena {

    constructor(container){
        //creating the scene, camera, and renderer
        scene = createScene();
        camera = createStarfieldCamera();
        renderer = createRenderer();

        // add the renderer
        container.append( renderer.domElement );

        // create a group spheres
        const geometry = new SphereGeometry( sphereRadius, 32, 16 );
        const material = new MeshBasicMaterial( { color: 0x00ff00 } );
        
        //const sphereGroup = new Group();
    
        for ( let i=0; i<sphereCount; i++){
            let sphereMesh = new Mesh( geometry, material );
            let positions = this._randomSpherePoint(0,0,0, 10);
            sphereMesh.position.x = positions[0];
            sphereMesh.position.y = positions[1];
            sphereMesh.position.z = positions[2];
            sphereGroup.add(sphereMesh);
        }

        scene.add(sphereGroup);
        //loop.updateables.push(sphereGroup);

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
        sphereGroup.rotateX(-0.01);
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
