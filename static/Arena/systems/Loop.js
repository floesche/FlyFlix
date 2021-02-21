import { Clock } from '/static/vendor/three.module.js';

const clock = new Clock();

class Loop {
    constructor(camera, scene, renderer) {
        this.camera = camera;
        this.scene = scene;
        this.renderer = renderer;
        this.updateables = [];
        this.interval = 1/60;
        this.rdelta = clock.getDelta();
    }

    start() {
        this.renderer.setAnimationLoop(() => {
            this.tick();
            if( this.rdelta > this.interval){
                this.renderer.render(this.scene, this.camera);
                this.rdelta = this.rdelta % this.interval;
            }
        }

        );
    }

    stop() {
        this.renderer.setAnimationLoop(null);
    }

    tick() {
        const delta = clock.getDelta();
        this.rdelta += delta;
        for(const object of this.updateables) {
            object.tick(delta);
        }
    }

    setFPS(fps) {
        this.interval = 1/fps;
    }
}

export { Loop };