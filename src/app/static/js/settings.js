const tabIds = [
    "account", "bank-accounts", "export"
]

function updateTab() {
    closePopups()
    let tabId = window.location.hash.slice(1)
    if (!tabIds.includes(tabId)) {
        tabId = tabIds[0]
    }
    let menuLink = document.querySelector(".menu .current")
    if (menuLink) {
        menuLink.classList.remove("current")
    }
    menuLink = document.querySelector(`.menu a[href='#${tabId}']`)
    menuLink.classList.add("current")

    let tab = document.querySelector(".tabs .tab.show")
    if (tab) {
        tab.classList.remove("show")
    }
    tab = document.getElementById(tabId)
    tab.classList.add("show")
}

function exportData() {
    let data = new FormData(document.getElementById("export-form"))
    apiPost("export/", data).then(res => {
        if (res.status !== "success") {
            alert(res.error)
            return
        }

        let content = JSON.stringify(res.data, null, 4)
        let blob = new Blob([content], { type: 'application/json' })
        let link = document.createElement("a");
        let now = new Date()
        let datetime = formatDate(now, "Ymd_HMS")
        let filename = `ETHOME_export-${datetime}.json`
        link.href = URL.createObjectURL(blob)
        link.download = filename
        link.style.display = "none"
        document.body.appendChild(link)
        link.click()
        link.remove()
    })
}

function closePopups() {
    document.querySelectorAll(".popup.show").forEach(popup => {
        popup.classList.remove("show")
    })
}

function showDeletePopup(accountId, accountNumber) {
    closePopups()
    let popup = document.querySelector("#confirm-delete-popup")
    popup.dataset.account = accountId
    popup.querySelector(".desc .num").innerText = accountNumber
    popup.classList.add("show")
}

function deleteAccount(id) {
    apiDelete(`accounts/${id}/`).then(res => {
        if (res.status === "success") {
            window.location.reload()
        } else {
            alert(res.error)
        }
    })
}

function saveUserInfo() {
    let data = new FormData(document.getElementById("user-form"))
    apiPost("user/", data).then(res => {
        if (res.status === "success") {
            window.location.reload()
        } else {
            alert(res.error)
        }
    })
}

function changePassword() {
    let data = new FormData(document.getElementById("password-form"))
    apiPost("user/change_password/", data).then(res => {
        if (res.status === "success") {
            window.location.reload()
        } else {
            alert(res.error)
        }
    })
}

window.addEventListener("hashchange", () => updateTab())

window.addEventListener("load", () => {
    updateTab()

    // Export
    document.getElementById("export-form").addEventListener("submit", e => {
        e.preventDefault()
        exportData()
    })

    // Accounts
    let deletePopup = document.getElementById("confirm-delete-popup")
    deletePopup.querySelector(".actions .cancel").addEventListener("click", () => closePopups())
    deletePopup.querySelector(".actions .delete").addEventListener("click", () => deleteAccount(deletePopup.dataset.account))

    document.querySelectorAll(".accounts .list .account").forEach(account => {
        let id = account.dataset.id
        let number = account.querySelector(".num").innerText
        let deleteBtn = account.querySelector(".delete")
        deleteBtn.addEventListener("click", () => {
            showDeletePopup(id, number)
        })
    })

    // User account
    let userForm = document.getElementById("user-form")
    userForm.addEventListener("submit", e => {
        e.preventDefault()
        saveUserInfo()
    })
    userForm.addEventListener("input", () => {
        userForm.querySelector("button").disabled = false
    })

    let passwordPopup = document.getElementById("change-pwd-popup")
    document.getElementById("change-pwd-btn").addEventListener("click", () => {
        passwordPopup.classList.add("show")
    })
    passwordPopup.querySelector(".actions .cancel").addEventListener("click", () => closePopups())
    document.getElementById("password-form").addEventListener("submit", e => {
        e.preventDefault()
        changePassword()
    })

    let mfaBtn = document.getElementById("enable-2fa")
    if (mfaBtn) {
        mfaBtn.addEventListener("click", () => {
            window.location.href = "/totp/"
        })
    }
})