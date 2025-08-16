// Global variables
let currentChart = null;
let currentMonth = new Date().getMonth(); // Pega o mês atual (0-11)
let currentYear = new Date().getFullYear(); // Pega o ano atual
const months = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    initializeMonthSelector();
    initializeChartSelector();
    loadFinancialData();
    
    // Carregar o gráfico padrão (barras)
    loadChartData('bar');
});

// Month selector functionality
function initializeMonthSelector() {
    const currentMonthElement = document.getElementById('currentMonth');
    const prevBtn = document.getElementById('prevMonth');
    const nextBtn = document.getElementById('nextMonth');
    
    updateMonthDisplay();
    
    prevBtn.addEventListener('click', () => {
        if (currentMonth === 0) {
            currentMonth = 11;
            currentYear--;
        } else {
            currentMonth--;
        }
        updateMonthDisplay();
        loadFinancialData();
        
        // Recarregar gráfico com os novos dados do mês selecionado
        const chartType = document.getElementById('chartType').value;
        loadChartData(chartType);
    });
    
    nextBtn.addEventListener('click', () => {
        if (currentMonth === 11) {
            currentMonth = 0;
            currentYear++;
        } else {
            currentMonth++;
        }
        updateMonthDisplay();
        loadFinancialData();
        
        // Recarregar gráfico com os novos dados do mês selecionado
        const chartType = document.getElementById('chartType').value;
        loadChartData(chartType);
    });
}

function updateMonthDisplay() {
    const currentMonthElement = document.getElementById('currentMonth');
    currentMonthElement.textContent = `${months[currentMonth]} ${currentYear}`;
}

// Load financial data from the server for the current month/year
function loadFinancialData() {
    const company_id = getCompanyId(); // Função para obter o ID da empresa da URL ou de outro lugar
    
    // Mostrar indicador de carregamento
    showLoading(true);
    
    // Fazer requisição para buscar dados do mês atual
    fetch(`/api/financial-summary?company_id=${company_id}&month=${currentMonth + 1}&year=${currentYear}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateFinancialCards(data.summary);
            } else {
                console.error('Erro ao carregar dados:', data.message);
                // Mostrar valores zerados ou mensagem de erro
                resetFinancialCards();
            }
        })
        .catch(error => {
            console.error('Erro na requisição:', error);
            resetFinancialCards();
        })
        .finally(() => {
            showLoading(false);
        });
}

function getCompanyId() {
    // Extrair company_id da URL
    const urlParams = new URLSearchParams(window.location.search);
    const pathParts = window.location.pathname.split('/');
    
    // Tentar obter do parâmetro da URL
    let companyId = urlParams.get('company_id');
    
    // Se não existir, tentar obter do caminho da URL (ex: /dashboard/123)
    if (!companyId && pathParts.length > 2) {
        companyId = pathParts[pathParts.length - 1];
    }
    
    return companyId;
}

function showLoading(isLoading) {
    // Implementar lógica para mostrar/esconder indicador de carregamento
    // Por exemplo:
    const cards = document.querySelectorAll('.card-value, .card-change');
    if (isLoading) {
        cards.forEach(card => {
            card.classList.add('loading');
        });
    } else {
        cards.forEach(card => {
            card.classList.remove('loading');
        });
    }
}

function resetFinancialCards() {
    document.getElementById('revenue-value').textContent = '€0';
    document.getElementById('expenses-value').textContent = '€0';
    document.getElementById('profit-value').textContent = '€0';
    document.getElementById('collaborators-value').textContent = '€0';
    
    document.getElementById('revenue-change').textContent = '0%';
    document.getElementById('expenses-change').textContent = '0%';
    document.getElementById('profit-change').textContent = '0%';
    document.getElementById('collaborators-change').textContent = '0%';
    document.getElementById('vat-value').textContent = '€0';
    document.getElementById('vat-change').textContent = '0%';
    
    // Remover classes de estilo
    document.querySelectorAll('.card-change').forEach(el => {
        el.classList.remove('positive', 'negative', 'neutral');
    });
}

function updateFinancialCards(data) {
    document.getElementById('revenue-value').textContent = formatCurrency(data.total_sales || 0);
    document.getElementById('expenses-value').textContent = formatCurrency(data.total_costs || 0);
    document.getElementById('profit-value').textContent = formatCurrency(data.profit_without_vat || 0);
    document.getElementById('collaborators-value').textContent = formatCurrency(data.total_employee_salaries || 0);
    document.getElementById('vat-value').textContent = formatCurrency(data.total_vat || 0);
    
    updateChangeIndicator('revenue-change', data.sales_change);
    updateChangeIndicator('expenses-change', data.costs_change);
    updateChangeIndicator('profit-change', data.profit_change);
    updateChangeIndicator('collaborators-change', data.employee_costs_change);
    updateChangeIndicator('vat-change', data.vat_change);
}

function updateChangeIndicator(elementId, changeValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Se não houver valor de mudança, mostrar neutro
    if (changeValue === undefined || changeValue === null) {
        element.textContent = '0%';
        element.className = 'card-change neutral';
        return;
    }
    
    // Formatar com sinal + ou -
    const formattedChange = (changeValue > 0 ? '+' : '') + changeValue.toFixed(1) + '%';
    element.textContent = formattedChange;
    
    // Adicionar classe apropriada
    element.className = 'card-change';
    if (changeValue > 0) {
        element.classList.add('positive');
    } else if (changeValue < 0) {
        element.classList.add('negative');
    } else {
        element.classList.add('neutral');
    }
}

function formatCurrency(value) {
    return '€' + Number(value).toLocaleString('pt-PT', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
}

// Chart functionality
function initializeChartSelector() {
    const chartSelector = document.getElementById('chartType');
    if (chartSelector) {
        chartSelector.addEventListener('change', (e) => {
            loadChartData(e.target.value);
        });
    }
}

function loadChartData(chartType) {
    const company_id = getCompanyId();
    
    // Mostrar indicador de carregamento no gráfico
    showChartLoading(true);
    
    // Fazer requisição para buscar dados do gráfico
    fetch(`/api/chart-data?company_id=${company_id}&type=${chartType}&month=${currentMonth + 1}&year=${currentYear}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                createChart(chartType, data.chartData);
            } else {
                console.error('Erro ao carregar dados do gráfico:', data.message);
                showChartError();
            }
        })
        .catch(error => {
            console.error('Erro na requisição:', error);
            showChartError();
        })
        .finally(() => {
            showChartLoading(false);
        });
}

function createChart(type, data) {
    const ctx = document.getElementById('mainChart').getContext('2d');
    
    // Destroy existing chart
    if (currentChart) {
        currentChart.destroy();
    }
    
    const config = {
        type: type === 'line' ? 'line' : type,
        data: data,
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

function showChartLoading(isLoading) {
    const chartContainer = document.querySelector('.chart-container');
    
    if (isLoading) {
        // Adicionar indicador de carregamento
        if (!document.getElementById('chart-loading')) {
            const loadingElement = document.createElement('div');
            loadingElement.id = 'chart-loading';
            loadingElement.className = 'chart-loading';
            loadingElement.innerHTML = `
                <div class="spinner"></div>
                <p>Carregando dados...</p>
            `;
            chartContainer.appendChild(loadingElement);
        }
    } else {
        // Remover indicador de carregamento
        const loadingElement = document.getElementById('chart-loading');
        if (loadingElement) {
            loadingElement.remove();
        }
    }
}

function showChartError() {
    const ctx = document.getElementById('mainChart').getContext('2d');
    
    // Destroy existing chart
    if (currentChart) {
        currentChart.destroy();
        currentChart = null;
    }
    
    // Limpar o canvas
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    
    // Desenhar mensagem de erro
    ctx.font = '16px Arial';
    ctx.textAlign = 'center';
    ctx.fillStyle = '#ef4444';
    ctx.fillText('Erro ao carregar dados do gráfico', ctx.canvas.width / 2, ctx.canvas.height / 2);
}

// Animation effects for cards
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
  const pathParts = window.location.pathname.split('/');
  const company_id = pathParts[pathParts.length - 1];
  window.location.href = `/main-menu/${company_id}`;
}

function handleLogout() {
  window.location.href = '/logout';
}