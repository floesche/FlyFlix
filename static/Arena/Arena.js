import { createCamera } from './components/camera.js';
import { createScene } from './components/scene.js';

import { Panels } from './components/Panels.js';

import { createRenderer } from './systems/renderer.js';
import { Resizer } from './systems/Resizer.js';
import { Loop } from './systems/Loop.js';

import { DataExchanger } from './systems/DataExchanger.js';

let camera;
let renderer;
let scene;
let loop;

let io;


class Arena {
    constructor(container) {
        camera = createCamera();
        scene = createScene();
        renderer = createRenderer();
        
        loop = new Loop(camera, scene, renderer);
        loop.updateables.push(camera);

        container.append(renderer.domElement);

        const panels = new Panels(10, 170);
        scene.add(panels);

        io = new DataExchanger(camera, loop, panels);

        camera.loggable = io;
        loop.loggable = io;
        panels.loggable = io;

        const resizer = new Resizer(container, camera, renderer);
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