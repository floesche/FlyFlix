import { PerspectiveCamera, MathUtils } from '/static/vendor/three.module.js';

class RotatingCamera extends PerspectiveCamera {
    constructor(fov, aspectRatio, nearClip, farClip, defaultAngle = 0, startOffset = 0, rotationAnglePerSecond = 1){
        super(fov, aspectRatio, nearClip, farClip);
        this.defaultAngle = defaultAngle;
        this.offset = startOffset;
        this.rotateRadHz = rotationAnglePerSecond;
        
        this.rotation.y = MathUtils.degToRad(defaultAngle + startOffset);
    }

    tick(delta) {        
        
        this.rotation.y = (this.rotation.y + delta * this.rotateRadHz) % (2*Math.PI);
    }

    setRotateRadHz(rotateRadHz){
        this.rotateRadHz = rotateRadHz;
    }

    setRotateDegHz(rotateDegHz){
        this.rotateRadHz = MathUtils.degToRad(rotateDegHz);
    }

    setRotationRad(rotation){
        this.rotation.y = rotation % (2*Math.PI);
    }

}

export { RotatingCamera };