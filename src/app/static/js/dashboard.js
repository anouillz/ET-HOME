let accounts = []

async function refreshDashboard() {
    let userId = document.getElementById("userId").value
    let accountsInfo = []
    let accountsPromises = []
    let curMonthDay = new Date()
    let lastMonthTotal = 0
    let curMonthTotal = 0
    let byCategory = {}
    let categoryNames = {}
    curMonthDay.setDate(1)
    accounts.forEach(account => {
        let promise = apiGet(`get_bankAccount_info/${account.id}`).then(info => {
            console.log(info)
            if (info.error) {
                return
            }
            let transactions = info.transactions
            let lastMonthTrx = []
            let curMonthTrx = []
            transactions.forEach(t => {
                let d = new Date(t.date)
                if (d < curMonthDay) {
                    lastMonthTrx.push(t)
                    lastMonthTotal += t.amount
                } else {
                    curMonthTrx.push(t)
                    curMonthTotal += t.amount
                    if (!(t.category.id in byCategory)) {
                        byCategory[t.category.id] = 0
                    }
                    if (!(t.category.id in categoryNames)) {
                        categoryNames[t.category.id] = t.category.name
                    }
                    byCategory[t.category.id] += t.amount
                }
            })
        })
        accountsPromises.push(promise)
    })

    await Promise.all(accountsPromises)
    let diff = curMonthTotal - lastMonthTotal

    document.querySelector("#current-month .value").innerText = formatMoney(curMonthTotal)
    document.querySelector("#last-month .total .value").innerText = formatMoney(lastMonthTotal)
    if (lastMonthTotal !== 0) {
        diff = diff / lastMonthTotal
        document.querySelector("#last-month .diff .value").innerText = formatPercentage(diff, true)
    }

    let categories = []
    Object.entries(byCategory).forEach(([id, total]) => {
        categories.push({
            id: id,
            name: categoryNames[id],
            total: total
        })
    })
    categories = categories.sort((c1, c2) => c1.total - c2.total)
    showTopCategories(categories)
}

function showTopCategories(categories) {
    let widget = document.getElementById("top-categories")
    let chart = widget.querySelector(".chart")
    let list = widget.querySelector(".list")

    let total = categories.map(c => c.total).reduce((a, b) => a+b, 0)
    let offset = -0.25
    let colStep = 360 / categories.length
    let gap = 3

    let ctx = chart.getContext("2d")
    let w = chart.width
    let h = chart.height
    let mx = w / 2
    let my = h / 2
    let radius = Math.min(mx, my) - 15
    ctx.lineWidth = 30
    ctx.clearRect(0, 0, w, h)

    list.innerHTML = ""
    categories.forEach((category, i) => {
        let ratio = category.total / total
        let angleStart = offset * 360 + gap / 2
        let angleEnd = angleStart + ratio * 360 - gap
        let col = `hsl(${i * colStep}deg 70% 60%)`

        if (angleEnd > angleStart) {
            ctx.strokeStyle = col
            ctx.beginPath()
            ctx.arc(mx, my, radius, angleStart * Math.PI / 180, angleEnd * Math.PI / 180)
            ctx.stroke()
        }

        offset += ratio

        let row = document.createElement("div")
        row.classList.add("category")
        row.style.setProperty("--col", col)
        row.innerText = category.name

        list.appendChild(row)
    })
}

window.addEventListener("load", () => {
    apiGet("get_accounts").then(res => {
        if (res.accounts) {
            accounts = res.accounts
        }
    }).then(() => {
        refreshDashboard()
    })
})