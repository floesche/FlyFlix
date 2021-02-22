class DataExchanger{
    constructor(camera, loop, panels){

        const socketurl = window.location.hostname + ":17000";
        this.socket = io(socketurl);
        this.isLogging = false;

        this.socket.onAny((event, ...args) => {
            console.log(event, args);
          });

        this.socket.on('disconnect', () => {
            const endEvent = new Event('end-experiment');
            camera.setRotateRadHz(0);
            window.dispatchEvent(endEvent);
        });

        this.socket.on('speed', (lid, speed) => {
            camera.setLid(lid);
            camera.setRotateRadHz(speed);
            this.log(lid, 'de-speed', speed);
        });

        this.socket.on('rotate-to', (lid, targetRotationRad) => {
            camera.setLid(lid);
            camera.setRotationRad(targetRotationRad);
            this.log(lid, 'de-rotate-to', targetRotationRad);
        })

        this.socket.on('fps', (lid, fps) => {
            loop.setLid(lid);
            loop.setFPS(fps);
            this.log(lid, 'de-fps', fps);
        });

        this.socket.on('spatial-setup', (lid, barWidth, spaceWidth) => {
            panels.setLid(lid);
            panels.changePanels(barWidth, spaceWidth);
            this.log(lid, 'de-spatial-setup-bar', barWidth);
            this.log(lid, 'de-spatial-setup-space', spaceWidth);
        });

        this.socket.on('meta', (lid, key, value) => {
            this.log(lid, key, value);
        })

        window.addEventListener('start-experiment', () => {
            this.isLogging = true;
            this.socket.emit('start-experiment', 1);
            this.log(0, 'de-start-experiment');
        });

    }

    log(lid, key, value){
        if (this.isLogging){
            this.socket.emit('dl', performance.now(), lid, key, value);
        }
    }

}



export { DataExchanger };