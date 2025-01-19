/**
 *
 * @param {HTMLFormElement} form
 */
function initializeForm(form) {
    form.addEventListener("submit", e => {
        e.preventDefault()
        let fd = new FormData(form)
        let endpoint = form.dataset.endpoint
        apiPost(endpoint, fd, true).then(res => {
            if (res.error) {
                alert(res.error)
            } else {
                alert(res.message)
            }
            window.location.reload()
        }).catch(err => {
            alert(err)
        })
    })
}

window.addEventListener("load", () => {
    let form = document.querySelector("form")
    if (form) {
        initializeForm(form)
    }
})