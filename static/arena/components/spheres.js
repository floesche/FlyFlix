import { Group, 
    MathUtils, 
    SphereGeometry, 
    MeshBasicMaterial, 
    Mesh,
    Color,
} from '/static/vendor/three.module.js';

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
    constructor( sphereCount, sphereRadius, shellRadius, color=0x00ff00 ){
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
     * @param {number} sphereCount - the amount of total spheres surrounding the fly
     * @param {number} sphereRadius - the radius of the spheres in the starfield
     * @param {number} shellRadius - the radius of the shell / distance between camera and spheres
     * @param {color} color - color of the spheres
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
     * Interface to change the sphere setup
     * @param {number} sphereCount - the amount of total spheres surrounding the fly
     * @param {number} sphereRadius - the radius of the spheres in the starfield
     * @param {number} shellRadius - the radius of the shell / distance between camera and spheres
     * @param {color} color - color of the spheres (default is green)
     */
    changeSpheres(sphereCount, sphereRadius, shellRadius, color=0x00ff00) {
        this.clear();
        this._log('panels-change-clear');
        this._log('xxxx',barHeight )
        this._setup(sphereCount, sphereRadius, shellRadius, color);
    }


    /**
     * Set the rotational speed of the spheres (in radians)
     * 
     * @param {number} rotateRadHz - rotational speed of the spherical shell in radians per second, 
     * positive is upwards
     */
    setRotateRadHz(rotateRadHz){
        this.rotateRadHz = rotateRadHz;
        this._log('spheres-set-rotateRadHz', rotateRadHz);
    }

    /**
    * Set the rotational speed of the spherical shell (in degree)
    * 
    * @param {number} rotate_deg_hz - rotational speed of the spheres in degree per second, 
    *      positive is up
    */
    setRotateDegHz(rotate_deg_hz){
        this.rotateRadHz = MathUtils.degToRad(rotate_deg_hz);
        this._log('spheres-set-rotate_deg_hz', rotate_deg_hz);
    }

    setOscillation(osc_hz, max_deg){
        if (osc_hz>0){
            this.startTime = Date.now()/1000;
        } else {
            this.startTime = undefined;
        }
        this.osc_hz = osc_hz;
        this.max_deg = MathUtils.degToRad(max_deg);
    }

    /**
     * Rotate the spherical shell to an absolute angle.
     * 
     * @param {number} rotation - set the absolute rotation of the camera in radians
     */
    setRotationRad(rotation){
        this.rotation.y = rotation % (2*Math.PI);
        this._log('spheres-set-rotationRad', rotation);
    }


    /**
     * Interface to allow arena to be animated.
     * 
     * @param {number} delta - time interval since last tick
     */
    tick(delta){
        this.rotateX(-0.01);
    }

    /**
     * Set the Loop ID
     * 
     * @param {bigint} lid - Loop ID
     */
    setLid(lid){
        this._log('spheres-set-lid-old', lid);
        this.lid = lid;
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