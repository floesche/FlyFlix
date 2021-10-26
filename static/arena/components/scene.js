import { Scene } from '/static/vendor/three.module.js';

/**
 * Scene creation module.
 * 
 * Inspired by https://discoverthreejs.com/book/first-steps/world-app/
 * 
 * @returns {Scene}
 */
function createScene() {
    const scene = new Scene();
    return scene;
}

export { createScene };