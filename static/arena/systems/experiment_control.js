/**
 * Restart button complete with style sheet. Becomes visible when `end-experiment` event is 
 *      triggered.
 * 
 * @param {Element} container - HTML to which the restart button should be added
 */
const addRestartButton = (container, socket) => {
    const restartExperiment = document.createElement("button");
        restartExperiment.innerHTML = "Restart";
        restartExperiment.style.position = "absolute";
        restartExperiment.style.visibility = "hidden";
        restartExperiment.classList.add("experiment-controller");
        restartExperiment.style.width = "25%";
        restartExperiment.style.height = "20%";
        restartExperiment.style.top = "20%";
        restartExperiment.style.left = "40%";
        container.appendChild(restartExperiment);

        restartExperiment.addEventListener('click', function () {
            manualRestart(socket);
            window.location.reload();
        });

        window.addEventListener('end-experiment', () => {
            restartExperiment.style.visibility = "visible";
        });
};

/**
 * Add start button to container. On click hide all Elements of the `experiment-controller` class
 *      and trigger the local `start-experiment` event.
 * 
 * @param {Element} container - HTML to which the start button attaches
 */
const addStartButton = (container) => {
    const startExperiment = document.createElement("button");
    startExperiment.innerHTML = "Start";
    startExperiment.style.position = "absolute";
    startExperiment.style.visibility = "visible";
    startExperiment.classList.add("experiment-controller");
    startExperiment.style.width = "25%";
    startExperiment.style.height = "20%";
    startExperiment.style.top = "20%";
    startExperiment.style.left = "70%";
    container.appendChild(startExperiment);

    startExperiment.addEventListener('click', function () {
        const startEvent = new Event('start-experiment');
        window.dispatchEvent(startEvent);
    });
};

/**
 * function to trigger control panel update after restart is pressed
 */
function manualRestart(socket){
    socket.emit('manual-restart', {});
}


/**
 * Module to add restart and start button.
 */
class ExperimentControl{

    /**
     * Create an experimental controller
     * 
     * @constructor
     * @param {Element} container - HTML element to which the start and restart button attaches
     */
    constructor(container, socket, add_start=true){
        addRestartButton(container, socket);
        if (add_start){
            addStartButton(container);
        }

        window.addEventListener('experiment-started', () =>{
            //startExperiment.style.visibility = 'hidden';
            const controllers = container.getElementsByClassName('experiment-controller');
            for (const element of controllers) {
                element.style.visibility = "hidden";
            }
        })

        // socket configuration for control panel buttons
        socket.on('start-triggered', function(empty){
            const controllers = container.getElementsByClassName('experiment-controller');
            for (const element of controllers) {
                element.style.visibility = "hidden";
            }
            const startEvent = new Event('start-experiment');
            window.dispatchEvent(startEvent);
        })

        socket.on('restart-triggered', function(empty){
            window.location.reload();
        })

        socket.on('stop-triggered', function(empty){
            const stopEvent = new Event('end-experiment');
            window.dispatchEvent(stopEvent);
            //window.location.reload();
        })
    }
}

export { ExperimentControl };

