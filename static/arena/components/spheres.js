import { Group, 
    MathUtils, 
    SphereGeometry, 
    MeshBasicMaterial, 
    Mesh,
    PerspectiveCamera,
    Scene,
    Color,
    WebGLRenderer,
    BoxGeometry,
} from '/static/vendor/three.module.js';

function createSpheres(sphereCount, sphereRadius, shellRadius, color=0x00ff00){
    const sphereGroup = new Group();
    const geometry = new SphereGeometry( sphereRadius, 32, 16 );
    const material = new MeshBasicMaterial( { color: 0x00ff00 } );

    for ( let i=0; i<sphereCount; i++){
        let sphereMesh = new Mesh( geometry, material );
        let positions = randomSpherePoint(0,0,0, shellRadius);
        sphereMesh.position.x = positions[0];
        sphereMesh.position.y = positions[1];
        sphereMesh.position.z = positions[2];
        sphereGroup.add(sphereMesh);
    }

    return sphereGroup;
}

/**
     * Function that takes in a center point (x0, y0, z0) and a radius 
     * and returns a random point on the sphere surrounding the point with that radius
     * taken from https://stackoverflow.com/questions/5531827/random-point-on-a-given-sphere answer from user Neil Lamoureux
     * 
    */
function randomSpherePoint(x0,y0,z0,radius){
    var u = Math.random();
    var v = Math.random();
    var theta = 2 * Math.PI * u;
    var phi = Math.acos(2 * v - 1);
    var x = x0 + (radius * Math.sin(phi) * Math.cos(theta));
    var y = y0 + (radius * Math.sin(phi) * Math.sin(theta));
    var z = z0 + (radius * Math.cos(phi));
    return [x,y,z];
}

export { createSpheres };