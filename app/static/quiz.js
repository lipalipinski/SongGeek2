// answer buttons
const buttons = document.querySelectorAll('.ans-btn');
const quest_num = document.querySelector('#quest_num');
const quizCard = document.querySelector('#quiz-card');
const loadCard = document.querySelector('.load-card');
const mainContainer = document.querySelector('#main-container');
let resp;
const countdownSeconds = 5;
let timer;
let gameId;

// audio player controls
const player = document.querySelector('#player');
const play = document.querySelector("#playpause");
const volume = document.querySelector('#volume');
const audioSource = document.querySelector('#audioSource');
const mute = document.querySelector('#mute');

function get_quiz() {

    // make request
    let data = {
        "mode": "newGame"
    }

    fetch(QUIZ_URL, {
        "method": "POST",
        "headers": { "Content-Type": "application/json" },
        "body": JSON.stringify(data),
    })
        .then((response) => {
            if (!response.ok) {
                mainContainer.textContent = ""
                mainContainer.innerHTML = `<div class="card  h-100 my-auto" style="">
                <div class="card-body my-auto">
                    <h5>Connection problem</h5>
                    <a href="${QUIZ_URL}?force=True">
                        <button type="submit" class="btn btn-primary">Try again</button>
                    </a>                    
                </div>
            </div>`
                throw new Error(`HTTP error: ${response.status}`);
            }
            return response.json();
        })
        .then((json) => {
            resp = json;
            document.querySelector('title').innerText = `SongGeek: ${json.plName}`;
            gameId = json.gameId;
            // set playlist img
            document.querySelector('#pl_img').setAttribute('src', json.plImgUrl);
            // set playlist name
            document.querySelector('#pl_name').textContent = json.plName;
            // set playlist owner
            document.querySelector('#pl_owner').textContent = json.plOwner;
            // set playlist description
            document.querySelector('#pl_desc').textContent = json.plDescription;
            // set playlist lvl
            let badge = document.createElement('h5');
            switch (json.plLvl) {
                case 1:
                    badge.innerHTML = 'level: <span class="badge text-bg-success">easy</span>';
                    break;
                case 2:
                    badge.innerHTML = 'level: <span class="badge text-bg-warning">normal</span>';
                    break;
                case 3:
                    badge.innerHTML = 'level: <span class="badge text-bg-danger">hard</span>';
                    break;
            };
            document.querySelector('#lvl-badge').appendChild(badge);
            // update audio src
            audioSource.setAttribute('src', json.next_url);
            player.load();
            // set random playback start time
            let startTime = Math.floor(Math.random() * 25);
            player.currentTime = startTime;
            play.addEventListener('click', startPlayer, { once: true });
            const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
            loadCard.classList.add('d-none');
            quizCard.classList.remove('d-none');

            question();
        })
        .catch((err) => console.error(`Fetch problem: ${err.message}`));
}

function startPlayer() {
    if (play.getAttribute('data-state') == 'results') {
        return;
    }
    if (player.paused || player.ended) {
        score = countdownSeconds;
        play.textContent = score;
        player.play();
        play.setAttribute('data-state', 'countdown');
        timer = setInterval(() => {
            score--;
            if (score == 0) {
                player.pause();
                play.setAttribute('data-state', 'after-countdown');
                play.textContent = "time's out!";
                buttons[buttons.length - 1].scrollIntoView(false);
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
        "mode": "nextQuest",
        "gameId": gameId,
        "id": e.target.value,
        "score": score
    }

    fetch(QUIZ_URL, {
        "method": "POST",
        "headers": { "Content-Type": "application/json" },
        "body": JSON.stringify(data),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }
            return response.json();
        })
        .then((json) => {
            resp = json;
            // update points display
            const points = document.querySelector('#points');
            points.textContent = json.total_points;

            // green answer
            turnGreen(document.querySelector(`#_${json.green}`));
            // show badge
            if (json.points > 0) {
                const badge = document.querySelector(`#_${json.green} span`);
                badge.classList.remove('d-none');
                badge.textContent = '+' + json.points;
            };
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
                // set random playback start time
                let startTime = Math.floor(Math.random() * 25);
                player.currentTime = startTime;
                // listen for new playback
                play.addEventListener('click', question);
                play.addEventListener('click', startPlayer, { once: true });
                play.textContent = 'NEXT';
            } else {
                // AFTER LAST QUEST
                
                play.textContent = ' ';
                play.setAttribute('data-state', 'results');
                const results = document.querySelector('#results');
                results.href = json.resultsUrl;
            }
        })
        .catch((err) => console.error(`Fetch problem: ${err.message}`));
}

// prepere the question
function question() {
    // update buttons
    for (let [i, btn] of buttons.entries()) {
        const badge = document.createElement('span');
        badge.classList.add('d-none', 'position-absolute', 'top-0', 'start-100', 'translate-middle', 'badge', 'rounded-pill', 'bg-danger');
        // names
        btn.textContent = resp.next_tracks[i].name;
        btn.appendChild(badge);
        // classes
        btnReset(btn);
        // btn id's
        btn.setAttribute('id', `_${resp.next_tracks[i].id}`);
        // btn values
        btn.setAttribute('value', resp.next_tracks[i].id);
        // event listener
        btn.addEventListener('click', answer);
        // quest_num update
        quest_num.textContent = resp.quest_num + 1
    }
    play.removeEventListener('click', question)
    buttons[buttons.length-1].scrollIntoView(false);
};

function turnGreen(btn) {
    btn.classList.replace('btn-light', 'btn-success');
};

function turnRed(btn) {
    btn.classList.replace('btn-light', 'btn-danger');
};

function btnReset(btn) {
    btn.classList.replace('btn-success', 'btn-light');
    btn.classList.replace('btn-danger', 'btn-light');
};

function progbar(bar, succes) {
    const prog = document.createElement('div');
    prog.classList.add('progress-bar');
    prog.style.width = '20%';
    if (succes == false) {
        prog.classList.add('bg-danger');
    } else {
        prog.classList.add('bg-success');
    }
    bar.appendChild(prog);
};


get_quiz()

for (const btn of buttons) {
    btn.addEventListener('click', answer);
}

//start at random second
let startTime = Math.floor(Math.random() * 25);
player.currentTime = startTime;

// disable all buttons after answer
play.addEventListener('click', () => {
    for (const btn of buttons) {
        btn.disabled = false;  
    };
}, { once: true });


// volume slider
volume.addEventListener('input', (e) => {
    player.volume = e.target.value / 100;
});

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

play.addEventListener('click', startPlayer, { once: true });
player.addEventListener('pause', () => {
    clearInterval(timer);
});
