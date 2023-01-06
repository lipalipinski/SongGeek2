// answer buttons
const buttons = document.querySelectorAll('.ans-btn');

for (const btn of buttons) {
    btn.addEventListener('click', answer);
}

// audio player controls
const player = document.querySelector('#player')
const playpause = document.querySelector("#playpause")
const volume = document.querySelector('#volume')

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
    
    for (const btn of buttons) {
        btn.removeEventListener('click', answer);
    }

    player.pause()

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
            console.log(json)
            const points = document.querySelector('#points');
            points.textContent = json.points;
            progbar(document.querySelector('#prog_bar'))
            turnGreen(document.querySelector(`#_${json.green}`));
            turnRed(document.querySelector(`#_${json.red}`));
        })
        .catch((err) => console.error(`Fetch problem: ${err.message}`));
}

function turnGreen(btn) {
    btn.classList.remove('btn-light')
    btn.classList.add('btn-success')
}

function turnRed(btn) {
    btn.classList.remove('btn-light')
    btn.classList.add('btn-danger')
}

function progbar(bar) {
    const prog = document.createElement('div')
    prog.classList.add('progress-bar')
    prog.style.width = '20%'
    bar.appendChild(prog)
}