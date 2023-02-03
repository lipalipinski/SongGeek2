const players = document.querySelectorAll(".audio-player");
const controls = document.querySelectorAll(".controls");
const volume = document.querySelector('#volume');

const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

function setLvlBadge(badge, lvl) {
    let badgeClass;
    let badgeText;
    switch (lvl) {
        case 1:
            badgeClass = 'text-bg-success';
            badgeText = 'easy';
            break;
        case 2:
            badgeClass = 'text-bg-warning';
            badgeText = 'normal';
            break;
        case 3:
            badgeClass = 'text-bg-danger';
            badgeText = 'hard';
            break;
    };
    badge.classList.add(badgeClass);
    badge.textContent = badgeText;
}

// change play/pause button state (background img)
function changeButtonState(player, control) {
    if (player.paused || player.ended) {
        control.setAttribute('data-state', 'play');
    }
    else {
        control.setAttribute('data-state', 'pause');
    };
};

setLvlBadge(document.querySelector('#lvl-badge'), GAME_LVL);

if (USER_LOGGED == 'True') {
    setLikes(document.querySelectorAll(".like"));
}

// play/pause player
for (const [i, playpause] of controls.entries()) {
    playpause.addEventListener('click', () => {
        //pause other players while playing
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

// change play button state
for (const [i, player] of players.entries()) {
    player.addEventListener('play', () => {
        changeButtonState(player, controls[i]);
    }, false)
    player.addEventListener('pause', () => {
        changeButtonState(player, controls[i]);
    }, false);
};

// adjust players volume
volume.addEventListener('input', (e) => {
    for (const player of players) {
        player.volume = e.target.value / 100;
    };
});
