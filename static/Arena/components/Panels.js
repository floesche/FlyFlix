import { Group, MathUtils, PlaneBufferGeometry, CylinderBufferGeometry, MeshBasicMaterial, Mesh, BackSide } from '/static/vendor/three.module.js';

class Panels extends Group {
    constructor(panelAngle, intervalAngle, arenaRadius=0.1525, arenaHeight=0.8) {
        super();

        this.loggable = null;
        this.lid = 0;

        this.arenaRadius = arenaRadius;
        this.arenaHeight = arenaHeight;

        this._setup(panelAngle, intervalAngle);
    }

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

        // const geometry = new CylinderBufferGeometry(this.arenaRadius, this.arenaRadius,this.arenaHeight, cylinderHorizSegments, 1, true, 0, MathUtils.degToRad(panelAngle))
        const geometry = new CylinderBufferGeometry(this.arenaRadius, this.arenaRadius,this.arenaHeight, cylinderHorizSegments, 1, true, 0, panelAngle)
        const material = new MeshBasicMaterial({ color: barcolor, side:BackSide });

        for (let alpha = 0; alpha < 2*Math.PI; alpha += panelAngle + intervalAngle) {
            const bar = new Mesh(geometry, material);
            // bar.rotation.y = MathUtils.degToRad(alpha);
            bar.rotation.y = alpha;
            this.add(bar);
            this._log('panels-bar', alpha);
        }
    }

    changePanels(panelAngle, intervalAngle) {
        this.clear();
        this._log('panels-change-clear')
        this._setup(panelAngle, intervalAngle);
    }

    tick(delta){}

    setLid(lid){
        this._log('panels-set-lid-old', this.lid);
        this.lid = lid;
    }

    _log(key, value){
        if (this.loggable){
            this.loggable.log(this.lid, key, value);
        }
    }

}

export { Panels };