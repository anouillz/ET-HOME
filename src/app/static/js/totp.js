function validateTotp() {
    let data = new FormData(document.getElementById("totp-form"))
    apiPost("user/totp/", data).then(res => {
        if (res.status === "success") {
            window.location.href = "/"
        } else {
            let codeInput = document.getElementById("test-code")
            codeInput.setCustomValidity("Invalid code")
            codeInput.reportValidity()
        }
    })
}

window.addEventListener("load", () => {
    document.getElementById("totp-form").addEventListener("submit", e => {
        console.log("Submitting")
        e.preventDefault()
        validateTotp()
    })
    let codeInput = document.getElementById("test-code")
    codeInput.addEventListener("input", () => codeInput.setCustomValidity(""))
})