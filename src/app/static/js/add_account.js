let confirmBtn
let step1, step2, step3

async function confirm() {
    let userId = document.getElementById("bankUserId").value
    let bankName = document.getElementById("bankName").value
    let accountNum = document.getElementById("bankAccountNumber").value
    let password = document.getElementById("bankUserPassword").value
    confirmBtn.disabled = true
    let data = new FormData()
    data.set("user_id", userId)
    data.set("bank_name", bankName)
    data.set("account_number", accountNum)
    data.set("password", password)

    step1.classList.add("finished")
    step2.classList.add("active")

    let accountId = await apiPost("add_bank_account", data).then(res => {
        if (res.error) {
            throw new Error(res.error)
        }
        return res.id
    }).catch(err => {
        console.error(err)
        confirmBtn.disabled = false
        step1.classList.remove("finished")
        step2.classList.remove("active")
    })
    if (accountId === null) {
        return
    }

    step2.classList.add("finished")
    step3.classList.add("active")
    data = new FormData()
    data.set("account_id", accountId)
    apiPost("test_secret", data).then(res => {
        if (res.error !== undefined) {
            throw new Error(res.error)
        }
        step3.classList.add("finished")
        setTimeout(() => window.location.href = "/", 1000)
    }).catch(err => {
        console.error(err)
        confirmBtn.disabled = false
        step2.classList.remove("finished")
        step3.classList.remove("active")
    })
}

window.addEventListener("load", () => {
    step1 = document.querySelector(".step-1")
    step2 = document.querySelector(".step-2")
    step3 = document.querySelector(".step-3")
    confirmBtn = document.getElementById("confirmBtn")
    confirmBtn.addEventListener("click", confirm)
})