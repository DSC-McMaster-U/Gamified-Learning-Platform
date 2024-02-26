document.addEventListener("DOMContentLoaded", function () {
    var dropdownLinks = document.querySelectorAll("#dropdown-content a");
    var unitNumberElement = document.getElementById("unit-number");

    dropdownLinks.forEach(function (link) {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            var selectedCourse = link.dataset.unit;
            unitNumberElement.textContent = selectedCourse;
        });
    });
});

$(document).ready(function () {
    google.charts.setOnLoadCallback(initializeGoogleCharts);

    $('.carousel-container').slick({
        infinite: true,
        slidesToShow: 1,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 2000,
        prevArrow: '<button type="button" class="slick-custom-arrow slick-prev"> < </button>',
        nextArrow: '<button type="button" class="slick-custom-arrow slick-next"> > </button>'
    });

    function initializeGoogleCharts() {
        drawClassLengthChart();
        drawActiveChart();
        drawGradeChart();
        drawLessonChart();
        drawQuizChart();
    }

    function drawClassLengthChart() {
        var data = google.visualization.arrayToDataTable([
            ['Time', 'Number of Weeks'],
            ['Weeks Finished', 6],
            ['Weeks Left', 5]
        ]);

        var options = {
            title: 'Course Progress'
        };

        var chart = new google.visualization.PieChart(document.getElementById('class-length-chart'));

        chart.draw(data, options);
    }

    function drawActiveChart() {
        var data = google.visualization.arrayToDataTable([
            ['Active', 'Number of Students'],
            ['Logged On Today', 15],
            ['Logged On in the past 3 days', 8],
            ['Logged On in the past Week', 3],
            ['Inactive for 1 month+', 5]
        ]);

        var options = {
            title: 'Last Login'
        };

        var chart = new google.visualization.PieChart(document.getElementById('active-chart'));

        chart.draw(data, options);
    }

    function drawGradeChart() {
        var data = google.visualization.arrayToDataTable([
            ['Grade', 'Number of Students'],
            ['<50%', 3],
            ['50%-60%', 7],
            ['60%-70%', 10],
            ['70%-80%', 15],
            ['80%-100%', 13]
        ]);

        var options = {
            title: 'Class Grades'
        };

        var chart = new google.visualization.PieChart(document.getElementById('grade-chart'));

        chart.draw(data, options);
    }

    function drawLessonChart() {
        var data = google.visualization.arrayToDataTable([
            ['Lesson Progress', 'Number of Students'],
            ['Have not started', 10],
            ['Finished Lesson 1', 13],
            ['Finished Lesson 2', 17],
            ['Finished Lesson 3', 15],
            ['Finished Lesson 4', 2]
        ]);

        var options = {
            title: 'Lesson Progress'
        };

        var chart = new google.visualization.PieChart(document.getElementById('lesson-chart'));

        chart.draw(data, options);
    }

    function drawQuizChart() {
        var data = google.visualization.arrayToDataTable([
            ['Quiz Progress', 'Number of Students'],
            ['Have not started', 10],
            ['Finished Quiz 1', 15],
            ['Finished Quiz 2', 9],
            ['Finished Quiz 3', 6],
            ['Finished Quiz 4', 0]
        ]);

        var options = {
            title: 'Quiz Progress'
        };

        var chart = new google.visualization.PieChart(document.getElementById('quiz-chart'));

        chart.draw(data, options);
    }
});
