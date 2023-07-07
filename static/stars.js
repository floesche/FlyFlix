
import { StarfieldArena } from './arena/starfield_arena.js';

import { FullScreener } from './arena/systems/full_screener.js';
import { ExperimentControl } from './arena/systems/experiment_control.js';

/**
 * 
 */
var socket = io();

function main() {
    const container = document.querySelector('#scene-container');
  
    const arena = new StarfieldArena(container);

    const fullScreenButton = new FullScreener(container);
    const experimentController = new ExperimentControl(container, socket);
  
    
    arena.start();

}

main();
