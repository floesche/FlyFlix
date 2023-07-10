import { PerspectiveCamera, MathUtils } from '/static/vendor/three.module.js';

/**
 * Representation of the camera at the virtual fly position within the arena.
 */
class RotatingCamera extends PerspectiveCamera {
    /**
     * Representation of camera at virtual fly position. Inherits from PerspectiveCamera
     * 
     * @param {number} fov - field of view
     * @param {number} aspectRatio - camera's ratio of width over height
     * @param {number} nearClip - distance of plane where everything closer is going to be clipped
     * @param {number} farClip - distance of plane where everything farther away is going to be
     *      clipped
     * @param {number} defaultAngle - default angle in degree where camera is facing
     * @param {number} startOffset - offset in addition to starting angle in degree
     * @param {number} rotationAnglePerSecond - rotation of camera in degree per second, positive
     *      is clockwise
     */
    constructor(fov, aspectRatio, nearClip, farClip, defaultAngle = 0, startOffset = 0, rotationAnglePerSecond = 0){
        super(fov, aspectRatio, nearClip, farClip);
        this.defaultAngle = defaultAngle;
        this.offset = startOffset;
        this.rotateRadHz = rotationAnglePerSecond;

        this.loggable = null;
        this.lid = 0;

        this.rotation.y = MathUtils.degToRad(defaultAngle + startOffset);
        //this.position.z = -0.07;
    }

    /**
     * Animate camera rotation
     * 
     * @param {number} delta - time difference since last tick
     */
    tick(delta) {
        this.rotation.y = (this.rotation.y + delta * this.rotateRadHz) % (2*Math.PI);
        this._log('camera-tick-rotation', this.rotation.y);
    }

    /**
     * Set the rotational speed of the camera (in radians)
     * 
     * @param {number} rotateRadHz - rotational speed of the camera in radians per second, positive
     *      is clockwise
     */
    setRotateRadHz(rotateRadHz){
        this.rotateRadHz = rotateRadHz;
        this._log('camera-set-rotateRadHz', rotateRadHz);
    }

    /**
     * Set the rotational speed of the camera (in degree)
     * 
     * @param {number} rotate_deg_hz - rotational speed of he camera in degree per second, 
     *      positive is clockwise
     */
    setRotateDegHz(rotate_deg_hz){
        this.rotateRadHz = MathUtils.degToRad(rotate_deg_hz);
        this._log('camera-set-rotate_deg_hz', rotate_deg_hz);
    }

    /**
     * Rotate the camera to an absolute angle.
     * 
     * @param {number} rotation - set the absolute rotation of the camera in radians
     */
    setRotationRad(rotation){
        this.rotation.y = rotation % (2*Math.PI);
        this._log('camera-set-rotationRad', rotation);
    }

    /**
     * Set the Loop ID.
     * 
     * @param {bigint} lid - Loop ID
     */
    setLid(lid){
        this._log('camera-set-lid-old', lid);
        this.lid = lid;
        
    }

    /**
     * Flip the camera on its side. The movement then appears to be up/down instead of left/right.
     * 
     * @param {boolean} updown - flip camera on its side?
     */
    flipUpDown(updown){
        if (updown) {
            this.rotation.z = 0.5*Math.PI;
        } else {
            this.rotation.z = 0;
        }
    }

    /**
     * (private) Log key-value pair to any element that is listed in the loggable array.
     * 
     * @param {string} key - key in key-value pair to be logged
     * @param {string} value - value in key-value pair to be logged
     */
    _log(key, value){
        if (this.loggable){
            this.loggable.log(this.lid, key, value);
        }
    }
}

export { RotatingCamera };