import { WebGLRenderer } from '/static/vendor/three.module.js';


/**
 * Create a renderer
 * 
 * @returns {WebGLRenderer} - Renderer available to client
 */
function createRenderer() {
    const renderer = new WebGLRenderer();

    return renderer;
}

export { createRenderer };