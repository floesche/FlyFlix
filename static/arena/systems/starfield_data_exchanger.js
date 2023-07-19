/**
 * Module to exchange data between server and client. This is FlyFlix specific.
 * Only for starfield trials
 */
import { Color, MathUtils } from '/static/vendor/three.module.js';
class StarfieldDataExchanger{
    /**
     * FlyFlix specific module for data exchange between server and client.
     * 
     * @param {Camera} camera - The camera used in the scene
     * @param {Scene} scene
     * @param {Loop} loop - The animation loop
     * @param {Spheres} spheres - the group of spheres
     */
    constructor(camera, scene, loop, spheres){

        // The data exchanger connects to a Socket IO at port 17000
        const socketurl = window.location.hostname + ":17000";
        this.socket = io(socketurl);
        this.isLogging = false;

        /**
         * Event handler for `disconnect` sends the event `end-experiment` and stops camera 
         *      and spheres rotation.
         */
        this.socket.on('disconnect', () => {
            const endEvent = new Event('end-experiment');
            spheres.setRotateRadHz(0);
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
         * @param {number} speed - set rotational speed for spheres in radians per second
         */
        this.socket.on('star-speed', (lid, speed) => {
            spheres.setLid(lid);
            spheres.setRotateRadHz(speed);
            this.log(lid, 'de-sphere-speed', speed);
        });

        this.socket.on('star-oscillation', (lid, osc_freq, osc_width) => {
            spheres.setLid(lid);
            spheres.setOscillation(osc_freq, osc_width);
            this.log(lid, 'de-spheres-oscillation', osc_freq);
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
         * Event handler for `rotate-to` message to rotate a spheres object to a target rotation.
         * 
         * @param {bigint} lid - Loop ID
         * @param {number} targetRotationRad - target rotation in radians
         */
        this.socket.on('rotate-to', (lid, targetRotationRad) => {
            spheres.setLid(lid);
            spheres.setRotationRad(targetRotationRad);
            this.log(lid, 'de-rotate-spheres-to', targetRotationRad);
        })

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
         * Event handler for `spatial-setup` message. The spherical arena consists of spheres. 
         * Spheres have different radii depending on their position due to distortion.
         * 
         * @param {bigint} lid -Loop ID
         * Interface to change the sphere setup
         * @param {number} sphereCount - the amount of total spheres surrounding the fly
         * @param {number} sphereRadius - the radius of the spheres in the starfield
         * @param {number} shellRadius - the radius of the shell / distance between camera and spheres
         * @param {color} color - color of the spheres (default is green)
        */
        this.socket.on('star-spatial-setup', (lid, sphereCount, sphereRadius, shellRadius, seed, positionList, color) => {
            var positions = JSON.parse(positionList)
            spheres.setLid(lid);
            spheres.changeSpheres(sphereCount, sphereRadius, shellRadius, seed, positions, color);
            this.log(lid, 'de-spatial-setup-sphereCount', sphereCount);
            this.log(lid, 'de-spatial-setup-color', color);
            this.log(lid, 'de-spatial-setup-sphereRadius', sphereRadius);
            this.log(lid, 'de-spatial-setup-shellRadius', shellRadius);
            this.log(lid, 'de-spatial-setup-seed', seed)
            loop.start();
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
export { StarfieldDataExchanger };