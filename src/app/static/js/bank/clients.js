function deleteClient(id) {
    apiPost(`clients/${id}/delete`, {}, true).then(res => {
        window.location.reload()
    })
}

window.addEventListener("load", () => {
    document.querySelectorAll("tbody tr").forEach(row => {
        let id = row.dataset.id
        let deleteBtn = row.querySelector(".delete-btn")
        deleteBtn.addEventListener("click", () => deleteClient(id))
    })
})