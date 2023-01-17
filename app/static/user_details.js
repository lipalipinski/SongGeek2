const topTracksTable = document.querySelector('#top-tracks')
const topArtistsList = document.querySelector('#top-artists ul');
const topArtistsSpinner = document.querySelector('#artists-spinner');
const topTracksSpinner = document.querySelector('#tracks-spinner');
const topPlaylistsList = document.querySelector('#top-playlists ul');
const topPlaylistsSpinner = document.querySelector('#playlists-spinner');

function setMultiPlayer(plrs, cntrls, vol) {
    // play/pause player
    for (const [i, playpause] of cntrls.entries()) {
        playpause.addEventListener('click', () => {
            //pause other players while playing
            if (plrs[i].paused || plrs[i].ended) {
                for (const [j, player] of plrs.entries()) {
                    if (j == i) {
                        player.play();
                        console.log(i)
                    } else {
                        player.pause();
                    };
                };
            } else {
                plrs[i].pause();
            };
        });
    };

    // change play button state
    for (const [i, player] of plrs.entries()) {
        player.addEventListener('play', () => {
            changeButtonState(player, cntrls[i]);
        }, false)
        player.addEventListener('pause', () => {
            changeButtonState(player, cntrls[i]);
        }, false);
    };

    // adjust players volume
    vol.addEventListener('input', (e) => {
        for (const player of plrs) {
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
};

function setLikes(likes) {
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
                badgeForButton(btn, 'Added to Liked Songs', 900);
                // no like
            } else {
                btn.setAttribute('data-state', 'not-liked');
                btn.addEventListener('click', (e) => {
                    likeSong(track.id, true, e.target)
                }, { once: true });
                badgeForButton(btn, 'Removed from Liked Songs', 900);
            };
        });
};

// flash a badge for [timeout] seconds
function badgeForButton(button, message, timeout) {
    badge = document.createElement('span');
    badge.classList.add('position-absolute', 'top-100', 'start-50', 'translate-middle', 'badge', 'rounded-pill', 'bg-dark');
    badge.textContent = message;
    button.appendChild(badge);
    setTimeout(() => {
        badge.remove();
    }, timeout);
};

// TOP TRACKS
let data = {
    'mode':'topTracks'
};
fetch(FETCH_URL, {
    'method': 'POST',
    'headers': { 'Content-Type': 'application/json' },
    'body': JSON.stringify(data)
})
    .then((response) => {
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        };
        return response.json();
    })
    .then((tracks) => {
        if (tracks.length == 0) {
            const tr = document.createElement('tr');
            tr.textContent = "to few games";
            topTracksTable.querySelector('tbody').appendChild(tr);
            topTracksSpinner.classList.add('d-none');
            topTracksTable.classList.remove('d-none', 'list-group-numbered');
        }
        for (let [i, track] of tracks.entries()) {
            const tr = document.createElement('tr');
            tr.classList.add(`_${track.id}`)
            let artists = '';
            for (artist of track.artists) {
                artists += `<a href="${artist.url}" class="link-dark" data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Open in Spotify" target="_blank" noopener noreferer>
                                ${artist.name}
                            </a>`;
            }
            tr.innerHTML = `
                            <td><strong>${track.rank}.</strong></td>
                            <td>
                                <a href="${track.albumUrl}"  data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Open in Spotify" target="_blank" noopener noreferer>
                                    <img src="${track.albumImg}" class="cover-img" alt="">
                                </a>
                            </td>
                            <td>
                            ${artists} - 
                            <a href="${track.url}" class="link-dark" data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Open in Spotify" target="_blank" noopener noreferer>
                                ${track.name}
                            </a>
                            </td>
                            <td>
                                <strong>${track.score}</strong>
                            </td>
                            <td>
                                <audio id="player${i}" class="audio-player" preload>
                                    <source id="audioSource${i}" src="${track.prevUrl}" type="audio/mpeg">
                                </audio>
                                <button id="playpause${i}" class="multiplayer controls btn btn-sm btn-light" data-state="play"></button>
                            </td>
                            <td>
                                <button id="like${i}" class="like multiplayer btn btn-sm btn-light position-relative" data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Add to Liked Songs" data-state="loading" value="${track.id}">                                        
                                    <div id="spinner${i}" class="spinner-border spinner-border-sm" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </button>
                            </td>`;
            topTracksTable.querySelector('tbody').appendChild(tr);
        }
    })
    .then(() => {
        // initialize link tooltips
        const tracksTooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        const tracksTooltipList = [...tracksTooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
        // set player
        const players = document.querySelectorAll(".audio-player");
        const controls = document.querySelectorAll(".controls");
        const volume = document.querySelector('#volume');
        setMultiPlayer(players, controls, volume);
        // set likes
        const likes = document.querySelectorAll(".like");
        setLikes(likes);
        topTracksSpinner.classList.add('d-none');
        topTracksTable.classList.remove('d-none');
    });

// TOP ARTISTS
data = {
    'mode': 'topArtists'
};
fetch(FETCH_URL, {
    'method': 'POST',
    'headers': { 'Content-Type': 'application/json' },
    'body': JSON.stringify(data)
})
    .then((response) => {
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        };
        return response.json();
    })
    .then((artists) => {
        if (artists.length == 0) {
            const li = document.createElement('li');
            li.classList.add('list-group-item');
            li.textContent = "to few games";
            topArtistsList.appendChild(li);
            topArtistsSpinner.classList.add('d-none');
            topArtistsList.classList.remove('d-none', 'list-group-numbered');
        }
        for (artist of artists) {
            const li = document.createElement('li');
            li.classList.add('list-group-item');
            li.textContent = `${artist.name} (${artist.score})`;
            topArtistsList.appendChild(li);
            topArtistsSpinner.classList.add('d-none');
            topArtistsList.classList.remove('d-none');
        }
    });

// TOP PLAYLISTS
data = {
    'mode': 'topPlaylists'
};
fetch(FETCH_URL, {
    'method': 'POST',
    'headers': { 'Content-Type': 'application/json' },
    'body': JSON.stringify(data)
})
    .then((response) => {
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        };
        return response.json();
    })
    .then((playlists) => {
        // no top plsts
        if (playlists.length == 0) {
            const li = document.createElement('li');
            li.classList.add('list-group-item');
            li.textContent = "to few games";
            topPlaylistsList.appendChild(li);
            topPlaylistsSpinner.classList.add('d-none');
            topPlaylistsList.classList.remove('d-none', 'list-group-numbered');
        }
        for (playlist of playlists) {
            const li = document.createElement('li');
            li.classList.add('list-group-item');
            li.textContent = `${playlist.name} (${playlist.score})`;
            topPlaylistsList.appendChild(li);
            topPlaylistsSpinner.classList.add('d-none');
            topPlaylistsList.classList.remove('d-none');
        }
    });