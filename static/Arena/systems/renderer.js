import { WebGLRenderer } from '/static/vendor/three.module.js';

function createRenderer() {
    const renderer = new WebGLRenderer();

    return renderer;
}

export { createRenderer };