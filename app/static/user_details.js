const topArtistsTable = document.querySelector('#top-artists');
const topArtistsSpinner = document.querySelector('#artists-spinner');
const topTracksTable = document.querySelector('#top-tracks')
const topTracksSpinner = document.querySelector('#tracks-spinner');
const topPlaylistsTable = document.querySelector('#top-playlists');
const topPlaylistsSpinner = document.querySelector('#playlists-spinner');
const playlistsRow = document.querySelector('#top-playlists');

function setMultiPlayer(plrs, cntrls, vol) {
    vol.classList.remove('d-none');
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

//set placeholders for playlists cards
function setPlaylistsPlaceholders(row, count) {
    //row.innerHTML = '';
    for (let i = 0; i < count; i++) {
        let placeholder = document.createElement('div');
        placeholder.classList.add('main-load', 'col', 'col-12', 'col-sm-6', 'col-md-4', 'col-lg-3', 'col-xl-2')
        placeholder.innerHTML = `
        <div class ="card h-100 px-0">
        <svg class="bd-placeholder-img card-img-top" width="100%" height="180" xmlns="http://www.w3.org/2000/svg" role="img"
                aria-label="Placeholder" preserveAspectRatio="xMidYMid slice" focusable="false">
                <title>Placeholder</title>
                <rect width="100%" height="100%" fill="#868e96"></rect>
            </svg>
            
            <div class="card-body">
                <h5 class="card-title placeholder-glow">
                        <span class="placeholder col-6"></span>
                </h5>
                <p class="card-text placeholder-glow">
                        <span class="placeholder col-1"></span> 
                        <span class="placeholder col-4"></span>
                </p>
                <p class="card-text placeholder-glow">
                        <span class="placeholder col-7"></span>
                        <span class="placeholder col-4"></span>
                        <span class="placeholder col-4"></span>
                        <span class="placeholder col-6"></span>
                        <span class="placeholder col-8"></span>
                </p>
            </div>
            <div class="card-footer text-center placeholder-glow">
                <span class="placeholder col-4"></span>
            </div>
            <div class="card-footer text-center placeholder-glow">
                <span class="placeholder col-4"></span>
            </div>
            </div>`;
        row.appendChild(placeholder);
    };
};

function removePlaceholders() {
    let placeholders = document.querySelectorAll('.main-load');
    for (placeholder of placeholders) {
        placeholder.remove();
    };
};

// TOP TRACKS
fetch(FETCH_URL + '/top-tracks', {
    'method': 'POST',
    'headers': { 'Content-Type': 'application/json' }
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
            tr.innerHTML = '<td class="text-center" colspan="6">to few games</td>'
            topTracksTable.querySelector('tbody').appendChild(tr);
            topTracksSpinner.classList.add('d-none');
            topTracksTable.classList.remove('d-none');
            return false;
        } else {
            
            for (let [i, track] of tracks.entries()) {
                const tr = document.createElement('tr');
                tr.classList.add(`_${track.id}`)
                let artists = '';
                for (let [i, artist] of track.artists.entries()) {
                    artists += `<a href="${artist.url}" class="link-dark" data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Open in Spotify" target="_blank" noopener noreferer>
                                ${artist.name}</a>`;
                    if (i != track.artists.length - 1) {
                        artists += ',';
                    };
                }
                tr.innerHTML = `
                            <td><strong>${track.rank}.</strong></td>
                            <td>
                                <a href="${track.albumUrl}"  data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Open in Spotify" target="_blank" noopener noreferer>
                                    <img src="${track.albumImg}" class="cover-img" alt="${track.name} cover photo">
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
                                <button id="like${i}" class="like multiplayer btn btn-sm btn-light position-relative" data-state="loading" value="${track.id}">                                        
                                    <div id="spinner${i}" class="spinner-border spinner-border-sm" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </button>
                            </td>`;
                topTracksTable.querySelector('tbody').appendChild(tr);
            }
            return true;
        };
    })
    .then((tracks) => {
        if (tracks) {
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
        };
    });

// TOP ARTISTS
fetch(FETCH_URL + '/top-artists', {
    'method': 'POST',
    'headers': { 'Content-Type': 'application/json' }
})
    .then((response) => {
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        };
        return response.json();
    })
    .then((artists) => {
        if (artists.length == 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td class="text-center" colspan="3">to few games</td>';
            topArtistsTable.querySelector('tbody').appendChild(tr);
            topArtistsSpinner.classList.add('d-none');
            topArtistsTable.classList.remove('d-none');
            return false;
        } else {
            for (let [i, artist] of artists.entries()) {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>
                <strong>${i + 1}.</strong>
                </td>
                <td>
                <a href="${artist.url}" class="link-dark" data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Open in Spotify" target="_blank" noopener noreferer>
                ${artist.name}
                </a>
                </td>
                <td>
                (<strong>${artist.score}</strong>)
                </td>`;
                topArtistsTable.querySelector('tbody').appendChild(tr);
                topArtistsSpinner.classList.add('d-none');
                topArtistsTable.classList.remove('d-none');
            };
            return true;
        };
    })
    .then((artists) => {
        if (artists) {    
            const artistsTooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            const artistsTooltipList = [...artistsTooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
        };
    });


function fetchPlaylists(row) {
    fetch(FETCH_URL + '/top-playlists', {
        'method': 'POST',
        'headers': { 'Content-Type': 'application/json' }
    })
    .then((response) => {
        if (!response.ok) {
            removePlaceholders()
            errorDiv = document.createElement('div');
            errorDiv.innerHTML = `<div class="card  h-100 my-auto" style="">
                    <div class="card-body my-auto">
                        <h5>Connection problem</h5>
                        <a href="${FETCH_URL}">
                            <button type="submit" class="btn btn-primary">Try again</button>
                        </a>                    
                    </div>
                </div>`;
            document.querySelector('#main-row').appendChild(errorDiv);
            throw new Error(`HTTP error ${response.status}`);
        };
        return response.json();
    })
        .then((json) => {
        // sort playlists by players avg score
        json.sort((p1, p2) => {
            return p2.score - p1.score;
        });
        removePlaceholders()
        for (pl of json) {
            let badge = '';
            if (pl.lvl == 1) {
                badge = '<h5>level: <span class="badge text-bg-success">easy</span></h5>';
            } if (pl.lvl == 2) {
                badge = '<h5>level: <span class="badge text-bg-warning">normal</span></h5>';
            } if (pl.lvl == 3) {
                badge = '<h5>level: <span class="badge text-bg-danger">hard</span></h5>';
            };
            let mainDiv = document.createElement('div');
            mainDiv.classList.add('col', 'col-12', 'col-sm-6', 'col-md-4', 'col-lg-3', 'col-xl-2')
            mainDiv.innerHTML = `<div class="card h-100">
            
            <div class="">
                <img src="${pl.imgUrl}" class="card-img-top" alt="${pl.name} cover image">
            </div>

            
            <div class="card-body">
                <h5 class="card-title">
                    <a href="${pl.url}" class="link-dark" target="_blank" data-bs-toggle="tooltip" data-bs-title="Open in Spotify" noopener noreferer>${pl.name}</a>
                </h5>
                <p class="card-text"><small class="text-muted">
                    by <a href="${pl.ownerUrl}" class="link-secondary" data-bs-toggle="tooltip" data-bs-title="Open in Spotify" target="_blank" noopener noreferer>
                        ${pl.ownerName}</a>
                </small></p>
                <p class="card-text">${pl.description}</p>
            </div>
            <div class="card-footer text-center">
                <span>
                    avg score: <strong>${pl.score}</strong>
                </span>
            </div>
            <div class="card-footer text-center">
                ${badge}
            </div>
            <div class="card-footer text-center">
                <a href="${QUIZ_URL}/${pl.id}">
                    <button name="pl" value="" class="btn btn-md btn-primary">Play!</button>
                </a>
            </div>
        </div>`;
            row.appendChild(mainDiv);
            const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
        };
    });
};

setPlaylistsPlaceholders(playlistsRow, 6);
fetchPlaylists(playlistsRow);