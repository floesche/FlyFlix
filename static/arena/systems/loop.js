import { Clock } from '/static/vendor/three.module.js';

const clock = new Clock();

/**
 * A Loop module to handle looping logic and the animation system.
 * 
 * inspired by https://discoverthreejs.com/book/first-steps/animation-loop/
 */
class Loop {

    /**
     * Loop class to handle the looping logic. Add any object that needs animation and has 
     *      a `tick()` method to the `updateables` array. 
     * 
     * @constructor
     * @param {Camera} camera - Camera object to be animated
     * @param {Scene} scene - scene to be animated
     * @param {Renderer} renderer - renderer where the scene and camera are going to be animated
     */
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

    /**
     * Start the animation
     */
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

    /**
     * Stop the animation.
     */
    stop() {
        this.renderer.setAnimationLoop(null);
    }

    /**
     * Advance the animation by one tick by calling the `tick()` method from each object in the 
     *      `updateables` array.
     */
    tick() {
        const delta = clock.getDelta();
        this.rdelta += delta;
        this._log('loop-tick-delta', delta);
        for(const object of this.updateables) {
            object.tick(delta);
        }
    }

    /**
     * Set the Loop ID.
     * 
     * @param {bigint} lid - Loop ID
     */
    setLid(lid){
        this._log('loop-set-lid-old', this.lid);
        this.lid = lid;
    }

    /**
     * Set the frame rate of the system.
     * 
     * @param {number} fps - frame rate in frames per second 
     */
    setFPS(fps) {
        this.interval = 1/fps;
        this._log('loop-set-fps', fps);
    }

    /**
     * (private) interface to log values
     * 
     * @param {string} key - key of key-value pair to be logged
     * @param {string} value - value of key-value pair to be logged
     */
    _log(key, value){
        if (this.loggable){
            this.loggable.log(this.lid, key, value);
        }
    }

}

export { Loop };