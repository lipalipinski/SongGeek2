// answer buttons
const buttons = document.querySelectorAll('.ans-btn');
const quest_num = document.querySelector('#quest_num')
var next_tracks
var resp

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
    if (playpause.getAttribute('data-state') == 'results') {
        return;
    }
    if (player.paused || player.ended) {
        player.play();
    } else {
        player.pause();
    }
});

// change play/pause button state (background img)
function changeButtonState() {
    playpause.textContent = '';
    if (player.paused || player.ended) {
        playpause.setAttribute('data-state', 'play');
    }
    else {
        playpause.setAttribute('data-state', 'pause');
    }
}

player.addEventListener('play', () => {
    changeButtonState();
}, false);

player.addEventListener('pause', () => {
    changeButtonState();
}, false);


// listen for the answer
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
            resp = json

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

            // if not last quest
            if (json.next_url != "") {
                // update audio src
                audioSource.setAttribute('src', json.next_url);
                player.load();
                // listen for new playback
                playpause.addEventListener('click', question);
                playpause.textContent = 'NEXT';
            } else {
                // AFTER LAST QUEST
                playpause.setAttribute('data-state', 'results');
                const results = document.querySelector('#results');
                results.setAttribute('href', RESULTS_URL);
            }
        })
        .catch((err) => console.error(`Fetch problem: ${err.message}`));
}


// prepere the question
function question(e) {
    // update buttons
    for (const [i, btn] of buttons.entries()) {
        // names
        btn.textContent = resp.next_tracks[i].name
        // classes
        btnReset(btn)
        // btn id's
        btn.setAttribute('id', `_${resp.next_tracks[i].id}`)
        // btn values
        btn.setAttribute('value', resp.next_tracks[i].id)
        // event listener
        btn.addEventListener('click', answer);
        // quest_num update
        quest_num.textContent = resp.quest_num +1
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
    } else {
        prog.classList.add('bg-success')
    }
    bar.appendChild(prog)
}