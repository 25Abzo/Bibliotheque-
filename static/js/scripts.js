// scripts.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('pretForm');

    form.addEventListener('submit', function(event) {
        const idClient = document.getElementById('id_client').value;
        const montant = document.getElementById('montant').value;
        const taux = document.getElementById('taux').value;
        const duree = document.getElementById('duree').value;
        const mensualite = document.getElementById('mensualite').value;
        const dateAccord = document.getElementById('date_accord').value;
        const jourExigibilite = document.getElementById('jour_exigibilite').value;

        if (!idClient || !montant || !taux || !duree || !mensualite || !dateAccord || !jourExigibilite) {
            event.preventDefault();
            alert('Veuillez remplir tous les champs.');
        }
    });
});
