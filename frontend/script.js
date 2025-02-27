'use strict'

document.addEventListener("DOMContentLoaded", () => {
    const addBookForm = document.getElementById("add-book-form");
    const borrowBookForm = document.getElementById("borrow-book-form");
    const bookList = document.getElementById("book-list");

    // Fonction pour ajouter un livre
    addBookForm.addEventListener("submit", (event) => {
        event.preventDefault();
        
        const title = document.getElementById("book-title").value;
        const author = document.getElementById("book-author").value;
        
        fetch("/books", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ title, author }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert("Livre ajouté !");
            loadBooks(); // Recharger la liste des livres
        })
        .catch(error => {
            console.error("Erreur:", error);
        });
    });

    // Fonction pour emprunter un livre
    borrowBookForm.addEventListener("submit", (event) => {
        event.preventDefault();
        
        const memberId = document.getElementById("member-id").value;
        const bookId = document.getElementById("book-id").value;
        
        fetch("/loans", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ member_id: memberId, book_id: bookId }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert("Livre emprunté !");
        })
        .catch(error => {
            console.error("Erreur:", error);
        });
    });

    // Fonction pour charger la liste des livres
    function loadBooks() {
        fetch("/books")
        .then(response => response.json())
        .then(data => {
            bookList.innerHTML = "";
            data.forEach(book => {
                const li = document.createElement("li");
                li.textContent = `Titre: ${book.title} | Auteur: ${book.author}`;
                bookList.appendChild(li);
            });
        })
        .catch(error => {
            console.error("Erreur:", error);
        });
    }

    loadBooks(); // Charger les livres au chargement de la page
});


/**
 * DASHBOARD
 */
const ctx = document.getElementById('statsChart').getContext('2d');
const statsChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Livres', 'Utilisateurs', 'prêts actifs'],
    datasets: [{
      label: 'Statistiques',
      data: [
        window.dashboardStats.totalBooks, 
        window.dashboardStats.totalMembers, 
        window.dashboardStats.activeLoans
      ],
      /*backgroundColor: ['#0d6efd', '#198754', '#dc3545']*/
    }]
  },
  options: {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

// Gestion du mode sombre/light
const modeToggle = document.getElementById('modeToggle');
modeToggle.addEventListener('change', function() {
    if (this.checked) {
    document.body.classList.add('bg-dark', 'text-white');
    } else {
    document.body.classList.remove('bg-dark', 'text-white');
    }
});

