class FullScreener{
    constructor(container){
        const fullscreenButton = document.createElement("button");
        fullscreenButton.innerHTML = "Fullscreen";
        fullscreenButton.id = "fullscreen";
        fullscreenButton.classList.add("experiment-controller");
        fullscreenButton.style.position = "absolute";
        fullscreenButton.style.top = "20%";
        fullscreenButton.style.left = "20%";
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
    onFullscreenChange() {};
}

export { FullScreener };