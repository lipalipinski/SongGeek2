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
        return response.json();
    })
    .then((json) => {
        console.log(json);
        for (pl of json) {
            let mainDiv = document.createElement('div');
            mainDiv.classList.add('col')
            mainDiv.innerHTML = `<div class="card h-100" style="">
                
                <div class="">
                    <img src="${pl.imgUrl}" class="card-img-top" alt="${pl.name} cover image">
                </div>

                
                <div class="card-body">
                    <h5 class="card-title">
                        <a href="${pl.url}" target="_blank" noopener noreferer>${pl.name}</a>
                    </h5>
                    <p class="card-text"><small class="text-muted">
                        by <a href="${pl.ownerUrl}" target="_blank" noopener noreferer>
                            ${pl.ownerName}</a>
                    </small></p>
                    <p class="card-text">${pl.description}</p>
                </div>

                <div class="card-footer text-center">
                    <a href="${QUIZ_URL}/${pl.id}">
                        <button name="pl" value="" class="btn btn-md btn-primary">Play!</button>
                    </a>
                </div>
            </div>`;
            mainRow.appendChild(mainDiv);
        };
    });
