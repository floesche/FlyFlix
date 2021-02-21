import { Group, MathUtils, PlaneBufferGeometry, MeshBasicMaterial, Mesh, BackSide } from '/static/vendor/three.module.js';




class Panels extends Group {
    constructor(panelAngle, intervalAngle, arenaRadius=0.1525, arenaHeight=0.8) {
        super();

        this.arenaRadius = arenaRadius;
        this.arenaHeight = arenaHeight;

        const panelWidth = Math.atan(MathUtils.degToRad(panelAngle / 2)) * arenaRadius * 2;//Math.atan((angle / 2) * Math.PI / 180) * radius * 2;

        const geometry = new PlaneBufferGeometry(panelWidth, arenaHeight)
        const material = new MeshBasicMaterial({ color: 0x00ff00, side:BackSide });

        for (let alpha = 0; alpha < 360; alpha += panelAngle + intervalAngle) {
            const bar = new Mesh(geometry, material);
            bar.rotation.y = MathUtils.degToRad(alpha);

            bar.position.x = Math.sin(MathUtils.degToRad(alpha)) * arenaRadius;
            bar.position.z = Math.cos(MathUtils.degToRad(alpha)) * arenaRadius;

            this.add(bar);
        }

    }

    update(panelAngle, intervalAngle) {
        this.clear();
    }

    tick(delta){}
}

export { Panels };