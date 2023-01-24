function cookiesPrompt() {
    // cookies prompt
    const maxAge = 60 * 60 * 24 * 7 * 4 * 12;
    const cookiesBtn = document.querySelector('#cookies-understood')
    const cookiesModal = new bootstrap.Modal('#cookies-prompt', { keyboard: false });

    if (!document.cookie.split(';').find(row => row.startsWith('cookies'))) {
        cookiesModal.show();
    }

    cookiesBtn.addEventListener('click', () => {
        document.cookie = `cookies=true;max-age=${maxAge};samesite=strict`;
        cookiesModal.hide();
    });
};

function setVolume() {
    //remember volume
    const volumeSliders = document.querySelectorAll('.volume-slider');
    const volumeSetting = sessionStorage.getItem('volume');
    for (const slider of volumeSliders) {
        if (!volumeSetting) {
            slider.setAttribute('value', '80');
        } else {
            slider.setAttribute('value', volumeSetting);
        };
        // store volume setting
        slider.addEventListener('input', (e) => {
            sessionStorage.setItem('volume', e.target.value);
        });
    };
    //set audio players volume
    if (volumeSetting) {
        // set remembered volume to audio players
        const audioPlayers = document.querySelectorAll('audio');
        for (const audio of audioPlayers) {
            audio.volume = parseInt(volumeSetting)/100;
        };
    };
};

cookiesPrompt();
setVolume();