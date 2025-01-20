let accounts = []

const CATEG_MARGIN = 50
const CATEG_THICKNESS = 25
const CATEG_GAP = 3
const CATEG_PCT_PADDING = 10

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
                    if (t.amount < 0) {
                        byCategory[t.category.id] += t.amount
                    }
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
            total: -total
        })
    })
    categories = categories.sort((c1, c2) => c2.total - c1.total)
    showTopCategories(categories)
    showAccounts()
}

function showTopCategories(categories) {
    let widget = document.getElementById("top-categories")
    let chart = widget.querySelector(".chart")
    let list = widget.querySelector(".list")

    let total = categories.map(c => c.total).reduce((a, b) => a+b, 0)
    let offset = -0.25
    let colStep = 360 / categories.length

    /** @var {CanvasRenderingContext2D} ctx */
    let ctx = chart.getContext("2d")
    let w = chart.width
    let h = chart.height
    let mx = w / 2
    let my = h / 2
    let radius = Math.min(mx, my) - CATEG_MARGIN
    let radiusPct = radius + CATEG_THICKNESS / 2 + CATEG_PCT_PADDING
    ctx.lineWidth = CATEG_THICKNESS
    ctx.font = "16pt 'Arial', sans-serif"
    ctx.textAlign = "center"
    ctx.textBaseline = "middle"
    ctx.clearRect(0, 0, w, h)

    list.innerHTML = ""
    let template = document.querySelector(".template.category").cloneNode(true)
    template.classList.remove("template")
    categories.forEach((category, i) => {
        let ratio = category.total / total
        let angleStart = offset * 360 + CATEG_GAP / 2
        let angleEnd = angleStart + ratio * 360 - CATEG_GAP
        angleStart = angleStart * Math.PI / 180
        angleEnd = angleEnd * Math.PI / 180
        let angleMid = (angleEnd + angleStart) / 2
        let col = `hsl(${i * colStep}deg 70% 60%)`

        if (angleEnd > angleStart) {
            // Draw segment
            ctx.strokeStyle = col
            ctx.beginPath()
            ctx.arc(mx, my, radius, angleStart, angleEnd)
            ctx.stroke()

            // Place percentage label (minimize overlapping with segment)
            let x = mx + radiusPct * Math.cos(angleMid)
            let y = my + radiusPct * Math.sin(angleMid)
            let pct = formatPercentage(ratio)
            let measure = ctx.measureText(pct)
            let w2 = measure.width / 2
            let h2 = (measure.actualBoundingBoxAscent + measure.actualBoundingBoxDescent) / 2
            let m = Math.tan(angleMid)
            let a = angleMid % (2 * Math.PI)
            if (a < 0) {
                a += 2 * Math.PI
            }
            if (Math.PI / 2 < a && a < Math.PI) {
                m = -m
            }

            let dx = m === 0.0 ? w2 : Math.min(w2, Math.abs(h2 / m))
            let dy = Math.min(h2, Math.abs(m * w2))
            if (Math.PI / 2 < a && a < 3 * Math.PI / 2) {
                dx = -dx
            }
            if (Math.PI < a) {
                dy = -dy
            }
            ctx.fillText(pct, x + dx, y + dy)
        }

        offset += ratio

        let row = template.cloneNode(true)
        row.style.setProperty("--col", col)
        row.querySelector(".name").innerText = category.name
        row.querySelector(".amount").innerText = formatMoney(category.total)
        list.appendChild(row)
    })
}

function showAccounts() {
    let widget = document.getElementById("accounts")
    let template = widget.querySelector(".template.account").cloneNode(true)
    template.classList.remove("template")
    let list = widget.querySelector(".list")
    list.innerHTML = ""
    accounts.forEach(account => {
        let entry = template.cloneNode(true)
        entry.querySelector(".id").innerText = "#" + account.account_number.slice(-4)
        entry.querySelector(".bank").innerText = "(" + account.bank + ")"
        entry.querySelector(".balance").innerText = formatMoney(account.balance)
        list.appendChild(entry)
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