document.addEventListener("DOMContentLoaded", function () {
    // Handle toggle active state
    document.querySelectorAll(".toggle-category").forEach((toggle) => {
        toggle.addEventListener("change", function () {
            const categoryId = this.dataset.id;
            const isActive = this.checked;

            fetch("/categories/toggle/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify({ category_id: categoryId, is_active: isActive }),
            }).then(response => response.json());
        });
    });

    // Handle budget updates
    document.querySelectorAll(".category-budget").forEach((input) => {
        input.addEventListener("change", function () {
            const categoryId = this.dataset.id;
            const newBudget = this.value;

            fetch("/categories/update_budget/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify({ category_id: categoryId, new_budget: newBudget }),
            }).then(response => response.json());
        });
    });

    // Handle adding a new category
    document.getElementById("add-category-btn").addEventListener("click", function () {
        const categoryName = prompt("Enter the name of the new category:");
        const userBudget = prompt("Enter the budget for the new category:");

        if (categoryName && userBudget) {
            fetch("/categories/add/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify({ name: categoryName, user_budget: userBudget }),
            }).then(response => response.json()).then(data => {
                if (data.new_category_status === "success") {
                    location.reload();
                }
            });
        }
    });

    // Handle delete category
    document.querySelectorAll(".delete-category").forEach((button) => {
        button.addEventListener("click", function () {
            const categoryId = this.dataset.id;

            fetch("/categories/delete/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify({ id: categoryId }),
            }).then(response => response.json()).then(data => {
                if (data.delete_category_status === "success") {
                    location.reload();
                }
            });
        });
    });

    // Helper to get CSRF token
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
});
