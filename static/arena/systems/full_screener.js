/**
 * Module with fullscreen button
 */
class FullScreener{

    /**
     * Module to add a Fullscreen button to an HTML element.
     * 
     * @param {Element} container - HTML element to which the fullscreen button is attached.
     */
    constructor(container){
        const fullscreenButton = document.createElement("button");
        fullscreenButton.innerHTML = "Fullscreen";
        fullscreenButton.id = "fullscreen";
        fullscreenButton.classList.add("experiment-controller");
        fullscreenButton.style.position = "absolute";
        fullscreenButton.style.width = "25%";
        fullscreenButton.style.height = "20%";
        fullscreenButton.style.top = "20%";
        fullscreenButton.style.left = "5%";
        container.appendChild(fullscreenButton);
        
        fullscreenButton.addEventListener('click', () =>{
            document.body.requestFullscreen();
        });

        window.addEventListener('fullscreenchange', () => {
            if (document.fullscreenElement){
                fullscreenButton.style.visibility = "hidden";
            } else {
                fullscreenButton.style.visibility = "visible";
            }
        })
    }
}

export { FullScreener };