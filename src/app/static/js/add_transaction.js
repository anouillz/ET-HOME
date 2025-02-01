function addTransaction() {
    let data = new FormData(document.getElementById("transaction-form"))
    apiPost("transactions/", data).then(res => {
        if (res.status === "success") {
            window.location.href = "/transactions/"
        } else {
            alert(res.error)
        }
    })
}
window.addEventListener("load", () => {
    let form = document.getElementById("transaction-form")
    form.addEventListener("submit", e => {
        e.preventDefault()
        addTransaction()
    })
})
