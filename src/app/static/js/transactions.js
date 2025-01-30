function editTransaction(id) {
    window.location.href += `/${id}`
}

function deleteTransaction(id) {
    apiPost(`transactions/${id}/delete`, {}, true).then(res => {
        window.location.reload()
    })
}

window.addEventListener("load", () => {
    document.querySelectorAll("tbody tr").forEach(row => {
        let id = row.dataset.id
        let editBtn = row.querySelector(".edit-btn")
        let deleteBtn = row.querySelector(".delete-btn")
        editBtn.addEventListener("click", () => editTransaction(id))
        deleteBtn.addEventListener("click", () => deleteTransaction(id))
    })
})