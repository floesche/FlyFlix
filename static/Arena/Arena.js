import { createCamera } from './components/camera.js';
import { createCube } from './components/environment.js';
import { createScene } from './components/scene.js';

import { createRenderer } from './systems/renderer.js';
import { Resizer } from './systems/Resizer.js';
import { Loop } from './systems/Loop.js';

let camera;
let renderer;
let scene;
let loop;


class Arena {
    constructor(container) {
        camera = createCamera();
        scene = createScene();
        renderer = createRenderer();
        
        loop = new Loop(camera, scene, renderer);
        loop.updateables.push(camera);

        container.append(renderer.domElement);

        const cube = createCube();
        scene.add(cube);

        const resizer = new Resizer(container, camera, renderer);
        // resizer.onResize = () => { this.render(); }
    }

    render() {
        renderer.render(scene, camera);
    }

    start() {
        loop.start();
    }

    stop() {
        loop.stop();
    }
}

export { Arena };