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
            
        })
        .catch((err) => console.error(`Fetch problem: ${err.message}`));
}

function QuizPlayer(quests) {
    // init audio players
    this.state = 0;
    this.points = 0;
    this.players = [];

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

    // controlBtnStatus
    this.controlBtnStatus = function (state) {
        const btn = document.querySelector('#playpause');
        btn.innerText = '';
        switch (state) {
            case 'loading':
                const spinner = document.createElement('div');
                spinner.classList.add('spinner-border');
                spinner.setAttribute('role', 'status');
                btn.setAttribute('data-state', 'loading');
                btn.appendChild(spinner);
                break;
            case 'play':
                btn.setAttribute('data-state', 'play')
                break;
            case 'countdown':
                btn.setAttribute('data-state', 'countdown')
                break;
            case 'after-countdown':
                btn.setAttribute('data-state', 'after-countdown')
                break;
            case 'results':
                btn.setAttribute('data-state', 'results')
                break;
                break;
        };
    };

    // init players
    for (const quest of quests) {
        this.players.push(new Player(quest))
    };
    
    // load audio chain
    let loadChain = Promise.resolve();
    for ([i, player] of this.players.entries()) {
        loadChain = loadChain
        .then(player.loadAudio(i))
        .then(console.log(`loaded ${i}`))
    };
    
    this.controlBtnStatus('loading');
    removePlaceholder();
    showCard();

    this.players[0].ready
        .then(() => {
            this.nextQuest();
            this.enableBtns();
            this.controlBtnStatus('play');
        });
    

};

function Player(quest) {
    this.tracks = quest["tracks"];
    this.audioPlayer = new Audio();
    this.audioPlayer.preload = 'none';
    this.audioPlayer.src = quest["prevUrl"];
    this.startPosition = Math.floor(Math.random() * 25);
    this.readyResolver;
    this.ready = new Promise((resolve) => {
        this.readyResolver = resolve;
    });

    this.loadAudio = function (logger) {
        // count canplay events, if seeking fires twice
        console.log(logger);
        let canplayCounter = 0;
        this.audioPlayer.load();
        this.audioPlayer.currentTime = this.startPosition;

        const seeking = new Promise((resolve) => {
            this.audioPlayer.addEventListener('seeked', () => {
                resolve();
            });
        });
        
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
        let loaded;
        if (this.audioPlayer.currentTime != 0) {
            loaded = Promise.all([seeking, canplay]);
        } else {
            loaded = Promise.all([canplay]);
        }
        
        return loaded.then(this.readyResolver())
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