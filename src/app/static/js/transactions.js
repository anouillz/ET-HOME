function editTransaction(id) {
    window.location.href = `/transactions/${id}/`
}

function deleteTransaction(id) {
    apiDelete(`transactions/${id}/`).then(res => {
        if (res.status === "success") {
            window.location.reload()
        } else {
            alert(res.error)
        }
    })
}

window.addEventListener("load", () => {
    document.querySelectorAll("tbody tr[data-id]").forEach(row => {
        let id = row.dataset.id
        let editBtn = row.querySelector(".edit-btn")
        let deleteBtn = row.querySelector(".delete-btn")
        if (editBtn) {
            editBtn.addEventListener("click", () => editTransaction(id))
        }
        if (deleteBtn) {
            deleteBtn.addEventListener("click", () => deleteTransaction(id))
        }
    })
})

document.addEventListener("DOMContentLoaded", function () {
    const dropdownToggle = document.querySelector(".dropdown-toggle");
    const dropdownMenu = document.querySelector(".dropdown-menu");
    const menuItems = document.querySelectorAll(".dropdown-menu li");


    function updateURL(sortValue) {
        const newURL = `/transactions/?sort=${sortValue}`;
        window.history.pushState({}, "", newURL);
        window.location.reload();
    }


    dropdownToggle.addEventListener("click", function () {
        dropdownMenu.style.display = dropdownMenu.style.display === "block" ? "none" : "block";
    });


    menuItems.forEach(item => {
        item.addEventListener("click", function () {
            const sortValue = this.getAttribute("data-sort");
            dropdownToggle.textContent = this.textContent;
            dropdownMenu.style.display = "none";
            updateURL(sortValue);
        });
    });


    document.addEventListener("click", function (event) {
        if (!dropdownToggle.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.style.display = "none";
        }
    });

    const urlParams = new URLSearchParams(window.location.search);
    const currentSort = urlParams.get("sort");
    if (currentSort) {
        const selectedItem = document.querySelector(`.dropdown-menu li[data-sort="${currentSort}"]`);
        if (selectedItem) {
            dropdownToggle.textContent = selectedItem.textContent;
        }
    }
});



