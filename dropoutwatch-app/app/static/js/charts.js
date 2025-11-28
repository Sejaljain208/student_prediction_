// Chart.js utilities and helpers

// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    console.log('DropoutWatch charts initialized');
});

// Helper function to create risk distribution chart
function createRiskChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Low Risk', 'Medium Risk', 'High Risk'],
            datasets: [{
                data: [data.low, data.medium, data.high],
                backgroundColor: ['#28a745', '#ffc107', '#dc3545']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Helper function to update charts dynamically
function updateChartData(chart, newData) {
    chart.data.datasets[0].data = newData;
    chart.update();
}
