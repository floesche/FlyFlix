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

/**
 * Definition of the spheres that form a spherical shell
 */

class Spheres extends Group {

    /**
     * Representation of the panels in a virtual fly arena.
     * 
     * @constructor
     * @param {number} sphereCount - number of spheres
     * @param {number} sphereRadius - radius of the spheres in m
     * @param {number} shellRadius - radius of the spherical shell in m
     * 
     */
    constructor(sphereCount, sphereRadius, shellRadius) {
        super();
        this.loggable = null;
        this.lid = 0;
        this.sphereCount = sphereCount;
        this.sphereRadius = sphereRadius;
        this.shellRadius = shellRadius;
        this.rotateRadHz = 0;
        this.startTime = undefined;
        const sphereColor = 0x00ff00;
        this._setup(sphereCount, sphereRadius, shellRadius, sphereColor);
    }

    /**
     * (private) Method to set up the arena with a specific panel and interval angle.
     * 
     * @param {number} panelAngle - width of a panel in radians
     * @param {number} intervalAngle - width of an interval between panels in radians
     */
    _setup(sphereCount, sphereRadius, shellRadius, sphereColor){

        this._log('spheres-color', sphereColor);
        const geometry = new SphereGeometry( sphereRadius, 32, 16 );
        const material = new MeshBasicMaterial( { color: sphereColor } );
        for ( let i=0; i<sphereCount; i++){
            let sphereMesh = new Mesh( geometry, material );
            let positions = randomSpherePoint(0,0,0, shellRadius);
            sphereMesh.position.x = positions[0];
            sphereMesh.position.y = positions[1];
            sphereMesh.position.z = positions[2];
            this.add(sphereMesh);
        }
    }

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


    /**
     * Interface to change the spheres setup, specifically the bar and interval sizes
     * 
     */
    changePanels(sphereCount, sphereRadius, shellRadius, sphereColor=0x00ff00) {
        this.clear();
        this._log('spheres-change-clear');
        this._setup(sphereCount, sphereRadius, shellRadius, sphereColor);
    }


    /**
     * Set the rotational speed of the spheres (in radians)
     * 
     * @param {number} rotateRadHz - rotational speed of the panels in radians per second, positive
     *      is upwards
     */
    setRotateRadHz(rotateRadHz){
        this.rotateRadHz = rotateRadHz;
        this._log('spheres-set-rotateRadHz', rotateRadHz);
    }

    /**
    * Set the rotational speed of the panels (in degree)
    * 
    * @param {number} rotate_deg_hz - rotational speed of he panels in degree per second, 
    *      positive is upwards
    */
    setRotateDegHz(rotate_deg_hz){
        this.rotateRadHz = MathUtils.degToRad(rotate_deg_hz);
        this._log('spheres-set-rotate_deg_hz', rotate_deg_hz);
    }


    /**
     * Interface to allow arena to be animated.
     * 
     * @param {number} delta - time interval since last tick
     */
    tick(delta){
        this.rotation.x = (this.rotation.x + delta * this.rotateRadHz) % (2*Math.PI);
        this._log('spheres-tick-rotation', this.rotation.y);
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