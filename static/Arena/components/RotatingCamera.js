import { PerspectiveCamera, MathUtils } from '/static/vendor/three.module.js';

class RotatingCamera extends PerspectiveCamera {
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

    setRotateDegHz(rotateDegHz){
        this.rotateRadHz = MathUtils.degToRad(rotateDegHz);
        this._log('camera-set-rotateDegHz', rotateDegHz);
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