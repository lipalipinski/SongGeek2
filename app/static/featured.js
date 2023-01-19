const mainRow = document.querySelector('#main-row');
// change country button (in modal)
const changeBtn = document.querySelector('#change-country');
// dropdown menu
const selectCountry = document.querySelector('#select-country');
// selected option in dropdown menu
const selectedCountry = document.querySelector('#selected-country')
// select country button (navbar)
const buttonCountry = document.querySelector('#country-btn');
let targetCountry;

function setPlaceholders() {
    mainRow.innerHTML = '';
    for (let i = 0; i < 8; i++) {
        let placeholder = document.createElement('div');
        placeholder.classList.add('main-load', 'col');
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
        mainRow.appendChild(placeholder);
    };  
};

function removePlaceholders() {
    let placeholders = document.querySelectorAll('.main-load');
    for (placeholder of placeholders) {
        placeholder.remove();
    };
};

function fetchPlaylists() {
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
            json.sort((p1, p2) => {
                return p2.lvl - p1.lvl;
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
                mainDiv.classList.add('col')
                mainDiv.innerHTML = `<div class="card h-100">
                
                <div class="">
                    <img src="${pl.imgUrl}" class="card-img-top" alt="${pl.name} cover image">
                </div>

                
                <div class="card-body">
                    <a href="${pl.url}" class="link-dark" target="_blank" data-bs-toggle="tooltip" data-bs-title="Open in Spotify" noopener noreferer>
                        <h4 class="card-title align-middle">
                            ${pl.name}
                            <img id="spotify-icon" src="static/img/Spotify_Icon_RGB_Green.png" alt="Spotify icon">
                        </h4>
                        
                    </a>
                    
                    <p class="card-text">${pl.description}</p>
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
                mainRow.appendChild(mainDiv);
                const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
                const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
            };
        });
};


function changeCountry(code) {
    data = {
        "code": code
    }
    fetch(COUNTRY_URL, {
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
            // update page
            selectedCountry.textContent = `${json["code"]}: ${json["name"]}}`;
            buttonCountry.textContent = `Country: ${json["name"]}`;
        })
        .then(() => {
            fetchPlaylists();
        });
};

selectCountry.addEventListener('input', (e) => {
    targetCountry = e.target.value
});


setPlaceholders();
fetchPlaylists();

changeBtn.addEventListener('click', () => {
    setPlaceholders();
    changeCountry(targetCountry);
});