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
     * @param {number} nearClip - 
     * @param {*} farClip 
     * @param {*} defaultAngle 
     * @param {*} startOffset 
     * @param {*} rotationAnglePerSecond 
     */
    constructor(fov, aspectRatio, nearClip, farClip, defaultAngle = 0, startOffset = 0, rotationAnglePerSecond = 0){
        super(fov, aspectRatio, nearClip, farClip);
        this.defaultAngle = defaultAngle;
        this.offset = startOffset;
        this.rotateRadHz = rotationAnglePerSecond;
        
        this.loggable = null;
        this.lid = 0;

        this.rotation.y = MathUtils.degToRad(defaultAngle + startOffset);
    }

    tick(delta) {
        this.rotation.y = (this.rotation.y + delta * this.rotateRadHz) % (2*Math.PI);
        this._log('camera-tick-rotation', this.rotation.y);
    }

    setRotateRadHz(rotateRadHz){
        this.rotateRadHz = rotateRadHz;
        this._log('camera-set-rotateRadHz', rotateRadHz);
    }

    setRotateDegHz(rotate_deg_hz){
        this.rotateRadHz = MathUtils.degToRad(rotate_deg_hz);
        this._log('camera-set-rotate_deg_hz', rotate_deg_hz);
    }

    setRotationRad(rotation){
        this.rotation.y = rotation % (2*Math.PI);
        this._log('camera-set-rotationRad', rotation);
    }

    setLid(lid){
        this._log('camera-set-lid-old', lid);
        this.lid = lid;
        
    }

    _log(key, value){
        if (this.loggable){
            this.loggable.log(this.lid, key, value);
        }
    }

}

export { RotatingCamera };