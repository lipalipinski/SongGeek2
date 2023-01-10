const topTracksList = document.querySelector('#top-tracks')
const topArtistsList = document.querySelector('#top-artists ul')
const topArtistsSpinner = document.querySelector('#artists-spinner')
const topTracksSpinner = document.querySelector('#tracks-spinner')


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
        for (track of tracks) {
            const li = document.createElement('li');
            li.classList.add('list-group-item');
            li.textContent = `${track.artists} - ${track.name} (${track.score})`;
            topTracksList.appendChild(li);
            topTracksSpinner.classList.add('d-none');
            topTracksList.classList.remove('d-none');
        }
    });

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
        for (artist of artists) {
            const li = document.createElement('li');
            li.classList.add('list-group-item');
            li.textContent = `${artist.name} (${artist.score})`;
            topArtistsList.appendChild(li);
            topArtistsSpinner.classList.add('d-none');
            topArtistsList.classList.remove('d-none');
        }
    });