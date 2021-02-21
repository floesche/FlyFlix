import { RotatingCamera } from './RotatingCamera.js';

function createCamera() {
    const camera = new RotatingCamera(
        120,                                        // fov
        window.innerWidth / window.innerHeight,     // aspect ratio
        0.01,                                       // near clipping
        2                                           // far clipping
    );
    return camera;
}

export { createCamera };
