// answer buttons
const buttons = document.querySelectorAll('.ans-btn');
const quest_num = document.querySelector('#quest_num');
var next_tracks;
var resp;
var countdownSeconds = 5;

for (const btn of buttons) {
    btn.addEventListener('click', answer);
}

// audio player controls
const player = document.querySelector('#player');
const play = document.querySelector("#playpause");
const volume = document.querySelector('#volume');
const audioSource = document.querySelector('#audioSource');
const mute = document.querySelector('#mute');

// volume slider
volume.addEventListener('input', (e) => {
    player.volume = e.target.value / 100;
})

// toggle mute 
mute.addEventListener('click', (e) => {
    if (!player.muted) {
        player.muted = true;
        e.target.setAttribute('data-state', 'muted');
    } else {
        player.muted = false;
        e.target.setAttribute('data-state', 'not-muted');
    }
})

play.addEventListener('click', startPlayer, {once: true});

function startPlayer() {
    if (play.getAttribute('data-state') == 'results') {
        return;
    }
    if (player.paused || player.ended) {
        score = countdownSeconds;
        play.textContent = score;
        player.play();
        play.setAttribute('data-state', 'countdown');
        const timer = setInterval(() => {
            score--;
            if (player.paused) {
                clearInterval(timer);
                return;
            } else if (score == 0) {
                player.pause();
                play.setAttribute('data-state', 'after-countdown');
                play.textContent = "time's out!";
                clearInterval(timer);
                return;
            } else {
                play.textContent = score;
            };
        }, 1000);
    };
};

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
        "id": e.target.value,
        "score": score
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
                play.addEventListener('click', question);
                play.addEventListener('click', startPlayer, { once: true });
                play.textContent = 'NEXT';
            } else {
                // AFTER LAST QUEST
                play.textContent = null;
                play.setAttribute('data-state', 'results');
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
    play.removeEventListener('click', question)
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