const ctx = document.getElementById('watchChart');

new Chart(ctx, {
    type: 'line',

    data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],

        datasets: [{
            label: 'Minutos',

            data: [30, 22, 44, 12, 35, 50, 28],

            tension: 0.4,

            fill: true,

            borderColor: '#ff5b2e',

            backgroundColor: 'rgba(255,91,46,0.15)',

            pointBackgroundColor: '#ff5b2e',

            pointRadius: 5
        }]
    },

    options: {
        responsive: true,

        plugins: {
            legend: {
                display: false
            }
        },

        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});