import { Group, MathUtils, PlaneBufferGeometry, CylinderBufferGeometry, MeshBasicMaterial, Mesh, BackSide } from '/static/vendor/three.module.js';




class Panels extends Group {
    constructor(panelAngle, intervalAngle, arenaRadius=0.1525, arenaHeight=0.8) {
        super();

        this.arenaRadius = arenaRadius;
        this.arenaHeight = arenaHeight;

        this._setup(panelAngle, intervalAngle);

    }

    _setup(panelAngle, intervalAngle){
        const geometry = new CylinderBufferGeometry(this.arenaRadius, this.arenaRadius,this.arenaHeight, 12, 1, true, 0, MathUtils.degToRad(panelAngle))
        const material = new MeshBasicMaterial({ color: 0x00ff00, side:BackSide });

        for (let alpha = 0; alpha < 360; alpha += panelAngle + intervalAngle) {
            const bar = new Mesh(geometry, material);
            bar.rotation.y = MathUtils.degToRad(alpha);
            this.add(bar);
        }
    }

    changePanels(panelAngle, intervalAngle) {
        this.clear();
        this._setup(panelAngle, intervalAngle);
    }

    tick(delta){}
}

export { Panels };