// import { Loop } from "./Loop.js";


class DataExchanger{
    constructor(camera, loop, panels){

        const socket = io("http://localhost:17000");

        socket.emit('start-experiment', 1);
        console.log("sent start");

        socket.onAny((event, ...args) => {
            console.log(event, args);
          });

        socket.on('speed', (id, speed) => {
            camera.setRotateRadHz(speed);
        });

        socket.on('rotate-to', (id, targetRotationRad) => {
            camera.setRotationRad(targetRotationRad);
        })

        socket.on('fps', (id, fps) => {
            loop.setFPS(fps);
        });

        socket.on('spatial-setup', (id, barWidth, spaceWidth) => {
            panels.update(barWidth, spaceWidth);
        });

    }

}



export { DataExchanger };