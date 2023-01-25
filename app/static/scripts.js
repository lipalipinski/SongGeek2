function cookiesPrompt() {
    // cookies prompt
    const maxAge = 60 * 60 * 24 * 7 * 4 * 12;
    const cookiesBtn = document.querySelector('#cookies-understood')
    const cookiesModal = new bootstrap.Modal('#cookies-prompt', { keyboard: false });

    if (!document.cookie.split(';').find(row => row.startsWith('cookies'))) {
        cookiesModal.show();
    }

    cookiesBtn.addEventListener('click', () => {
        document.cookie = `cookies=true;max-age=${maxAge};samesite=strict`;
        cookiesModal.hide();
    });
};

// handles remembering and setting volume in audio players
// volume controls must have .volume-slider
function setVolume() {
    //remember volume
    const volumeSliders = document.querySelectorAll('.volume-slider');
    const volumeSetting = sessionStorage.getItem('volume');
    for (const slider of volumeSliders) {
        if (!volumeSetting) {
            slider.setAttribute('value', '80');
        } else {
            slider.setAttribute('value', volumeSetting);
        };
        // store volume setting
        slider.addEventListener('input', (e) => {
            sessionStorage.setItem('volume', e.target.value);
        });
    };
    //set audio players volume
    if (volumeSetting) {
        // set remembered volume to audio players
        const audioPlayers = document.querySelectorAll('audio');
        for (const audio of audioPlayers) {
            audio.volume = parseInt(volumeSetting)/100;
        };
    };
};

cookiesPrompt();
setVolume();

// flash tooltip for [timeout] seconds
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

// fetch like status of the songs and set heart buttons state
function setLikes(likeButtons) {
    let tracks = [];
    for (like of likeButtons) {
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
                for (like of likeButtons) {
                    like.setAttribute('disabled', 'true');
                    like.setAttribute('data-state', 'fail');
                };
                throw new Error(`HTTP error: ${response.status}`);
            }
            return response.json();
        })
        .then((resp) => {
            for (const [i, track] of resp.tracks.entries()) {
                btn = document.querySelector(`#like${i}`);
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

// request adding/removing track from users library
function likeSong(id, like, btn) {
    // id - track_id, like - bool (true=add song), btn - heart button
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
