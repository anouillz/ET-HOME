window.addEventListener("click", () => {
    let form = document.getElementById("form")
    form.addEventListener("submit", e => {
        e.preventDefault()
        let id = form.dataset.id
        let fd = new FormData(form)
        apiPost(`transactions/${id}/`, fd).then(res => {
            if (res.status === "success") {
                window.location.href = "../"
            } else {
                alert(res.error)
            }
        })
    })
})