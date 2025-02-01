const tabIds = [
    "account", "bank-accounts", "export"
]

function updateTab() {
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

window.addEventListener("hashchange", () => updateTab())

window.addEventListener("load", () => {
    updateTab()

    document.getElementById("export-form").addEventListener("submit", e => {
        e.preventDefault()
        exportData()
    })
})