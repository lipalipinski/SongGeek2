const players = document.querySelectorAll(".audio-player");
const controls = document.querySelectorAll(".controls");
const volume = document.querySelector('#volume');
const likes = document.querySelectorAll(".like")

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

// change button state
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
                    btn.addEventListener('click', () => {
                        like_song(track.id, false)
                    }, { once: true })
                // no like
                } else {
                    btn.setAttribute('data-state', 'not-liked');
                    btn.addEventListener('click', () => {
                        like_song(track.id, true)
                    }, { once: true })
                };
            };
    })
}

function like_song(id, like) {

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
                throw new Error(`HTTP error: ${response.status}`);
            }
            return response.json();
        })
        .then((track) => {
            btn = document.querySelector(`#_${track.id} td button.like`);
                if (like == true) {
                    btn.setAttribute('data-state', 'liked');
                    btn.addEventListener('click', () => {
                        like_song(track.id, false)
                    }, { once: true });
                    // no like
                } else {
                    btn.setAttribute('data-state', 'not-liked');
                    btn.addEventListener('click', () => {
                        like_song(track.id, true)
                    }, { once: true });
                };
        })
}