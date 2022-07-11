import { Group, MathUtils, PlaneBufferGeometry, CylinderBufferGeometry, MeshBasicMaterial, Mesh, BackSide } from '/static/vendor/three.module.js';

/**
 * Definition of the panels that form a cylindrical arena.
 */

class Panels extends Group {

    /**
     * Representation of the panels in a virtual fly arena.
     * 
     * @constructor
     * @param {number} panelAngle - width of a single panel in radians
     * @param {number} intervalAngle - width of the interval between panels in radians
     * @param {number} arenaRadius - radius of the arena in m (default: 0.1525m; same as G4 arena)
     * @param {number} arenaHeight - height of the arena in m (default: 0.8m)
     */
    constructor(panelAngle, intervalAngle, arenaRadius=0.1525, arenaHeight=0.8) {
        super();
        this.loggable = null;
        this.lid = 0;
        this.arenaRadius = arenaRadius;
        this.arenaHeight = arenaHeight;
        this.rotateRadHz = 0;
        this.startTime = undefined;
        const fgColor = 0x00ff00;
        const bgColor = 0x000000;
        this._setup(panelAngle, intervalAngle, fgColor, bgColor, arenaHeight);
    }

    /**
     * (private) Method to set up the arena with a specific panel and interval angle.
     * 
     * @param {number} panelAngle - width of a panel in radians
     * @param {number} intervalAngle - width of an interval between panels in radians
     */
    _setup(panelAngle, intervalAngle, fgColor, bgColor, arenaHeight){
        
        const cylinderHorizSegments = 12;
        
        this._log('panels-panel-angle', panelAngle);
        this._log('panels-interval-angle', intervalAngle);
        this._log('panels-arena-radius', this.arenaRadius);
        this._log('panels-arena-height', arenaHeight);
        this._log('panels-type', 'CylinderBufferGeometry');
        this._log('panels-horizontal-segments', cylinderHorizSegments);
        this._log('panels-bar-color', fgColor);

        const geometry = new CylinderBufferGeometry(
            this.arenaRadius, this.arenaRadius,
            arenaHeight, 
            cylinderHorizSegments, 1, 
            true, // TODO Test with "false" instead of "true" to have it openEnded
            0, panelAngle);

        const material = new MeshBasicMaterial({ color: fgColor, side:BackSide });

        for (let alpha = 0; alpha < 2*Math.PI; alpha += panelAngle + intervalAngle) {
            const bar = new Mesh(geometry, material);
            // bar.rotation.y = MathUtils.degToRad(alpha);
            bar.rotation.y = alpha;
            this.add(bar);
            this._log('panels-bar', alpha);
        }
    }

    /**
     * Interface to change the panel setup, specifically the bar and interval sizes
     * 
     * @param {number} panelAngle - width of the panel in radians
     * @param {number} intervalAngle  - width of interval between panels in radians
     */
    changePanels(panelAngle, intervalAngle, fgColor, bgColor, barHeight) {
        this.clear();
        this._log('panels-change-clear');
        this._log('xxxx',barHeight )
        this._setup(panelAngle, intervalAngle, fgColor, bgColor, barHeight);
    }

    /**
     * Set the rotational speed of the panels (in radians)
     * 
     * @param {number} rotateRadHz - rotational speed of the panels in radians per second, positive
     *      is clockwise
     */
    setRotateRadHz(rotateRadHz){
        this.rotateRadHz = rotateRadHz;
        this._log('panels-set-rotateRadHz', rotateRadHz);
    }

    /**
    * Set the rotational speed of the panels (in degree)
    * 
    * @param {number} rotate_deg_hz - rotational speed of he panels in degree per second, 
    *      positive is clockwise
    */
    setRotateDegHz(rotate_deg_hz){
        this.rotateRadHz = MathUtils.degToRad(rotate_deg_hz);
        this._log('panels-set-rotate_deg_hz', rotate_deg_hz);
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
     * Rotate the panels to an absolute angle.
     * 
     * @param {number} rotation - set the absolute rotation of the camera in radians
     */
    setRotationRad(rotation){
        this.rotation.y = rotation % (2*Math.PI);
        this._log('panels-set-rotationRad', rotation);
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

export { Panels };