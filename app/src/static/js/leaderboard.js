let currentPage = 1;
const pageSize = 8;

function fetchLeaderBoard(page) {
    fetch('/leaderboard')
        .then(response => {
            return response.json();
        })
        .then(data => {
            renderLeaderboard(data);
        })
        .catch(error => console.log(error));
}

function renderLeaderboard(data) {
    const tableBody = document.getElementById('table-body');
    tableBody.innerHTML = '';

    data.slice(0,8).forEach((entry, index) => {
        const tableRow = `
            <tr class="table-entry" id="rank-${(currentPage - 1) * pageSize + index + 1}">
                <td class="entry-ranking">${(currentPage - 1) * pageSize + index + 1}</td>
                <td class="entry-username">${entry.username}</td>
                <td class="entry-points">${entry.points}</td>
            </tr>`;
        tableBody.innerHTML += tableRow;
    });
}

function loadNextPage() {
    currentPage++;
    fetchLeaderBoard(currentPage);
}

fetchLeaderBoard(currentPage);