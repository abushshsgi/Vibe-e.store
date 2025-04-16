// Charts for admin dashboard using Chart.js

// Initialize charts
function initCharts() {
    // Set default Chart.js options
    Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue('--admin-text-color').trim();
    Chart.defaults.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--admin-border-color').trim();
    
    // Initialize chart canvases with empty data
    // They will be populated via API calls
    initDailyViewsChart();
    initProductViewsChart();
    initProductClicksChart();
}

// Daily Views Chart
let dailyViewsChart;
function initDailyViewsChart() {
    const ctx = document.getElementById('dailyActivityChart');
    if (!ctx) return;
    
    dailyViewsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Views',
                data: [],
                backgroundColor: 'rgba(20, 110, 180, 0.2)',
                borderColor: 'rgba(20, 110, 180, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(20, 110, 180, 1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

function updateDailyViewsChart(labels, data) {
    if (!dailyViewsChart) return;
    
    dailyViewsChart.data.labels = labels;
    dailyViewsChart.data.datasets[0].data = data;
    dailyViewsChart.update();
}

// Product Views Chart (Pie Chart)
let productViewsChart;
function initProductViewsChart() {
    const ctx = document.getElementById('viewsByProductChart');
    if (!ctx) return;
    
    productViewsChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    'rgba(255, 153, 0, 0.8)',
                    'rgba(20, 110, 180, 0.8)',
                    'rgba(40, 167, 69, 0.8)',
                    'rgba(220, 53, 69, 0.8)',
                    'rgba(255, 193, 7, 0.8)'
                ],
                borderColor: 'rgba(255, 255, 255, 0.5)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} views (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function updateProductViewsChart(labels, data) {
    if (!productViewsChart) return;
    
    productViewsChart.data.labels = labels;
    productViewsChart.data.datasets[0].data = data;
    productViewsChart.update();
}

// Product Clicks Chart (Bar Chart)
let productClicksChart;
function initProductClicksChart() {
    const ctx = document.getElementById('clicksByProductChart');
    if (!ctx) return;
    
    productClicksChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Clicks',
                data: [],
                backgroundColor: 'rgba(255, 153, 0, 0.7)',
                borderColor: 'rgba(255, 153, 0, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                },
                x: {
                    ticks: {
                        callback: function(value) {
                            const label = this.getLabelForValue(value);
                            return truncateAxisLabel(label, 15);
                        }
                    }
                }
            }
        }
    });
}

function updateProductClicksChart(labels, data) {
    if (!productClicksChart) return;
    
    productClicksChart.data.labels = labels;
    productClicksChart.data.datasets[0].data = data;
    productClicksChart.update();
}

// Utility: Truncate axis label
function truncateAxisLabel(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}
