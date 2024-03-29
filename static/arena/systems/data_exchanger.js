/**
 * Module to exchange data between server and client. This is FlyFlix specific.
 */
import { Color, MathUtils } from '/static/vendor/three.module.js';
class DataExchanger{

    /**
     * FlyFlix specific module for data exchange between server and client.
     * 
     * @param {Camera} camera - The camera used in the scene
     * @param {Scene} scene
     * @param {Loop} loop - The animation loop
     * @param {Panels} panels - the group of panels
     */
    constructor(camera, scene, loop, panels, masks){

        // The data exchanger connects to a Socket IO at port 17000
        const socketurl = window.location.hostname + ":17000";
        this.socket = io(socketurl);
        this.isLogging = false;

        const mr = MathUtils.degToRad(35);

        /**
         * Event handler for `disconnect` sends the event `end-experiment` and stops camera 
         *      and panels rotation.
         */
        this.socket.on('disconnect', () => {
            const endEvent = new Event('end-experiment');
            panels.setRotateRadHz(0);
            camera.setRotateRadHz(0);
            window.dispatchEvent(endEvent);
        });

        this.socket.on('experiment-started', () =>{
            const startExperiment = new Event('experiment-started');
            window.dispatchEvent(startExperiment);
        });

        /**
         * Event handler for `speed` sets rotational speed and loop ID for the panels object.
         * 
         * @param {bigint} lid - Loop ID
         * @param {number} speed - set rotational speed for panels in radians per second
         */
        this.socket.on('speed', (lid, speed) => {
            panels.setLid(lid);
            panels.setRotateRadHz(speed);
            this.log(lid, 'de-panel-speed', speed);
        });

        this.socket.on('oscillation', (lid, osc_freq, osc_width) => {
            panels.setLid(lid);
            panels.setOscillation(osc_freq, osc_width);
            this.log(lid, 'de-panels-oscillation', osc_freq);
        });

        /**
         * Event handler for `ssync` returns `csync` message with current client time stamp and 
         *      loop id
         * 
         * @param {bigint} lid - Loop ID
         */
        this.socket.on('ssync', (lid) => {
            this.socket.emit('csync', performance.now(), lid, 'de-sync');
        });

        /**
         * Event handler for `rotate-to` message to rotate a panels object to a target rotation.
         * 
         * @param {bigint} lid - Loop ID
         * @param {number} targetRotationRad - target rotation in radians
         */
        this.socket.on('rotate-to', (lid, targetRotationRad) => {
            panels.setLid(lid);
            panels.setRotationRad(targetRotationRad);
            this.log(lid, 'de-rotate-panel-to', targetRotationRad);
        })


        this.socket.on('camera-flip', (lid, updown) => {
            camera.flipUpDown(updown);
            this.log(lid, 'de-flip-camera-updown', updown);
        }
        )

        /**
         * Event handler for `fps` message to set the target frame rate.
         * 
         * @param {bigint} lid - Loop ID
         * @param {number} fps - target client frame rate
         */
        this.socket.on('fps', (lid, fps) => {
            loop.setLid(lid);
            loop.setFPS(fps);
            this.log(lid, 'de-fps', fps);
        });

        /**
         * Event handler for `spatial-setup` message. The cylindrical arena consists of vertical bars interleaved with spaces. All bars have the same width as all intervals do. The bars and spaces are repeated until the fill cylinder is filled. To have an arena with four bars spanning one eighth of the cylinder, barWidth and spaceWidth could both be defined as pi/4. To have a single bright bar that spans a quarter of an arena, barWidth could be pi/2 and spaceWidth pi*3/2.
         * 
         * @param {bigint} lid -Loop ID
         * @param {number} barWidth - bar width in radians
         * @param {number} spaceWidth - interval width between bars in radians
         */
        this.socket.on('spatial-setup', (lid, barWidth, spaceWidth, maskStart, maskEnd, fgColor, bgColor, barHeight) => {
            panels.setLid(lid);
            panels.changePanels(barWidth, spaceWidth, fgColor, bgColor, barHeight);
            //scene.changeBgColor(bgColor);
            scene.background = new Color(bgColor);
            masks.setLid(lid);
            masks.changeMask(maskStart+mr, maskEnd+mr, bgColor);
            this.log(lid, 'de-spatial-setup-bar', barWidth);
            this.log(lid, 'de-spatial-setup-space', spaceWidth);
            this.log(lid, 'de-spatial-setup-mask-start', maskStart);
            this.log(lid, 'de-spatial-setup-mask-end', maskEnd);
            this.log(lid, 'de-spatial-setup-fgcolor', fgColor);
            this.log(lid, 'de-spatial-setup-bgcolor', bgColor);
            this.log(lid, 'de-spatial-setup-barheight', barHeight);
        });

        /**
         * Event handler for `meta`. The key and value will be logged.
         * 
         * @param {bigint} lid - Loop ID
         * @param {string} key - key of key-value-pair
         * @param {string} value - value of key-value-pair
         */
        this.socket.on('meta', (lid, key, value) => {
            this.log(lid, key, value);
        })

        /**
         * Local HTML event listener for click on `start-experiment` button which will emit the 
         *      socket message `start-experiment`.
         */
        window.addEventListener('start-experiment', () => {
            this.isLogging = true;
            this.socket.emit('start-experiment', 1);
            this.log(0, 'de-start-experiment');
        });

    }

    /**
     * Log client on the server by sending a `dl` message with the current client timestamp, lid, 
     *      key, and value.
     * 
     * @param {bigint} lid - Loop ID
     * @param {string} key - key of key-value-pair
     * @param {string} value - value of key-value-pair
     */
    log(lid, key, value){
        if (this.isLogging){
            this.socket.emit('dl', performance.now(), lid, key, value);
        }
    }
}

export { DataExchanger };