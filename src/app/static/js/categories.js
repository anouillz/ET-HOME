document.addEventListener("DOMContentLoaded", function () {
    let categoryToDelete = null
    let categoryNameToDelete = ""

    // modals and buttons
    const confirmDeleteModal = document.getElementById("confirm-delete-modal")
    const successDeleteModal = document.getElementById("success-delete-modal")
    const confirmDeleteBtn = document.getElementById("confirm-delete-btn")
    const cancelDeleteBtn = document.getElementById("cancel-delete-btn")
    const closeSuccessModal = document.getElementById("close-success-modal")
    const successDeleteMessage = document.getElementById("success-delete-message")

    const addCategoryModal = document.getElementById("add-category-modal")
    const confirmAddCategoryBtn = document.getElementById("confirm-add-category")
    const cancelAddCategoryBtn = document.getElementById("cancel-add-category")
    const newCategoryNameInput = document.getElementById("new-category-name")
    const newCategoryBudgetInput = document.getElementById("new-category-budget")

    // modals hidden by default
    document.getElementById("budget-modal").style.display = "none"
    document.getElementById("confirm-delete-modal").style.display = "none"
    document.getElementById("success-delete-modal").style.display = "none"
    document.getElementById("add-category-modal").style.display = "none"

    // add category modal
    document.getElementById("add-category-btn").addEventListener("click", function () {
        addCategoryModal.style.display = "flex"
    })

    // close modal when clicking outside
    cancelAddCategoryBtn.addEventListener("click", function () {
        addCategoryModal.style.display = "none"
        newCategoryNameInput.value = ""
        newCategoryBudgetInput.value = ""
    })

    // add category if user clicks "Add"
    confirmAddCategoryBtn.addEventListener("click", function () {
        const categoryName = newCategoryNameInput.value.trim()
        const categoryBudget = newCategoryBudgetInput.value.trim()

        if (!categoryName || !categoryBudget) {
            alert("Please enter a category name and budget!")
            return
        }

        let data = new FormData()
        data.set("name", categoryName)
        data.set("user_budget", categoryBudget)
        apiPost("categories/", data).then(res => {
            if (res.status === "success") {
                window.location.reload() // Reload to show new category
            } else {
                alert(res.error)
            }
        })
    })

    // update budget with enter key
    document.querySelectorAll(".category-budget").forEach((input) => {
        input.addEventListener("change", function (event) {
                const hiddenInput = this.closest(".category-item").querySelector("#changed");
                if (hiddenInput) {
                    hiddenInput.value = "true"; 
                }
        })
    })
    document.querySelectorAll(".toggle-category").forEach((input) => {
        input.addEventListener("change", function (event) {
            const hiddenInput = this.closest(".category-item").querySelector("#changed");
            if (hiddenInput) {
                hiddenInput.value = "true"; 
            }
        })
    })

    // delete category with modal
    document.querySelectorAll(".delete-category").forEach((button) => {
        button.addEventListener("click", function () {
            categoryToDelete = this.dataset.id
            categoryNameToDelete = this.closest(".category-item").querySelector(".category-name").innerText
            confirmDeleteModal.style.display = "flex"
        })
    })

    // validate delete
    confirmDeleteBtn.addEventListener("click", function () {
        if (!categoryToDelete) return

        apiDelete(`categories/${categoryToDelete}/`).then(res => {
            if (res.status === "success") {
                console.log("Category deleted successfully!")
                confirmDeleteModal.style.display = "none"
                successDeleteMessage.innerText = `Category "${categoryNameToDelete}" deleted successfully!`
                successDeleteModal.style.display = "flex"
            } else {
                alert(res.error)
            }
        })
    })

    // if user doesnt want to delete
    cancelDeleteBtn.addEventListener("click", function () {
        confirmDeleteModal.style.display = "none"
    })

    // if user wants to close success modal
    closeSuccessModal.addEventListener("click", function () {
        successDeleteModal.style.display = "none"
        location.reload()
    })

    // checkbox
    document.querySelectorAll(".toggle-category").forEach((checkbox) => {

    })

    // close budget modal
    document.getElementById("close-modal").addEventListener("click", function () {
        document.getElementById("budget-modal").style.display = "none"
    })
})


async function update_categories(){
        let categories = document.querySelectorAll(".category-item");
        let categoryData = [];

        // Loop through each category and extract data
        categories.forEach(category => {
            let categoryId = category.getAttribute("data-id");
            let categoryBudget = category.querySelector(".category-budget").value;
            let isActive = category.querySelector(".toggle-category").checked; // Get checkbox state
            let changed = category.querySelector("#changed").value
            if(changed == "true"){
            categoryData.push({
                id: categoryId,
                budget: parseFloat(categoryBudget), // Convert to number
                is_active: isActive
            });
        }
        });

        if(categoryData.length > 0){
            let response = await apiPost("categories/update",{ categories: categoryData },false)

            if (response.status == "success"){
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
            //refresh page
        }else{
            console.log("no category to update")
        }
}
document.getElementById("update-categories-btn").addEventListener("click", update_categories);