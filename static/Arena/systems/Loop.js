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

        this.lid = 0;
        this.loggable = null;
    }

    start() {
        this.renderer.setAnimationLoop(() => {
            this.tick();
            if( this.rdelta > this.interval){
                this.renderer.render(this.scene, this.camera);
                this.rdelta = this.rdelta % this.interval;
                this._log('loop-render', this.rdelta);
            } else {
                this._log('loop-skip', this.rdelta);
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
        this._log('loop-tick-delta', delta);
        for(const object of this.updateables) {
            object.tick(delta);
        }
    }

    setLid(lid){
        this._log('loop-set-lid-old', this.lid);
        this.lid = lid;
    }

    setFPS(fps) {
        this.interval = 1/fps;
        this._log('loop-set-fps', fps);
    }

    _log(key, value){
        if (this.loggable){
            this.loggable.log(this.lid, key, value);
        }
    }

}

export { Loop };