// answer buttons
const buttons = document.querySelectorAll('.ans-btn');
var next_tracks

for (const btn of buttons) {
    btn.addEventListener('click', answer);
}

// audio player controls
const player = document.querySelector('#player')
const playpause = document.querySelector("#playpause")
const volume = document.querySelector('#volume')
const audioSource = document.querySelector('#audioSource')

volume.addEventListener('input', (e) => {
    player.volume = e.target.value / 100;
})

playpause.addEventListener('click', () => {
    if (player.paused || player.ended) {
        player.play();
    } else {
        player.pause();
    }
});

// change play/pause button state (background img)
function changeButtonState() {
    if (player.paused || player.ended) {
        playpause.setAttribute('data-state', 'play')
    }
    else {
        playpause.setAttribute('data-state', 'pause')
    }
}

player.addEventListener('play', () => {
    changeButtonState();
}, false);

player.addEventListener('pause', () => {
    changeButtonState();
}, false);


function answer(e) {
    
    // remove listeners from buttons
    for (const btn of buttons) {
        btn.removeEventListener('click', answer);
    }

    // pause player
    player.pause()

    // make request
    let data = {
        "id": e.target.value
    }

    fetch(ANSWER_URL, {
        "method": "POST",
        "headers": { "Content-Type": "application/json" },
        "body": JSON.stringify(data),})
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }
            return response.json();
        })
        .then((json) => {
            // DEBUG LOG
            console.log(json)

            // update points display
            const points = document.querySelector('#points');
            points.textContent = json.points;
            
            // green answer
            turnGreen(document.querySelector(`#_${json.green}`));
            // red answer
            if (json.red != "") {
                turnRed(document.querySelector(`#_${json.red}`));
                progbar(document.querySelector('#prog_bar'), false);
            } else {
                progbar(document.querySelector('#prog_bar'), true);
            }

            // if not last game
            // update audio src
            audioSource.setAttribute('src', json.next_url)
            player.load()

            next_tracks = json.next_tracks
            // listen for new playback
            playpause.addEventListener('click', question)

        })
        .catch((err) => console.error(`Fetch problem: ${err.message}`));
}

function question(e) {
    // update buttons
    for (const [i, btn] of buttons.entries()) {
        // names
        btn.textContent = next_tracks[i].name
        // classes
        btnReset(btn)
        // btn id's
        btn.setAttribute('id', `_${next_tracks[i].id}`)
        // btn values
        btn.setAttribute('value', next_tracks[i].id)
        // event listener
        btn.addEventListener('click', answer);
    }
    playpause.removeEventListener('click', question)
}

function turnGreen(btn) {
    btn.classList.replace('btn-light', 'btn-success');
}

function turnRed(btn) {
    btn.classList.replace('btn-light', 'btn-danger');
}

function btnReset(btn) {
    btn.classList.replace('btn-success', 'btn-light');
    btn.classList.replace('btn-danger', 'btn-light');
}

function progbar(bar, succes) {
    const prog = document.createElement('div')
    prog.classList.add('progress-bar')
    prog.style.width = '20%'
    if (succes == false) {
        prog.classList.add('bg-danger')
    }
    bar.appendChild(prog)
}