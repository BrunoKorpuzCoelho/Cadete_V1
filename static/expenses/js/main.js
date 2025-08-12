let transactions = []
let nextId = 1

const modal = document.getElementById("modal")
const form = document.getElementById("transaction-form")
const tbody = document.getElementById("transactions-tbody")
const emptyState = document.getElementById("empty-state")
const grossValueInput = document.getElementById("gross-value")
const ivaRateSelect = document.getElementById("iva-rate")
const typeSelect = document.getElementById("type")
const ivaValueSpan = document.getElementById("iva-value")
const netValueSpan = document.getElementById("net-value")
const ivaValueInput = document.getElementById("iva-value-input")
const netValueInput = document.getElementById("net-value-input")
const ivaRateGroup = document.querySelector('.form-group:has(#iva-rate)') || ivaRateSelect.closest('.form-group')
const userType = document.body.getAttribute('data-user-type') || 'user'

document.addEventListener("DOMContentLoaded", () => {
  updateCalculatedValues()
  renderTransactions()

  grossValueInput.addEventListener("input", updateCalculatedValues)
  ivaRateSelect.addEventListener("change", updateCalculatedValues)
  
  typeSelect.addEventListener("change", handleTypeChange)
  
  form.addEventListener("submit", handleSubmit)
  
  updateIvaFieldVisibility()
})

function openModal() {
  modal.classList.add("show")
  document.body.style.overflow = "hidden"
  
  updateIvaFieldVisibility()
}

function closeModal() {
  modal.classList.remove("show")
  document.body.style.overflow = "auto"
  form.reset()
  updateCalculatedValues()
  updateIvaFieldVisibility()
}

function handleTypeChange() {
  const type = typeSelect.value
  
  if (type === "despesa") {
    ivaRateSelect.value = "0"
  }
  
  updateIvaFieldVisibility()
  
  updateCalculatedValues()
}

function updateIvaFieldVisibility() {
  const type = typeSelect.value;
  
  if (!ivaRateGroup) return; 
  
  if (type === "despesa" && userType !== 'Admin') {
    ivaRateGroup.style.display = 'none';
  } else {
    ivaRateGroup.style.display = 'block';
  }
  
  if (type === "despesa") {
    ivaRateSelect.value = "0";
  }
}

function goBack() {
  window.history.back() || alert("Voltar à página anterior")
}

function updateCalculatedValues() {
  const grossValue = Number.parseFloat(grossValueInput.value) || 0
  const ivaRate = Number.parseFloat(ivaRateSelect.value) || 0
  const type = typeSelect.value

  let ivaValue = 0
  let netValue = grossValue

  if (type === "ganho" && ivaRate > 0) {
    ivaValue = grossValue * (ivaRate / 100)
    netValue = grossValue - ivaValue
  }

  // Atualizar os spans visíveis
  ivaValueSpan.textContent = formatCurrency(ivaValue)
  netValueSpan.textContent = formatCurrency(netValue)
  
  // Atualizar os campos ocultos
  ivaValueInput.value = ivaValue.toFixed(2)
  netValueInput.value = netValue.toFixed(2)
}

function formatCurrency(value) {
  return new Intl.NumberFormat("pt-PT", {
    style: "currency",
    currency: "EUR",
  }).format(value)
}

function handleLogout() {
  window.location.href = '/logout'
}

function handleSubmit(e) {
  // Não prevenir o comportamento padrão, permitindo que o formulário seja enviado
  // Mas garantir que os valores calculados estão atualizados nos campos ocultos
  const grossValue = Number.parseFloat(grossValueInput.value) || 0
  const ivaRate = Number.parseFloat(ivaRateSelect.value) || 0
  const type = typeSelect.value

  let ivaValue = 0
  let netValue = grossValue

  if (type === "ganho" && ivaRate > 0) {
    ivaValue = grossValue * (ivaRate / 100)
    netValue = grossValue - ivaValue
  }

  // Atualizar os campos ocultos antes do envio
  ivaValueInput.value = ivaValue.toFixed(2)
  netValueInput.value = netValue.toFixed(2)
  
  // O formulário será enviado normalmente para o backend
}

// Função para buscar as transações da API (a ser implementada)
function fetchTransactions() {
  // Implementação futura para buscar dados do backend
  fetch('/api/expenses')
    .then(response => response.json())
    .then(data => {
      transactions = data;
      renderTransactions();
    })
    .catch(error => console.error('Erro ao buscar transações:', error));
}

// Render transactions table
function renderTransactions() {
  if (transactions.length === 0) {
    tbody.innerHTML = ""
    emptyState.style.display = "block"
    return
  }

  emptyState.style.display = "none"

  tbody.innerHTML = transactions
    .map(
      (transaction) => `
        <tr>
            <td>
                <span class="type-badge type-${transaction.type}">
                    ${transaction.type === "ganho" ? "Ganho" : "Despesa"}
                </span>
            </td>
            <td>${transaction.description}</td>
            <td>${formatCurrency(transaction.grossValue)}</td>
            <td>${transaction.ivaRate}%</td>
            <td>${formatCurrency(transaction.ivaValue)}</td>
            <td>${formatCurrency(transaction.netValue)}</td>
            <td>
                <button class="delete-btn" onclick="deleteTransaction(${transaction.id})">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3,6 5,6 21,6"></polyline>
                        <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
                    </svg>
                </button>
            </td>
        </tr>
    `,
    )
    .join("")
}

function deleteTransaction(id) {
  if (confirm("Tem certeza que deseja eliminar esta transação?")) {
    transactions = transactions.filter((t) => t.id !== id)
    renderTransactions()
  }
}

modal.addEventListener("click", (e) => {
  if (e.target === modal) {
    closeModal()
  }
})

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && modal.classList.contains("show")) {
    closeModal()
  }
})