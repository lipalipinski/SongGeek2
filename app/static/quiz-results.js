const players = document.querySelectorAll(".audio-player");
const controls = document.querySelectorAll(".controls");
const volume = document.querySelector('#volume');
const likes = document.querySelectorAll(".like")

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

function setLikes() {
    let tracks = [];
    for (like of likes) {
        tracks.push(like.value)
    }
    let data = {
        'mode': 'check',
        'tracks': tracks,
    }
    fetch(LIKES_API, {
        'method': 'POST',
        'headers': { "Content-Type": "application/json" },
        'body': JSON.stringify(data)
    })
        .then((response) => {
            if (!response.ok) {
                // make buttons inactive
                for (like of likes) {
                    like.setAttribute('disabled', 'true');
                    like.setAttribute('data-state', 'fail');
                };
                throw new Error(`HTTP error: ${response.status}`);
            }
            return response.json();
        })
        .then((resp) => {
            for (const [i, track] of resp.tracks.entries()) {
                btn = document.querySelector(`#_${track.id} td button.like`);
                // song is liked
                if (track.like == true) {
                    btn.setAttribute('data-state', 'liked');
                    btn.addEventListener('click', (e) => {
                        likeSong(track.id, false, e.target)
                    }, { once: true })
                    // no like
                } else {
                    btn.setAttribute('data-state', 'not-liked');
                    btn.addEventListener('click', (e) => {
                        likeSong(track.id, true, e.target)
                    }, { once: true })
                };
            };
        });
};

function likeSong(id, like, btn) {

    btn.setAttribute('data-state', 'loading')

    let data = {
        'mode': 'set_like',
        'like': like,
        'id': id,
    };
    fetch(LIKES_API, {
        'method': 'POST',
        'headers': { "Content-Type": "application/json" },
        'body': JSON.stringify(data)
    })
        .then((response) => {
            if (!response.ok) {
                // set likes if request fails
                setLikes();
                btn.setAttribute('data-state', 'fail');
                btn.setAttribute('disabled', 'true');
                throw new Error(`HTTP error: ${response.status}`);
            }
            return response.json();
        })
        .then((track) => {
            if (like == true) {
                btn.setAttribute('data-state', 'liked');
                btn.addEventListener('click', (e) => {
                    likeSong(track.id, false, e.target)
                }, { once: true });
                flashTooltip(btn, 'Added to Liked Songs', 900);
                // no like
            } else {
                btn.setAttribute('data-state', 'not-liked');
                btn.addEventListener('click', (e) => {
                    likeSong(track.id, true, e.target)
                }, { once: true });
                flashTooltip(btn, 'Removed from Liked Songs', 900);
            };
        });
};

// flash a tooltip for [timeout] seconds
function flashTooltip(element, message, timeout) {
    const tooltip = new bootstrap.Tooltip(element, {
        'title': message,
        'trigger': 'manual'
    });
    tooltip.show();
    setTimeout(() => {
        tooltip.dispose();
    }, timeout);
};


setLvlBadge(document.querySelector('#lvl-badge'), GAME_LVL);

setLikes()

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
