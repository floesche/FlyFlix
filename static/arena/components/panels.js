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
        this._setup(panelAngle, intervalAngle);
    }

    /**
     * (private) Method to set up the arena with a specific panel and interval angle.
     * 
     * @param {number} panelAngle - width of a panel in radians
     * @param {number} intervalAngle - width of an interval between panels in radians
     */
    _setup(panelAngle, intervalAngle){
        const barcolor = 0x00ff00;
        const cylinderHorizSegments = 12;
        
        this._log('panels-panel-angle', panelAngle);
        this._log('panels-interval-angle', intervalAngle);
        this._log('panels-arena-radius', this.arenaRadius);
        this._log('panels-arena-height', this.arenaHeight);
        this._log('panels-type', 'CylinderBufferGeometry');
        this._log('panels-horizontal-segments', cylinderHorizSegments);
        this._log('panels-bar-color', barcolor);

        const geometry = new CylinderBufferGeometry(
            this.arenaRadius, this.arenaRadius,
            this.arenaHeight, 
            cylinderHorizSegments, 1, 
            true, // TODO Test with "false" instead of "true" to have it openEnded
            0, panelAngle);

        const material = new MeshBasicMaterial({ color: barcolor, side:BackSide });

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
    changePanels(panelAngle, intervalAngle) {
        this.clear();
        this._log('panels-change-clear')
        this._setup(panelAngle, intervalAngle);
    }

    /**
     * Interface to allow arena to be animated.
     * 
     * @param {number} delta - time interval since last tick
     */
    tick(delta){}

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