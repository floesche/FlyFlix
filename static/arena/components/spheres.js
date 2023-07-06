import { Group, 
    MathUtils, 
    MeshBasicMaterial, 
    Mesh, 
    BackSide,
    SphereGeometry,
} from '/static/vendor/three.module.js';

/**
 * Representation of spheres arranged in a sphere around the fly in the virtual environment
 */

class Spheres extends Group {

    /**
     * @constructor
     * @param {number} sphereCount - amount of spheres surrounding the fly
     * @param {number} sphereRadius - radius of the spheres in m 
     * @param {number} shellRadius - radius of the shell in m (all spheres will be this distance from the camera)
     */
    constructor(sphereCount, sphereRadius){
        super();
        this.loggable = null;
        this.lid = 0;
        const fgColor = 0x00ff00;
        this._setup(sphereCount, sphereRadius, fgColor);
    }


    _setup(sphereCount, sphereRadius, fgColor){

        const geometry = new SphereGeometry( sphereRadius, 32, 16 );
        const material = new MeshBasicMaterial( { color: fgColor } );

        for (let count = 0; count < sphereCount; count++){
            const sphere = new Mesh(geometry, material)

            sphere.position.x = count;
            this.add(sphere)
            this._log("spheres-sphere", count);
        }
    }

    /**
     * Interface to allow arena to be animated.
     * 
     * @param {number} delta - time interval since last tick
     */
    tick(delta){
        if (this.startTime === undefined){
            this.rotation.y = (this.rotation.y + delta * this.rotateRadHz) % (2*Math.PI);
            this._log('panels-tick-rotation', this.rotation.y);
        } else {
            const c_time = Date.now()/1000;
            this.rotation.y = Math.sin((c_time - this.startTime) * this.osc_hz * (2*Math.PI)) * this.max_deg;
            this._log('panels-tick-rotation', this.rotation.y);
        }
    }


    /**
     * Set the Loop ID
     * 
     * @param {bigint} lid - Loop ID
     */
    setLid(lid){
        this._log('panels-set-lid-old', lid);
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