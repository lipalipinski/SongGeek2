const topTracksList = document.querySelector('#top-tracks')



data = {
    "mode": "topTracks"
};
fetch(FETCH_URL, {
    'method': 'POST',
    'headers': { "Content-Type": "application/json" },
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
        }
    });