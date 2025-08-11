// Global state
let transactions = []
let nextId = 1

// DOM elements
const modal = document.getElementById("modal")
const form = document.getElementById("transaction-form")
const tbody = document.getElementById("transactions-tbody")
const emptyState = document.getElementById("empty-state")
const grossValueInput = document.getElementById("gross-value")
const ivaRateSelect = document.getElementById("iva-rate")
const typeSelect = document.getElementById("type")
const ivaValueSpan = document.getElementById("iva-value")
const netValueSpan = document.getElementById("net-value")

// Initialize app
document.addEventListener("DOMContentLoaded", () => {
  updateCalculatedValues()
  renderTransactions()

  // Add event listeners
  grossValueInput.addEventListener("input", updateCalculatedValues)
  ivaRateSelect.addEventListener("change", updateCalculatedValues)
  typeSelect.addEventListener("change", updateCalculatedValues)
  form.addEventListener("submit", handleSubmit)
})

// Modal functions
function openModal() {
  modal.classList.add("show")
  document.body.style.overflow = "hidden"
}

function closeModal() {
  modal.classList.remove("show")
  document.body.style.overflow = "auto"
  form.reset()
  updateCalculatedValues()
}

// Navigation
function goBack() {
  // In a real app, this would navigate back
  alert("Voltar à página anterior")
}

// Calculate IVA values
function updateCalculatedValues() {
  const grossValue = Number.parseFloat(grossValueInput.value) || 0
  const ivaRate = Number.parseFloat(ivaRateSelect.value) || 0
  const type = typeSelect.value

  let ivaValue = 0
  let netValue = grossValue

  // Only calculate IVA for "ganho" (income)
  if (type === "ganho" && ivaRate > 0) {
    ivaValue = grossValue * (ivaRate / 100)
    netValue = grossValue - ivaValue
  }

  ivaValueSpan.textContent = formatCurrency(ivaValue)
  netValueSpan.textContent = formatCurrency(netValue)
}

// Format currency
function formatCurrency(value) {
  return new Intl.NumberFormat("pt-PT", {
    style: "currency",
    currency: "EUR",
  }).format(value)
}

// Handle form submission
function handleSubmit(e) {
  e.preventDefault()

  const formData = new FormData(form)
  const grossValue = Number.parseFloat(grossValueInput.value)
  const ivaRate = Number.parseFloat(ivaRateSelect.value)
  const type = typeSelect.value

  let ivaValue = 0
  let netValue = grossValue

  // Calculate IVA only for "ganho"
  if (type === "ganho" && ivaRate > 0) {
    ivaValue = grossValue * (ivaRate / 100)
    netValue = grossValue - ivaValue
  }

  const transaction = {
    id: nextId++,
    type: type,
    description: document.getElementById("description").value,
    grossValue: grossValue,
    ivaRate: ivaRate,
    ivaValue: ivaValue,
    netValue: netValue,
    date: new Date(),
  }

  transactions.push(transaction)
  renderTransactions()
  closeModal()
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

// Delete transaction
function deleteTransaction(id) {
  if (confirm("Tem certeza que deseja eliminar esta transação?")) {
    transactions = transactions.filter((t) => t.id !== id)
    renderTransactions()
  }
}

// Close modal when clicking outside
modal.addEventListener("click", (e) => {
  if (e.target === modal) {
    closeModal()
  }
})

// Close modal with Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && modal.classList.contains("show")) {
    closeModal()
  }
})
