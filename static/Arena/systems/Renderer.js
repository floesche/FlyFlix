import { WebGLRenderer } from '/static/vendor/three.module.js';


/**
 * Module to create a renderer.
 * 
 * Inspired by https://discoverthreejs.com/book/first-steps/world-app/
 * 
 * @returns {WebGLRenderer} - Renderer available to client
 */
function createRenderer() {
    const renderer = new WebGLRenderer();

    return renderer;
}

export { createRenderer };