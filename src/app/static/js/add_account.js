let confirmBtn
let step1, step2, step3

async function confirm() {
    confirmBtn.disabled = true
    let data = new FormData(document.getElementById("info-form"))
    step1.classList.add("finished")
    step2.classList.add("active")

    let accountId = await apiPost("accounts/", data).then(res => {
        if (res.status === "success") {
            return res.account.id
        }
        confirmBtn.disabled = false
        step1.classList.remove("finished")
        step2.classList.remove("active")
        return null
    })
    if (accountId === null) {
        return
    }

    step2.classList.add("finished")
    step3.classList.add("active")
    data = new FormData()
    data.set("account_id", accountId)
    apiPost("test_secret/", data).then(res => {
        if (res.status === "success") {
            step3.classList.add("finished")
            setTimeout(() => window.location.href = "/", 1000)
        } else {
            confirmBtn.disabled = false
            step2.classList.remove("finished")
            step3.classList.remove("active")
        }
    })
}

window.addEventListener("load", () => {
    step1 = document.querySelector(".step-1")
    step2 = document.querySelector(".step-2")
    step3 = document.querySelector(".step-3")
    confirmBtn = document.getElementById("confirmBtn")
    document.getElementById("info-form").addEventListener("submit", e => {
        e.preventDefault()
        confirm()
    })
})