
import { Arena } from './Arena/Arena.js';

import { FullScreener } from './Arena/systems/FullScreener.js';
import { ExperimentControl } from './Arena/systems/ExperimentControl.js';


function main() {
    const container = document.querySelector('#scene-container');
  
    const arena = new Arena(container);

    const fullScreenButton = new FullScreener(container);
    const experimentController = new ExperimentControl(container);
  
    arena.start();
  }
main();
