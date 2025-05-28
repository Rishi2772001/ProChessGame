document.addEventListener("DOMContentLoaded", function() {
    function fetchData() {
        fetch(currentGameStatusUrl)  // Use the variable set in the HTML
        .then(response => response.json())
        .then(data => {
            document.getElementById('activeGames').innerHTML = `Active Games: ${data.active_games}`;
            document.getElementById('loggedInUsers').innerHTML = `Logged-In Users: ${data.logged_in_users}`;
            document.getElementById('turn-info').textContent = 'It is ' + data.current_turn + "'s turn.";
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    setInterval(fetchData, 1000); 
});

function resignGame() {
    $.ajax({
        url: "{% url 'resign_game' game.id %}",
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        },
        success: function () {
            window.location.href = "{% url 'home' %}";
        },
        error: function () {
            alert('Error resigning from game.');
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    setInterval(checkGameStatus, 1000); 
});

