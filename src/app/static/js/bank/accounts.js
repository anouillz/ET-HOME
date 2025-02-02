function editAccount(id) {
    window.location.href += `/${id}`
}

function deleteAccount(id) {
    apiPost(`accounts/${id}/delete`, {}, true).then(res => {
        window.location.reload()
    })
}

window.addEventListener("load", () => {
    document.querySelectorAll("tbody tr").forEach(row => {
        let id = row.dataset.id
        let editBtn = row.querySelector(".edit-btn")
        let deleteBtn = row.querySelector(".delete-btn")
        editBtn.addEventListener("click", () => editAccount(id))
        deleteBtn.addEventListener("click", () => deleteAccount(id))
    })
})