const players = document.querySelectorAll(".audio-player");
const controls = document.querySelectorAll(".controls");
const volume = document.querySelector('#volume');

for (const [i, playpause] of controls.entries()) {
    playpause.addEventListener('click', () => {
        if (players[i].paused || players[i].ended) {
            for (const [j, player] of players.entries()) {
                if (j == i) {
                    player.play();
                } else {
                    player.pause();
                }
            }
        } else {
            players[i].pause();
        };
    });
};

for (const [i, player] of players.entries()) {
    player.addEventListener('play', () => {
        changeButtonState(player, controls[i]);
    }, false)
    player.addEventListener('pause', () => {
        changeButtonState(player, controls[i]);
    }, false);
};

volume.addEventListener('input', (e) => {
    for (const player of players) {
        player.volume = e.target.value / 100;
    };
});


// change play/pause button state (background img)
function changeButtonState(player, control) {
    if (player.paused || player.ended) {
        control.setAttribute('data-state', 'play');
    }
    else {
        control.setAttribute('data-state', 'pause');
    };
};