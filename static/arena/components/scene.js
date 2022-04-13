import { Scene, Color } from '/static/vendor/three.module.js';

/**
 * Scene creation module.
 * 
 * Inspired by https://discoverthreejs.com/book/first-steps/world-app/
 * 
 * @returns {Scene}
 */
function createScene() {
    const scene = new Scene();
    scene.background = new Color(0x0000FF);
    return scene;
}

export { createScene };