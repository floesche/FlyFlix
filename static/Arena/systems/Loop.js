import { Clock } from '/static/vendor/three.module.js';

const clock = new Clock();

class Loop {
    constructor(camera, scene, renderer) {
        this.camera = camera;
        this.scene = scene;
        this.renderer = renderer;
        this.updateables = [];
    }

    start() {
        this.renderer.setAnimationLoop(() => {
            this.tick();
            this.renderer.render(this.scene, this.camera);
        }

        );
    }

    stop() {
        this.renderer.setAnimationLoop(null);
    }

    tick() {
        const delta = clock.getDelta();

        for(const object of this.updateables) {
            object.tick(delta);
        }
    }
}

export { Loop };