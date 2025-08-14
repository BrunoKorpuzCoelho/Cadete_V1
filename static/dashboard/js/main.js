function handleCardClick(cardType) {
    console.log(`Clicked on: ${cardType} for company: ${companyId}`);
    
    if (cardType === 'adicionar-transacao') {
        window.location.href = `/expenses/${companyId}`;
    } else if (cardType === 'configurar-orcamento') {
        window.location.href = `/employee/${companyId}`;
    } else if (cardType === 'despesas-mensais') {
        window.location.href = `/dashboard/${companyId}`;  
    } else {
        alert(`Funcionalidade "${cardType}" será implementada em breve!`);
    }
}

function handleLogout() {
    window.location.href = '/logout';
}

document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('touchstart', function() {
        this.style.transform = 'scale(0.95)';
    });
    
    card.addEventListener('touchend', function() {
        setTimeout(() => {
            this.style.transform = 'scale(1)';
        }, 100);
    });
});

function goBack() {
  window.location.href = '/company';
}