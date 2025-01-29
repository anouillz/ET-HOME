document.addEventListener("DOMContentLoaded", function () {
    // Add Category
    document.getElementById("add-category-btn").addEventListener("click", function () {
        const categoryName = prompt("Enter category name:");
        const categoryBudget = prompt("Enter category budget:");

        if (!categoryName || !categoryBudget) {
            alert("Both name and budget are required.");
            return;
        }

        fetch("/categories/add/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCookie("csrftoken"), // Include CSRF token
            },
            body: `name=${encodeURIComponent(categoryName)}&user_budget=${encodeURIComponent(categoryBudget)}`,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.status === "success") {
                    alert("Category added successfully!");
                    location.reload(); // Reload the page to reflect the new category
                } else {
                    alert(`Error: ${data.message}`);
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("An error occurred while adding the category.");
            });
    });

    // Update Budget
    document.querySelectorAll(".category-budget").forEach((input) => {
    // Événement pour valider la modification avec la touche "Enter"
        input.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {  // Vérifie si la touche "Enter" est pressée
                event.preventDefault();  // Empêche le comportement par défaut (évite un rechargement de la page)

                const categoryId = this.dataset.id;
                const newBudget = this.value;

                console.log(`🟡 Enter key pressed! Updating budget for Category ID: ${categoryId}, New Budget: ${newBudget}`); // Debug

                // Envoi de la requête de mise à jour
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
                    console.log("🔹 Budget update response:", data);  // Affiche la réponse du serveur
                    if (data.status === "success") {
                        console.log(`✅ Budget successfully updated for category ID ${categoryId} → New budget: ${newBudget}`);
                    } else {
                        console.error("🔴 Error updating budget:", data.message);
                    }
                })
                .catch((error) => {
                    console.error("🔴 Error:", error);
                });
            }
        });
    });





    // Delete Category
    document.querySelectorAll(".delete-category").forEach((button) => {
    button.addEventListener("click", function () {
        const categoryId = this.dataset.id;
        console.log(`🟡 Trying to delete category ID: ${categoryId}`);

        if (!confirm("Are you sure you want to delete this category?")) {
            return;
        }

        fetch("/categories/delete/", {  // 🔥 Garde cette URL, car elle est bien définie !
            method: "POST",  // 🔥 Assure-toi que c'est bien une requête POST
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCookie("csrftoken"),  // CSRF obligatoire pour Django
            },
            body: `category_id=${encodeURIComponent(categoryId)}`,
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("🔹 Server response:", data);
                if (data.status === "success") {
                    alert("Category deleted successfully!");
                    location.reload();
                } else {
                    alert(`Error: ${data.message}`);
                }
            })
            .catch((error) => {
                console.error("🔴 Error:", error);
                alert("An error occurred while deleting the category.");
            });
    });
});


    // Helper Function: Get CSRF Token
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
});
