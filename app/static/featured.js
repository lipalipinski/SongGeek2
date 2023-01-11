const mainRow = document.querySelector('#main-row');

let data = {
    'mode': 'featuredPlaylists'
};
fetch(FETCH_URL, {
    'method': 'POST',
    'headers': { 'Content-Type': 'application/json' },
    'body': JSON.stringify(data)
})
    .then((response) => {
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        };
    });
