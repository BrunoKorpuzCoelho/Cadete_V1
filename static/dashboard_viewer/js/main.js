// Global variables
let currentChart = null;
let currentMonth = 0;
const months = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];

// Sample data
const financialData = {
    bar: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
        datasets: [
            {
                label: 'Receitas',
                data: [12450, 13200, 11800, 14500, 13900, 15200],
                backgroundColor: '#22c55e',
                borderRadius: 4
            },
            {
                label: 'Despesas',
                data: [8320, 8900, 7800, 9200, 8700, 9500],
                backgroundColor: '#f59e0b',
                borderRadius: 4
            },
            {
                label: 'Custos Colaboradores',
                data: [4250, 4250, 4250, 4500, 4500, 4750],
                backgroundColor: '#8b5cf6',
                borderRadius: 4
            }
        ]
    },
    pie: {
        labels: ['Produto A', 'Produto B', 'Produto C', 'Serviços', 'Outros'],
        datasets: [{
            data: [35, 25, 20, 15, 5],
            backgroundColor: [
                '#22c55e',
                '#3b82f6',
                '#f59e0b',
                '#ef4444',
                '#8b5cf6'
            ],
            borderWidth: 0
        }]
    },
    line: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
        datasets: [{
            label: 'Performance Financeira',
            data: [4130, 4300, 4000, 5300, 5200, 5700],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#3b82f6',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 6
        }]
    }
};

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    initializeMonthSelector();
    initializeChartSelector();
    createChart('bar');
});

// Month selector functionality
function initializeMonthSelector() {
    const currentMonthElement = document.getElementById('currentMonth');
    const prevBtn = document.getElementById('prevMonth');
    const nextBtn = document.getElementById('nextMonth');
    
    updateMonthDisplay();
    
    prevBtn.addEventListener('click', () => {
        currentMonth = currentMonth === 0 ? 11 : currentMonth - 1;
        updateMonthDisplay();
        updateFinancialData();
    });
    
    nextBtn.addEventListener('click', () => {
        currentMonth = currentMonth === 11 ? 0 : currentMonth + 1;
        updateMonthDisplay();
        updateFinancialData();
    });
}

function updateMonthDisplay() {
    const currentMonthElement = document.getElementById('currentMonth');
    currentMonthElement.textContent = `${months[currentMonth]} 2024`;
}

function updateFinancialData() {
    // Simulate data changes based on month
    const variation = Math.random() * 0.2 - 0.1; // ±10% variation
    const cards = document.querySelectorAll('.card-value');
    const baseValues = [12450, 8320, 4130, 4250];
    
    cards.forEach((card, index) => {
        const newValue = Math.round(baseValues[index] * (1 + variation));
        card.textContent = `€${newValue.toLocaleString()}`;
    });
}

// Chart functionality
function initializeChartSelector() {
    const chartSelector = document.getElementById('chartType');
    chartSelector.addEventListener('change', (e) => {
        createChart(e.target.value);
    });
}

function createChart(type) {
    const ctx = document.getElementById('mainChart').getContext('2d');
    
    // Destroy existing chart
    if (currentChart) {
        currentChart.destroy();
    }
    
    const config = {
        type: type === 'line' ? 'line' : type,
        data: financialData[type],
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            },
            scales: type !== 'pie' ? {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#f1f5f9'
                    },
                    ticks: {
                        callback: function(value) {
                            return '€' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            } : {}
        }
    };
    
    // Special configuration for line chart
    if (type === 'line') {
        config.options.elements = {
            point: {
                hoverRadius: 8
            }
        };
    }
    
    currentChart = new Chart(ctx, config);
}

document.querySelectorAll('.summary-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-4px)';
        this.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.15)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
    });
});

function goBack() {
  window.history.back()
}

function handleLogout() {
  window.location.href = '/logout'
}