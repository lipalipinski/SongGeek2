function get_quiz() {

    // make request
    let data = {
        "mode": "newGame"
    }
    fetch(window.location.href, {
        "method": "POST",
        "headers": { "Content-Type": "application/json" },
        "body": JSON.stringify(data),
    })
        .then((response) => {
            // response not ok
            if (!response.ok) {
                const mainContainer = document.querySelector('#main-container');
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
            questNum = json.questNum;

            // set playlist img
            document.querySelector('#pl_img').setAttribute('src', json.plImgUrl);
            // set playlist name
            document.querySelector('#pl_name').textContent = json.plName;
            document.querySelector('#pl_name').setAttribute('href', json.plUrl)
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
            
            const quiz = new QuizPlayer(resp["quests"]);
            
            quiz.nextQuest();
        })
        .catch((err) => console.error(`Fetch problem: ${err.message}`));
}

function QuizPlayer(quests) {
    // init audio players
    this.state = 0;
    this.points = 0;
    this.players = [];

    for (const quest of quests) {
        this.players.push(new Player(quest))
    };

    // chain load audio
    this.players[0].loadAudio(1)
        .then(() => {
            this.enableBtns();
            return this.players[1].loadAudio(2);
        })
        .then(() => {
            return this.players[2].loadAudio(3);
        })
        .then(() => {
            return this.players[3].loadAudio(4);
        })
        .then(() => {
            return this.players[4].loadAudio(5);
        })

    this.nextQuest = function () {
        // quest counter
        document.querySelector('#quest_num').innerText = this.state + 1;
        // points counter
        document.querySelector('#points').innerText = this.points;
        this.players[this.state].setAnswers();
        this.state++;
    };

    //enable playback and answer
    this.enableBtns = function (enable=true) {
        for (const [i, btn] of document.querySelectorAll('.ans-btn').entries()) {
            if (enable == true) {
                btn.classList.remove('disabled');
            } else {
                btn.classList.add('disabled');
            }
        };
    };
};

function Player(quest) {
    this.tracks = quest["tracks"];
    this.audioPlayer = new Audio();
    this.audioPlayer.preload = 'none';
    this.audioPlayer.src = quest["prevUrl"];
    this.startPosition = Math.floor(Math.random() * 25);

    this.loadAudio = function (logger) {
        // count canplay events, if seeking fires twice
        let canplayCounter = 0;
        this.audioPlayer.load();
        this.audioPlayer.currentTime = this.startPosition;

        const seeking = new Promise((resolve) => {
            this.audioPlayer.addEventListener('seeked', () => {
                resolve();
            });
        });
        console.log('sdfsdfsdf')
        const canplay = new Promise((resolve) => {
            this.audioPlayer.addEventListener('canplaythrough', (e) => {
                if (this.audioPlayer.currentTime === 0) {
                    resolve();
                } else if (canplayCounter === 1) {
                    resolve();
                };
                canplayCounter++;
            });
        });

        // wait for seeking if start time not 0
        if (this.audioPlayer.currentTime != 0) {
            return Promise.all([seeking, canplay]);
        } else {
            return Promise.all([canplay]);
        }
    };

    // answer btns
    this.setAnswers = function () {
        for (const [i, btn] of document.querySelectorAll('.ans-btn').entries()) {
            btn.setAttribute('id', `_${this.tracks[i]["id"]}`);
            btn.setAttribute('value', `${this.tracks[i]["id"]}`);
            btn.innerText = this.tracks[i]["name"];
        };
    };

    this.startPlayback = function () {
        this.audioPlayer.play();
    };
};

function removePlaceholder() {
    document.querySelector('.load-card').remove();
};

function showCard() {
    document.querySelector('#quiz-card').classList.remove('d-none');
}


get_quiz();
removePlaceholder();
showCard();