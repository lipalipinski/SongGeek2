const rankingTable = document.querySelector('#top-players');

data = {
    "mode":"getRanking"
};
fetch(FETCH_URL, {
    'method': 'POST',
    'headers': { 'Content-Type': 'application/json' },
    'body': JSON.stringify(data)
})
    .then((resp) => {
        if (!resp.ok) {
            const tr = document.createElement(tr);
            tr.innerHTML = '<td colspan="2">ranking failed to load</td>';
            rankingTable.querySelector('tbody').appendChild(tr);
            rankingTable.classList.remove('d-none');
            throw new Error(`HTTP error ${response.status}`);
        };
        return resp.json();
    })
    .then((ranking) => {
        for (user of ranking) {
            // user rank > 10
            if (user.rank > 10) {
                const extraTr = document.createElement('tr');
                extraTr.innerHTML = `<td colspan="4" class="text-center">.<br>.<br>.<br></td>`;
                rankingTable.querySelector('tbody').appendChild(extraTr);
            }
            const tr = document.createElement('tr');
            if (user.current == true) {
                tr.classList.add('text-bg-dark');
            }
            tr.innerHTML = `<td><strong>${user.rank}</strong></td>
                            <td>
                                <img src="${user.imgUrl}" class="usr-img">
                            </td>
                            <td>${user.name}</td>
                            <td><strong>${user.total}</strong></td>`;
            rankingTable.querySelector('tbody').appendChild(tr);
            rankingTable.classList.remove('d-none');
        }
    })