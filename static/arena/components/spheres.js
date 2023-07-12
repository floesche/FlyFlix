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

function createSpheres(sphereCount, sphereRadius, shellRadius, color=0x00ff00){
    const sphereGroup = new Group();
    const geometry = new SphereGeometry( sphereRadius, 32, 16 );
    const material = new MeshBasicMaterial( { color: 0x00ff00 } );

    for ( let i=0; i<sphereCount; i++){
        let sphereMesh = new Mesh( geometry, material );
        let positions = randomSpherePoint(0,0,0, shellRadius);
        sphereMesh.position.x = positions[0];
        sphereMesh.position.y = positions[1];
        sphereMesh.position.z = positions[2];
        sphereGroup.add(sphereMesh);
    }

    return sphereGroup;
}

/**
     * Function that takes in a center point (x0, y0, z0) and a radius 
     * and returns a random point on the sphere surrounding the point with that radius
     * taken from https://stackoverflow.com/questions/5531827/random-point-on-a-given-sphere answer from user Neil Lamoureux
     * 
    */
function randomSpherePoint(x0,y0,z0,radius){
    var u = Math.random();
    var v = Math.random();
    var theta = 2 * Math.PI * u;
    var phi = Math.acos(2 * v - 1);
    var x = x0 + (radius * Math.sin(phi) * Math.cos(theta));
    var y = y0 + (radius * Math.sin(phi) * Math.sin(theta));
    var z = z0 + (radius * Math.cos(phi));
    return [x,y,z];
}

class Spheres extends Group {

    /**
     * Representation of stars in a virtual fly arena
     * 
     * @constructor
     * @param {number} sphereCount - the amount of total spheres surrounding the fly
     * @param {number} sphereRadius - the radius of the spheres in the starfield
     * @param {number} shellRadius - the radius of the shell / distance between camera and spheres
     * @param {color} color - color of the spheres (default is green)
     */
    constructor( sphereCount, sphereRadius, shellRadius, color ){
        super();
        this.sphereCount = sphereCount;
        this.sphereRadius = sphereRadius;
        this.shellRadius = shellRadius;
        this.color = color;
        this.loggable = null;
        this.lid = 0;
        this.startTime = undefined;
        this._setup(sphereCount, sphereRadius, shellRadius, color);
    }

    /**
     * (private) method to set up the arena with stars
     * 
     */
    _setup( sphereCount, sphereRadius, shellRadius, color){

        const geometry = new SphereGeometry( sphereRadius, 32, 16 );
        const material = new MeshBasicMaterial( { color: color } );

        this._log('spheres-sphere-count', sphereCount);
        this._log('spheres-sphere-radius', sphereRadius);
        this._log('spheres-shell-radius',shellRadius);
        this._log('spheres-sphere-color', color);
        this._log('spheres-type', 'SphereGeometry');

        for ( let i=0; i<sphereCount; i++){
            const sphereMesh = new Mesh( geometry, material );
            let positions = this._randomSpherePoint(0,0,0, shellRadius);
            sphereMesh.position.x = positions[0];
            sphereMesh.position.y = positions[1];
            sphereMesh.position.z = positions[2];
            this.add(sphereMesh);
        }

    }

    /**
     * (private) method that takes in a center point (x0, y0, z0) and a radius 
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

    /**
     * (private) Interface to log all parts of the loggable list.
     * 
     * @param {string} key - key of key-value pair to be logged
     * @param {string} value - value of key-value-pair to be logged
     */
    _log(key, value){
        if (this.loggable){
            this.loggable.log(this.lid, key, value);
        }
    }
}

export { Spheres };