import { Group, MathUtils, CylinderGeometry, MeshBasicMaterial, Mesh, BackSide } from '/static/vendor/three.module.js';

/**
 * Definition of the panels that form a cylindrical arena.
 */

class Mask extends Group {

    /**
     * Representation of the panels in a virtual fly arena.
     * 
     * @constructor
     * @param {number} panelAngle - width of a single panel in radians
     * @param {number} intervalAngle - width of the interval between panels in radians
     * @param {number} arenaRadius - radius of the arena in m (default: 0.1525m; same as G4 arena)
     * @param {number} arenaHeight - height of the arena in m (default: 0.8m)
     */
    constructor(maskStart, maskEnd, arenaRadius=0.1525, arenaHeight=0.8) {
        super();
        this.loggable = null;
        this.lid = 0;
        this.maskRadius = arenaRadius-0.001;
        this.maskHeight = arenaHeight;
        const bgColor = 0x000000;
        this._setup(maskStart, maskEnd, bgColor);
    }

    /**
     * (private) Method to set up the arena with a specific panel and interval angle.
     * 
     * @param {number} panelAngle - width of a panel in radians
     * @param {number} intervalAngle - width of an interval between panels in radians
     */
    _setup(maskStart, maskEnd, maskColor){
        const cylinderHorizSegments = 12;

        this._log('panels-mask-color', maskColor);
        if (maskStart != maskEnd){
            const maskGeometry = new CylinderGeometry(
                this.maskRadius, this.maskRadius,
                this.maskHeight,
                cylinderHorizSegments, 1,
                true,
                maskStart, maskEnd-maskStart);
            const maskMaterial = new MeshBasicMaterial( { color: maskColor, side:BackSide});
            const mask = new Mesh(maskGeometry, maskMaterial);
            this.add(mask);
            this._log('panels-add-mask-start', maskStart);
            this._log('panels-add-mask-end', maskEnd);
            this._log('panels-add-mask-color', maskColor);
        }
    }

    /**
     * Interface to change the panel setup, specifically the bar and interval sizes
     * 
     * @param {number} panelAngle - width of the panel in radians
     * @param {number} intervalAngle  - width of interval between panels in radians
     */
    changeMask(maskStart, maskEnd, bgColor) {
        this.clear();
        this._log('mask-change-clear')
        this._setup(maskStart, maskEnd, bgColor);
    }

    /**
     * Set the rotational speed of the camera (in radians)
     * 
     * @param {number} rotateRadHz - rotational speed of the camera in radians per second, positive
     *      is clockwise
     */
    setRotateRadHz(rotateRadHz){
        this.rotateRadHz = rotateRadHz;
        this._log('mask-set-rotateRadHz', rotateRadHz);
    }

    /**
    * Set the rotational speed of the camera (in degree)
    * 
    * @param {number} rotate_deg_hz - rotational speed of he camera in degree per second, 
    *      positive is clockwise
    */
    setRotateDegHz(rotate_deg_hz){
        this.rotateRadHz = MathUtils.degToRad(rotate_deg_hz);
        this._log('mask-set-rotate_deg_hz', rotate_deg_hz);
    }


    /**
     * Interface to allow arena to be animated.
     * 
     * @param {number} delta - time interval since last tick
     */
    tick(delta){
        this.rotation.y = (this.rotation.y + delta * this.rotateRadHz) % (2*Math.PI);
        this._log('mask-tick-rotation', this.rotation.y);
    }

    /**
     * Set the Loop ID
     * 
     * @param {bigint} lid - Loop ID
     */
    setLid(lid){
        this._log('mask-set-lid-old', lid);
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

export { Mask };