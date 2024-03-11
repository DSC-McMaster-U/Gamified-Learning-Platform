document.addEventListener('DOMContentLoaded', function() {
    fetchAndDisplayQuizScores();
});

function fetchAndDisplayQuizScores() {
    // Replace '/quizzes?user_assigned=true' with the correct endpoint if different
    fetch('/quizzes?user_assigned=true', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            // Add any necessary headers, such as authentication tokens
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const quizScoresContainer = document.getElementById('quiz-scores-container');
        // Clear previous content
        quizScoresContainer.innerHTML = '';

        // Check if there are any quizzes returned
        if (data.length === 0) {
            quizScoresContainer.innerHTML = '<p>No quiz scores available.</p>';
            return;
        }

        // Dynamically create and insert elements for each quiz score
        data.forEach(quiz => {
            const quizElement = document.createElement('div');
            quizElement.className = 'quiz-score-item';
            quizElement.innerHTML = `
                <strong>${quiz.title}</strong>: ${quiz.score} points
            `;
            quizScoresContainer.appendChild(quizElement);
        });
    })
    .catch(error => {
        console.error('Error fetching quiz scores:', error);
        document.getElementById('quiz-scores-container').innerHTML = '<p>Error loading quiz scores.</p>';
    });
}
