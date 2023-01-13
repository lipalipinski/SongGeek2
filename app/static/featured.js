const mainRow = document.querySelector('#main-row');
let mainLoadSpinner = document.querySelector('#main-load-spinner');
// change country button (in modal)
const changeBtn = document.querySelector('#change-country');
// dropdown menu
const selectCountry = document.querySelector('#select-country');
// selected option in dropdown menu
const selectedCountry = document.querySelector('#selected-country')
// select country button (navbar)
const buttonCountry = document.querySelector('#country-btn');
let targetCountry;

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
                mainLoadSpinner.classList.add('d-none');
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
                mainLoadSpinner.classList.add('d-none')
                mainRow.appendChild(mainDiv);
            };
        });
};

function setLoading() {
    mainRow.textContent = "";
    spinner = document.createElement('div');
    spinner.setAttribute('id', 'main-load-spinner');
    spinner.classList.add('col', 'my-5', 'mx-auto');
    spinner.innerHTML = `<div class="d-flex h-100 justify-content-center align-items-center">
                <div class="spinner-border"></div></div>`;
    mainLoadSpinner = spinner;
    mainRow.appendChild(mainLoadSpinner);

};

selectCountry.addEventListener('input', (e) => {
    targetCountry = e.target.value
});

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

fetchPlaylists();

changeBtn.addEventListener('click', () => {
    setLoading();
    changeCountry(targetCountry);
});