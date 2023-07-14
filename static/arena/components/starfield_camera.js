import { PerspectiveCamera } from '/static/vendor/three.module.js';

/**
 * Camera creation module. 
 * 
 * Inspired by https://discoverthreejs.com/book/first-steps/world-app/
 * 
 * @returns {Camera}
 */

function createStarfieldCamera(orientation=0) {
    const camera = new PerspectiveCamera(
        90,                                         // fov. According to measurements with the Fire tablet, this is closest to true angles at a distance of around 35mm between fly and display.
        window.innerWidth / window.innerHeight,     // aspect ratio
        0.001,                                       // near clipping
        10000,                                        // far clipping
        orientation
    );
    return camera;
}

export { createStarfieldCamera };
