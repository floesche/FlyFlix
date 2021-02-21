import { PerspectiveCamera, MathUtils } from '/static/vendor/three.module.js';

class RotatingCamera extends PerspectiveCamera {
    constructor(fov, aspectRatio, nearClip, farClip, defaultAngle = 0, startOffset = 0, rotationAnglePerSecond = 1){
        super(fov, aspectRatio, nearClip, farClip);
        this.defaultAngle = defaultAngle;
        this.offset = startOffset;
        this.rotateRadHz = rotationAnglePerSecond;
        
        this.rotation.y = MathUtils.degToRad(defaultAngle + startOffset);

        this.loggable = null;
    }

    tick(delta) {
        this.rotation.y = (this.rotation.y + delta * this.rotateRadHz) % (2*Math.PI);
        this._log('camera-rotation', this.rotation.y);
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

    _log(key, value){
        if (this.loggable){
            this.loggable.log(key, value);
        }
    }

}

export { RotatingCamera };