const buttons = document.querySelectorAll('.ans-btn');

for (const btn of buttons) {
    btn.addEventListener('click', answer);
    console.log('qwertyuio');
}

function answer(e) {
    url = `/`
    let data = {
        "id": e.target.id,
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
        .then((json) => console.log(json))
        .catch((err) => console.error(`Fetch problem: ${err.message}`));

}

function turnGreen(e) {
    e.target.classList.remove('btn-primary')
    e.target.classList.add('btn-success')
}

function turnRed(e) {
    e.target.classList.remove('btn-primary')
    e.target.classList.add('btn-danger')
}