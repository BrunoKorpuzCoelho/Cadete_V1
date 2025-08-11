function handleCardClick(cardType) {
    console.log(`Clicked on: ${cardType}`);
    
    if (cardType === 'adicionar-transacao') {
        window.location.href = '/expenses';
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