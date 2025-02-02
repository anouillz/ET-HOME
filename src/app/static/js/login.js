function login() {
    let data = new FormData(document.querySelector("form"))
    apiPost("user/login/", data).then(res => {
        if (res.status === "success") {
            window.location.href = "/"
        } else if (res.status === "totp-needed") {
            document.getElementById("totp-code").classList.remove("hidden")
        } else {
            alert(res.error)
        }
    })
}

window.addEventListener("load", () => {
    document.querySelector("form").addEventListener("submit", e => {
        e.preventDefault()
        login()
    })
})