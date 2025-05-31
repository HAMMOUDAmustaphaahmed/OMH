// Fonction pour formater les dates
Date.prototype.format = function(format) {
    const monthNames = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"];
    
    switch(format) {
        case 'd/m/Y':
            return `${this.getDate().toString().padStart(2, '0')}/${(this.getMonth() + 1).toString().padStart(2, '0')}/${this.getFullYear()}`;
        case 'MMMM YYYY':
            return `${monthNames[this.getMonth()]} ${this.getFullYear()}`;
        default:
            return this.toString();
    }
};

// Fonction pour formater les nombres en devise
Number.prototype.currency = function() {
    return this.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
};

// Initialisation des composants
document.addEventListener('DOMContentLoaded', function() {
    // Affichage des notifications
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            message.classList.remove('show');
        }, 5000);
    });

    // Animation des cartes
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
        }, 100 * index);
    });

    // Gestion des formulaires
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enregistrement...';
        });
    });

    // Gestion des onglets
    const tabs = document.querySelectorAll('.tabs');
    tabs.forEach(tabContainer => {
        const tabButtons = tabContainer.querySelectorAll('.tab-button');
        const tabContents = tabContainer.querySelectorAll('.tab-content');
        
        tabButtons.forEach((button, index) => {
            button.addEventListener('click', () => {
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                button.classList.add('active');
                tabContents[index].classList.add('active');
            });
        });
    });

    // Ajout de l'ombre aux éléments au survol
    const hoverElements = document.querySelectorAll('.card, .widget, .trip-item');
    hoverElements.forEach(element => {
        element.addEventListener('mouseenter', () => {
            element.style.boxShadow = '0 8px 20px rgba(0, 0, 0, 0.15)';
            element.style.transform = 'translateY(-5px)';
        });
        
        element.addEventListener('mouseleave', () => {
            element.style.boxShadow = '';
            element.style.transform = '';
        });
    });
});