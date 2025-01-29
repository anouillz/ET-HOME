document.addEventListener("DOMContentLoaded", function () {
    let categoryToDelete = null;
    let categoryNameToDelete = "";

    // modals and buttons
    const confirmDeleteModal = document.getElementById("confirm-delete-modal");
    const successDeleteModal = document.getElementById("success-delete-modal");
    const confirmDeleteBtn = document.getElementById("confirm-delete-btn");
    const cancelDeleteBtn = document.getElementById("cancel-delete-btn");
    const closeSuccessModal = document.getElementById("close-success-modal");
    const successDeleteMessage = document.getElementById("success-delete-message");

    const addCategoryModal = document.getElementById("add-category-modal");
    const confirmAddCategoryBtn = document.getElementById("confirm-add-category");
    const cancelAddCategoryBtn = document.getElementById("cancel-add-category");
    const newCategoryNameInput = document.getElementById("new-category-name");
    const newCategoryBudgetInput = document.getElementById("new-category-budget");

    // modals hidden by default
    document.getElementById("budget-modal").style.display = "none";
    document.getElementById("confirm-delete-modal").style.display = "none";
    document.getElementById("success-delete-modal").style.display = "none";
    document.getElementById("add-category-modal").style.display = "none";

    // add category modal
    document.getElementById("add-category-btn").addEventListener("click", function () {
        addCategoryModal.style.display = "flex";
    });

    // close modal when clicking outside
    cancelAddCategoryBtn.addEventListener("click", function () {
        addCategoryModal.style.display = "none";
        newCategoryNameInput.value = "";
        newCategoryBudgetInput.value = "";
    });

    // add category if user clicks "Add"
    confirmAddCategoryBtn.addEventListener("click", function () {
        const categoryName = newCategoryNameInput.value.trim();
        const categoryBudget = newCategoryBudgetInput.value.trim();

        if (!categoryName || !categoryBudget) {
            alert("Please enter a category name and budget!");
            return;
        }

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
                console.log("Category added successfully!");
                addCategoryModal.style.display = "none";
                newCategoryNameInput.value = "";
                newCategoryBudgetInput.value = "";
                location.reload(); // Reload to show new category
            } else {
                console.error("Error adding category:", data.message);
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
    });

    // update budget with enter key
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
                    console.error("Error:", error);
                });
            }
        });
    });

    // delete category with modal
    document.querySelectorAll(".delete-category").forEach((button) => {
        button.addEventListener("click", function () {
            categoryToDelete = this.dataset.id;
            categoryNameToDelete = this.closest(".category-item").querySelector(".category-name").innerText;
            confirmDeleteModal.style.display = "flex";
        });
    });

    // validate delete
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
                console.log("Category deleted successfully!");
                confirmDeleteModal.style.display = "none";
                successDeleteMessage.innerText = `Category "${categoryNameToDelete}" deleted successfully!`;
                successDeleteModal.style.display = "flex";
            } else {
                console.error("Error deleting category:", data.message);
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
    });

    // if user doesnt want to delete
    cancelDeleteBtn.addEventListener("click", function () {
        confirmDeleteModal.style.display = "none";
    });

    // if user wants to close success modal
    closeSuccessModal.addEventListener("click", function () {
        successDeleteModal.style.display = "none";
        location.reload();
    });

    // checkbox
    document.querySelectorAll(".toggle-category").forEach((checkbox) => {

    });

    // close budget modal
    document.getElementById("close-modal").addEventListener("click", function () {
        document.getElementById("budget-modal").style.display = "none";
    });
});

// get cookie
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
