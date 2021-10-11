/**
 * 
 * @param {Element} container - HTML container that holds the 
 * @param {Camera} camera - Camera used in the container
 * @param {Renderer} renderer - renderer that is used in the container
 */
const setSize = (container, camera, renderer) => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
};


/**
 * Module to resize a scene.
 * 
 * Inspired by https://discoverthreejs.com/book/first-steps/world-app/
 */
class Resizer {
    /**
     * Resize the camera and renderer inside a container.
     * 
     * @param {Element} container - HTML container that holds the 
     * @param {Camera} camera - Camera used in the container
     * @param {Renderer} renderer - renderer that is used in the container
     */
    constructor(container, camera, renderer) {
        setSize(container, camera, renderer);
        window.addEventListener('resize', () => {
            setSize(container, camera, renderer);
            this.onResize();
        });
    }
    //TODO: check if setSize can be moved to onResize?
    onResize(){};
}

export { Resizer };