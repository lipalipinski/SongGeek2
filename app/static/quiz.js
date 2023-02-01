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
            
            const quiz = new QuizPlayer(resp["quests"], resp["gameId"]);
            
        })
        .catch((err) => console.error(`Fetch problem: ${err.message}`));
}

function QuizPlayer(quests, gameId) {
    // init audio players
    this.gameId = gameId;
    this.state = 0;
    this.points = 0;
    this.players = [];

    this.nextQuest = function () {
        // quest counter
        document.querySelector('#quest_num').innerText = this.state + 1;
        // points counter
        return this.players[this.state].setAnswers();
    };

    this.updatePoints = function () {
        document.querySelector('#points').innerText = this.points;
    }

    this.progbar = function (green = true) {
        const prog = document.createElement('div');
        prog.classList.add('progress-bar');
        prog.style.width = '20%';
        if (green) {
            prog.classList.add('bg-success');
        } else {
            prog.classList.add('bg-danger');
        }
        document.querySelector('#prog_bar').appendChild(prog);
    }

    // controlBtnStatus
    this.controlBtnStatus = function (state, message=' ') {
        const btn = document.querySelector('#playpause');
        btn.innerText = message;
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
        };
    };

    this.scrollToShowBtns = function () {
        document.querySelector('#quiz-card').scrollIntoView(false);  
    };

    this.controlBtnStatus('loading');

    // init players
    for (const quest of quests) {
        this.players.push(new Player(quest))
    };
    
    // load audio chain
    let loadChain = Promise.resolve();
    for ( player of this.players) {
        loadChain = loadChain
        .then(player.loadAudio())
    };
    
    this.updatePoints();
    removePlaceholder();
    showCard();

    // GAME CHAIN
    let gameChain = Promise.resolve();
    for (const player of this.players) {
        // wait for answer
        // first quest
        if (player.qNum == 0) {
                gameChain = gameChain
                    .then(() => {
                        this.controlBtnStatus('play');
                        const currentPlayer = this.players[this.state];

                        const answer = this.nextQuest();
                        this.scrollToShowBtns();

                        document.querySelector('#playpause').addEventListener('click', () => {
                            this.controlBtnStatus('loading');
                            currentPlayer.startPlayback();
                            this.state++;
                        }, { once: true });
                        return answer;
                    })
        } else {
            gameChain = gameChain
                .then(() => {
                    this.controlBtnStatus('play');
                    const currentPlayer = this.players[this.state];

                    
                    const answer = new Promise((resolve) => {
                        document.querySelector('#playpause').addEventListener('click', () => {
                            this.controlBtnStatus('loading');
                            currentPlayer.startPlayback();
                            this.nextQuest().then((answer) => resolve(answer))
                            this.state++;
                        }, { once: true });
                    })
                    
                    return answer
                })
        };
        // update game info after answer
        gameChain = gameChain
            .then((resp) => {
                // turn button green
                const green = document.querySelector(`#_${resp['green']}`);
                green.classList.replace('btn-light', 'btn-success');
                green.classList.add('opacity-100');

                // turn button red
                if (resp["red"] != "") {
                    const red = document.querySelector(`#_${resp["red"]}`);
                    red.classList.replace('btn-light', 'btn-danger');
                    red.classList.add('opacity-100')
                    // red progbar
                    this.progbar(false);
                } else {
                    // green progbar
                    this.progbar();
                }

                // show score badge
                if (resp["points"] > 0) {
                    const badge = document.querySelector(`#_${resp["green"]} span`);
                    badge.classList.remove('d-none');
                    badge.textContent = '+' + resp["points"];
                };

                // score update
                this.points += resp["points"];
                this.updatePoints();
            })
        // not last quest
        if (player.qNum != 4) {
            gameChain = gameChain
                .then(() => {
                    this.controlBtnStatus('after-countdown', 'NEXT');
                })
        } else {
            // last quest
            gameChain = gameChain
                .then(() => {
                    this.controlBtnStatus('results');
                    const resultsUrl = window.location.href + '/' + this.gameId;
                    document.querySelector('#results').setAttribute('href', resultsUrl);
            })
        }
    };

};

function Player(quest) {
    const that = this;
    this.qNum = quest["qNum"];
    this.tracks = quest["tracks"];
    this.audioPlayer = new Audio();
    this.audioPlayer.preload = 'none';
    this.audioPlayer.src = quest["prevUrl"];
    // volume slider
    this.volume = document.querySelector('#volume');
    // mute button
    this.mute = document.querySelector('#mute');
    // set volume from slider
    this.audioPlayer.volume = this.volume.value / 100; 
    this.startPosition = Math.floor(Math.random() * 25);
    this.score = 5;
    this.readyResolver;
    this.ready = new Promise((resolve) => {
        this.readyResolver = resolve;
    })
    
    this.setMuteImg = function () {
        // set mute img
        if (this.volume.value < 100 / 3) {
            this.mute.setAttribute('data-state', 'vol-1');
        } else if (this.volume.value > 200 / 3) {
            this.mute.setAttribute('data-state', 'vol-3');
        } else {
            this.mute.setAttribute('data-state', 'vol-2');
        };
    };
    
    this.setMuteImg();

    // toggle mute 
    this.mute.addEventListener('click', (e) => {
        if (!this.audioPlayer.muted) {
            this.audioPlayer.muted = true;
            e.target.setAttribute('data-state', 'muted');
        } else {
            this.audioPlayer.muted = false;
            this.setMuteImg();
        };
    })

    // volume slider
    this.volume.addEventListener('input', (e) => {
        this.audioPlayer.volume = e.target.value / 100;
        this.setMuteImg();
    });

    //enable answer
    this.enableBtns = function (enable = true) {
        for (const [i, btn] of document.querySelectorAll('.ans-btn').entries()) {
            if (enable == true) {
                btn.classList.remove('disabled');
            } else {
                btn.classList.add('disabled');
            }
        };
    };

    this.loadAudio = function () {
        // count canplay events, if seeking fires twice
        let canplayCounter = 0;
        this.audioPlayer.preload = 'auto';
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

        loaded.then(() => {
            return this.readyResolver()
        })

    };

    // answer btns
    this.setAnswers = function () {
        const answer = new Promise((resolve, reject) => {
            for (const [i, btn] of document.querySelectorAll('.ans-btn').entries()) {
                btn.classList.replace('btn-success', 'btn-light');
                btn.classList.replace('btn-danger', 'btn-light');
                btn.classList.remove('opacity-100');
                btn.setAttribute('id', `_${this.tracks[i]["id"]}`);
                btn.setAttribute('value', `${this.tracks[i]["id"]}`);
                btn.innerText = this.tracks[i]["name"];
                
                // score badge
                const badge = document.createElement('span');
                badge.classList.add('d-none', 'position-absolute', 'top-0', 'start-100', 'translate-middle', 'badge', 'rounded-pill', 'bg-danger');
                btn.appendChild(badge);
                
                btn.addEventListener('click', (e) => {
                    this.enableBtns(false);
                    this.stopPlayback();
                    // loading spinner 
                    const playBtn = document.querySelector('#playpause')
                    const spinner = document.createElement('div');
                    spinner.classList.add('spinner-border');
                    spinner.setAttribute('role', 'status');
                    playBtn.setAttribute('data-state', 'loading');
                    playBtn.appendChild(spinner);

                    // disable butons
                    const data = {
                        "mode": "nextQuest",
                        "qNum": this.qNum,
                        "id": e.target.value,
                        "score": this.score
                    }
                    const resp = fetch(window.location.href, {
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
                        return resolve(resp)
                    }, {once:true});
            };
        });
        return answer.then((answer) => {
            // clone remove event listeners from btns after answering
            for (const btn of document.querySelectorAll('.ans-btn')) {
                const newBtn = btn.cloneNode(true);
                btn.parentNode.replaceChild(newBtn, btn);
            };
            return answer;
        });
    };

    this.startPlayback = function () {
        console.log(this.ready)
        const timer = setTimeout(() => {
            if (this.audioPlayer.paused) {
                this.loadAudio();
            }
        }, 1500);
        this.ready
            .then(() => {
            this.audioPlayer.play();
            // start countdown only after audio play
                this.audioPlayer.addEventListener('play', () => {
                    clearTimeout(timer);
                    document.querySelector('#playpause').setAttribute('data-state', 'countdown');
                document.querySelector('#playpause').innerText = this.score;
                this.enableBtns();
                this.timer = setInterval(() => {
                    this.score--;
                    document.querySelector('#playpause').innerText = this.score;
                    if (this.score == 0) {
                        this.stopPlayback();
                        document.querySelector('#playpause').innerText = "TIME'S OUT";
                    };
                }, 1000);
            });
            });
    };

    this.stopPlayback = function () {
        clearInterval(this.timer);
        document.querySelector('#playpause').innerText = ' ';
        document.querySelector('#playpause').setAttribute('data-state', 'after-countdown');
        this.audioPlayer.pause();
    };
};

function removePlaceholder() {
    document.querySelector('.load-card').remove();
};

function showCard() {
    document.querySelector('#quiz-card').classList.remove('d-none');
}


get_quiz();