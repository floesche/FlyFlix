// import { Loop } from "./Loop.js";


class DataExchanger{
    constructor(camera, loop, panels){

        this.socket = io("http://localhost:17000");
        this.lid = 0;

        // this.socket.emit('start-experiment', 1);
        

        this.socket.onAny((event, ...args) => {
            console.log(event, args);
          });

        this.socket.on('disconnect', () => {
            const endEvent = new Event('end-experiment');
            camera.setRotateRadHz(0);
            window.dispatchEvent(endEvent);
        });

        this.socket.on('speed', (lid, speed) => {
            this.lid = lid;
            camera.setRotateRadHz(speed);
        });

        this.socket.on('rotate-to', (lid, targetRotationRad) => {
            this.lid = lid;
            camera.setRotationRad(targetRotationRad);
        })

        this.socket.on('fps', (lid, fps) => {
            this.lid = lid;
            loop.setFPS(fps);
        });

        this.socket.on('spatial-setup', (lid, barWidth, spaceWidth) => {
            this.lid = lid;
            this.log('changerequest-barwidth', barWidth);
            panels.changePanels(barWidth, spaceWidth);
        });

    }

    log(key, value){
        this.socket.emit('dl', performance.now(), this.lid, key, value);
    }

}



export { DataExchanger };