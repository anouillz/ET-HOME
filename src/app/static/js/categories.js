document.addEventListener("DOMContentLoaded", function () {
    let categoryToDelete = null;
    let categoryNameToDelete = "";

    // Sélection des modales et boutons
    const confirmDeleteModal = document.getElementById("confirm-delete-modal");
    const successDeleteModal = document.getElementById("success-delete-modal");
    const confirmDeleteBtn = document.getElementById("confirm-delete-btn");
    const cancelDeleteBtn = document.getElementById("cancel-delete-btn");
    const closeSuccessModal = document.getElementById("close-success-modal");
    const successDeleteMessage = document.getElementById("success-delete-message");

    // ✅ Assurer que les modales sont cachées au chargement de la page
    document.getElementById("budget-modal").style.display = "none";
    document.getElementById("confirm-delete-modal").style.display = "none";
    document.getElementById("success-delete-modal").style.display = "none";

    // 🔥 Ajout d'une nouvelle catégorie
    document.getElementById("add-category-btn").addEventListener("click", function () {
        const categoryName = prompt("Enter category name:");
        if (!categoryName) return;  // Si l'utilisateur annule

        const categoryBudget = prompt("Enter category budget:");
        if (!categoryBudget) return;

        fetch("/categories/add/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: `name=${encodeURIComponent(categoryName)}&user_budget=${encodeURIComponent(categoryBudget)}`,
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.status === "success") {
                console.log("✅ Category added successfully!");
                location.reload(); // Recharger la page pour afficher la nouvelle catégorie
            } else {
                console.error("🔴 Error adding category:", data.message);
            }
        })
        .catch((error) => {
            console.error("🔴 Error:", error);
        });
    });

    // 🔥 Mise à jour du budget avec la touche "Enter"
    document.querySelectorAll(".category-budget").forEach((input) => {
        input.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();

                const categoryId = this.dataset.id;
                const newBudget = this.value;
                const categoryName = this.closest(".category-item").querySelector(".category-name").innerText;

                fetch("/categories/update_budget/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-CSRFToken": getCookie("csrftoken"),
                    },
                    body: `category_id=${encodeURIComponent(categoryId)}&new_budget=${encodeURIComponent(newBudget)}`,
                })
                .then((response) => response.json())
                .then((data) => {
                    if (data.status === "success") {
                        document.getElementById("modal-message").innerText = `Budget for ${categoryName} updated to ${newBudget} CHF`;
                        document.getElementById("budget-modal").style.display = "flex";
                    }
                })
                .catch((error) => {
                    console.error("🔴 Error:", error);
                });
            }
        });
    });

    // 🔥 Suppression de catégorie avec modale
    document.querySelectorAll(".delete-category").forEach((button) => {
        button.addEventListener("click", function () {
            categoryToDelete = this.dataset.id;
            categoryNameToDelete = this.closest(".category-item").querySelector(".category-name").innerText;

            // Afficher la boîte modale de confirmation
            confirmDeleteModal.style.display = "flex";
        });
    });

    // ✅ Si l'utilisateur clique sur "Yes" pour supprimer
    confirmDeleteBtn.addEventListener("click", function () {
        if (!categoryToDelete) return;

        fetch("/categories/delete/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: `category_id=${encodeURIComponent(categoryToDelete)}`,
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.status === "success") {
                console.log("✅ Category deleted successfully!");

                // Cacher la modale de confirmation
                confirmDeleteModal.style.display = "none";

                // Mettre le message et afficher la modale de succès
                successDeleteMessage.innerText = `Category "${categoryNameToDelete}" deleted successfully!`;
                successDeleteModal.style.display = "flex";
            } else {
                console.error("🔴 Error deleting category:", data.message);
            }
        })
        .catch((error) => {
            console.error("🔴 Error:", error);
        });
    });

    // ✅ Si l'utilisateur clique sur "No", fermer la modale
    cancelDeleteBtn.addEventListener("click", function () {
        confirmDeleteModal.style.display = "none";
    });

    // ✅ Si l'utilisateur clique sur "OK" après suppression, fermer la modale et recharger
    closeSuccessModal.addEventListener("click", function () {
        successDeleteModal.style.display = "none";
        location.reload();
    });

    // 🔥 Activation/Désactivation d'une catégorie avec la checkbox
    document.querySelectorAll(".toggle-category").forEach((checkbox) => {
        checkbox.addEventListener("change", function () {
            const categoryId = this.dataset.id;
            const isActive = this.checked; // true si la case est cochée

            fetch("/categories/toggle/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: `category_id=${encodeURIComponent(categoryId)}&is_active=${isActive}`,
            })
            .then((response) => response.json())
            .then((data) => {
                if (data.status === "success") {
                    console.log(`✅ Category ${categoryId} toggled to ${isActive}`);
                } else {
                    console.error("🔴 Error toggling category:", data.message);
                }
            })
            .catch((error) => {
                console.error("🔴 Error:", error);
            });
        });
    });

    // ✅ Bouton pour fermer la boîte modale du budget
    document.getElementById("close-modal").addEventListener("click", function () {
        document.getElementById("budget-modal").style.display = "none";
    });
});

// 🔥 Fonction pour récupérer le token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
