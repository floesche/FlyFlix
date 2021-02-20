import { PerspectiveCamera } from '/static/vendor/three.module.js';

function createCamera() {
    const camera = new PerspectiveCamera(
        120,                                        // fov
        window.innerWidth / window.innerHeight,     // aspect ratio
        1,                                          // near clipping
        120                                        // far clipping
    );

    camera.position.set(0, 0, 0);

    camera.tick = (delta) => {
        
        camera.rotation.y = (camera.rotation.y + delta) % (2* Math.PI);
        console.log(camera.rotation.y);
    }

    return camera;
}

export { createCamera };
