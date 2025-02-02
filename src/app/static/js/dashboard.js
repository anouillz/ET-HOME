let accounts = []
/** @type {HTMLCanvasElement} */
let graphCanvas
let outcomes = {}
let incomes = {}
let graphStartDate = new Date()

const GRAPH_RANGES = {
    week: {
        days: 7,
        step: 1
    },
    fortnight: {
        days: 14,
        step: 2
    },
    month: {
        days: 30,
        step: 6
    },
    year: {
        days: 365,
        step: 36.5
    }
}
const GRAPH_VSTEPS = [5, 10, 25, 50, 100, 250, 500, 1000, 10_000, 100_000, 250_000, 1_000_000]
const GRAPH_LMARGIN = 60
const GRAPH_RMARGIN = 10
const GRAPH_TMARGIN = 10
const GRAPH_BMARGIN = 20
const GRAPH_MIN_VTICK_SPACING = 80

const CATEG_MARGIN = 50
const CATEG_THICKNESS = 25
const CATEG_GAP = 3
const CATEG_PCT_PADDING = 10

async function refreshDashboard() {
    let userId = document.getElementById("userId").value
    let accountsInfo = []
    let accountsPromises = []
    let curMonthDay = new Date()
    curMonthDay.setDate(1)
    curMonthDay.setHours(0)
    let lastMonthTotal = 0
    let curMonthTotal = 0
    let byCategory = {}
    let categoryNames = {}
    let accountFilter = document.getElementById("expenses-account")
    accountFilter.innerHTML = ""
    let opt = document.createElement("option")
    opt.value = "all"
    opt.innerText = "All accounts"
    accountFilter.appendChild(opt)
    accounts.forEach(account => {
        let promise = apiGet(`accounts/${account.id}`).then(info => {
            console.log(info)
            if (info.status !== "success") {
                return
            }
            let transactions = info.transactions
            let lastMonthTrx = []
            let curMonthTrx = []
            transactions.forEach(t => {
                let d = new Date(t.date)
                if (d < curMonthDay) {
                    lastMonthTrx.push(t)
                    lastMonthTotal += +t.amount
                } else {
                    curMonthTrx.push(t)
                    curMonthTotal += +t.amount
                    if (t.category !== null) {
                        if (!(t.category.id in byCategory)) {
                            byCategory[t.category.id] = 0
                        }
                        if (!(t.category.id in categoryNames)) {
                            categoryNames[t.category.id] = t.category.name
                        }
                        if (t.amount < 0) {
                            byCategory[t.category.id] += +t.amount
                        }
                    }
                }
            })
        })
        accountsPromises.push(promise)

        let opt = document.createElement("option")
        opt.value = account.id
        opt.innerText = `#${account.account_number.slice(-4)} (${account.bank_name})`
        accountFilter.appendChild(opt)
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
    resizeGraph()
    await updateGraph()
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
        entry.querySelector(".bank").innerText = "(" + account.bank_name + ")"
        entry.querySelector(".balance").innerText = formatMoney(account.balance)
        list.appendChild(entry)
    })
}

function resizeGraph() {
    let parent = graphCanvas.parentElement
    graphCanvas.width = parent.clientWidth
    graphCanvas.height = parent.clientHeight
    showExpenses()
}

async function updateGraph() {
    let range = document.getElementById("expenses-range").value
    let today = new Date()
    let rangeDays = GRAPH_RANGES[range].days
    let startDate = new Date(today.valueOf() - (rangeDays - 1) * 24 * 60 * 60 * 1000)
    let start = formatDate(startDate, "Y-m-d")
    let end = formatDate(today, "Y-m-d")
    let url = `transactions/${start}/${end}/`
    let accountFilter = document.getElementById("expenses-account")
    if (accountFilter.value !== "all") {
        url = `accounts/${accountFilter.value}/` + url
    }
    let transactions = (await apiGet(url)).transactions
    let categories = document.getElementById("expenses-categories").getAttribute("value") ?? "*"
    if (categories !== "*") {
        categories = categories.split(",")
        transactions = transactions.filter(t => t.category !== null && categories.includes(t.category.id))
    }

    incomes = {}
    outcomes = {}
    transactions.forEach(transaction => {
        let date = new Date(transaction.date)
        transaction.date = formatDate(date, "Y-m-d")
        if (transaction.amount < 0) {
            if (!(transaction.date in outcomes)) {
                outcomes[transaction.date] = 0
            }
            outcomes[transaction.date] += -transaction.amount
        } else {
            if (!(transaction.date in incomes)) {
                incomes[transaction.date] = 0
            }
            incomes[transaction.date] += transaction.amount
        }
    })
    graphStartDate = startDate
    showExpenses()
}

function showExpenses() {
    let range = document.getElementById("expenses-range").value
    /** @var {CanvasRenderingContext2D} ctx */
    let ctx = graphCanvas.getContext("2d")
    let {days, step: tickStep} = GRAPH_RANGES[range]

    let width = graphCanvas.width
    let height = graphCanvas.height
    ctx.clearRect(0, 0, width, height)
    let innerWidth = width - GRAPH_LMARGIN - GRAPH_RMARGIN
    let innerHeight = height - GRAPH_BMARGIN - GRAPH_TMARGIN
    let ox = GRAPH_LMARGIN
    let oy = GRAPH_TMARGIN + innerHeight
    let ticks = days / tickStep
    let hgap = innerWidth / (days - 1) * tickStep

    let style = getComputedStyle(graphCanvas)
    let axisColor = style.getPropertyValue("--axis-col")
    let gridColor = style.getPropertyValue("--grid-col")
    let labelColor = style.getPropertyValue("--label-col")
    let incomeLineColor = style.getPropertyValue("--income-line-col")
    let incomePtStroke = style.getPropertyValue("--income-pt-stroke")
    let incomePtFill = style.getPropertyValue("--income-pt-fill")
    let outcomeLineColor = style.getPropertyValue("--outcome-line-col")
    let outcomePtStroke = style.getPropertyValue("--outcome-pt-stroke")
    let outcomePtFill = style.getPropertyValue("--outcome-pt-fill")

    ctx.strokeStyle = axisColor
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(ox, oy - innerHeight)
    ctx.lineTo(ox, oy)
    ctx.lineTo(ox + innerWidth, oy)
    ctx.stroke()

    ctx.strokeStyle = gridColor
    ctx.lineWidth = 1
    let date = graphStartDate
    let stepMs = tickStep * 24 * 60 * 60 * 1000

    let maxOutcome = Math.max(...Object.values(outcomes))
    let maxIncome = Math.max(...Object.values(incomes))
    let maxValue = Math.max(maxOutcome, maxIncome)
    let outcomePts = []
    let incomePts = []

    ctx.fillStyle = labelColor
    // Horizontal lines
    ctx.font = "8pt 'Arial', sans-serif"
    ctx.textBaseline = "middle"
    ctx.textAlign = "right"
    let fmt = new Intl.NumberFormat("fr-CH")
    let vstep = GRAPH_VSTEPS[0]
    let nSteps = 1
    let stepHeight = innerHeight
    for (let i = 0; i < GRAPH_VSTEPS.length; i++) {
        vstep = GRAPH_VSTEPS[i]
        nSteps = Math.floor(maxValue / vstep)
        stepHeight = innerHeight * vstep / maxValue
        if (stepHeight > GRAPH_MIN_VTICK_SPACING) {
            break
        }
    }

    for (let i = 1; i <= nSteps; i++) {
        let y = oy - i * stepHeight
        ctx.beginPath()
        ctx.moveTo(ox, y)
        ctx.lineTo(ox + innerWidth, y)
        ctx.stroke()
        ctx.fillText("CHF " + fmt.format(vstep * i) + ".-", ox - 2, y)
    }

    // Vertical lines
    //ctx.font = "8pt 'Arial', sans-serif"
    ctx.textBaseline = "top"
    ctx.textAlign = "center"
    for (let i = 1; i < ticks; i++) {
        date = new Date(date.valueOf() + stepMs)
        let x = ox + hgap * i
        ctx.beginPath()
        ctx.moveTo(x, oy)
        ctx.lineTo(x, oy - innerHeight)
        ctx.stroke()
        if (i * tickStep !== days - 1) {
            ctx.fillText(formatDate(date, "d / m"), x, oy + 5)
        }
    }
    let dayStep = innerWidth / (days - 1)
    date = graphStartDate
    for (let i = 0; i < days; i++) {
        let x = ox + dayStep * i
        let key = formatDate(date, "Y-m-d")
        let outcome = outcomes[key]
        let income = incomes[key]
        if (outcome) {
            let y = oy - outcome * innerHeight / maxValue
            outcomePts.push([x, y])
        } else {
            //outcomePts.push([x, oy])
        }
        if (income) {
            let y = oy - income * innerHeight / maxValue
            incomePts.push([x, y])
        } else {
            //incomePts.push([x, oy])
        }
        date = new Date(date.valueOf() + 24 * 60 * 60 * 1000)
    }

    if (incomePts.length === 0 && outcomePts.length === 0) {
        ctx.textAlign = "center"
        ctx.textBaseline = "middle"
        ctx.font = "bold 16pt 'Arial', sans-serif"
        let m = ctx.measureText("No Data")
        let w = m.width
        let h = m.actualBoundingBoxAscent + m.actualBoundingBoxDescent
        let x = ox + innerWidth / 2
        let y = oy - innerHeight / 2
        ctx.fillStyle = "white"
        ctx.fillRect(x - w / 2 - 8, y - h / 2 - 8, w + 16, h + 16)
        ctx.fillStyle = gridColor
        ctx.fillText("No Data", x, y)
    }

    let start = formatDate(graphStartDate, "Y-m-d")
    let addedOrigin = false
    if (!(start in outcomes)) {
        outcomePts.splice(0, 0, [ox, oy])
        addedOrigin = true
    }
    drawGraph(ctx, outcomeLineColor, outcomePtStroke, outcomePtFill, outcomePts, addedOrigin ? [0] : [])
    addedOrigin = false
    if (!(start in incomes)) {
        incomePts.splice(0, 0, [ox, oy])
        addedOrigin = true
    }
    drawGraph(ctx, incomeLineColor, incomePtStroke, incomePtFill, incomePts, addedOrigin ? [0] : [])
}

function drawGraph(ctx, lineColor, strokeColor, fillColor, points, hidden=[]) {
    let withSlopes = []
    for (let i = 0; i < points.length; i++) {
        let pt = points[i]

        let pt0 = pt
        let pt2 = pt
        if (i !== 0) {
            pt0 = points[i - 1]
        }
        if (i !== points.length - 1) {
            pt2 = points[i + 1]
        }
        let dx = pt2[0] - pt0[0]
        let dy = pt2[1] - pt0[1]
        let slope = dy / dx

        let point = {
            slope: slope,
            x: pt[0],
            y: pt[1],
        }

        if (hidden.includes(i)) {
            point.hidden = true
        }

        withSlopes.push(point)
    }

    ctx.strokeStyle = lineColor
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(withSlopes[0].x, withSlopes[0].y)
    for (let i = 0; i < withSlopes.length - 1; i++) {
        let p1 = withSlopes[i]
        let p2 = withSlopes[i + 1]
        let dx = p2.x - p1.x
        let dy1 = p1.slope * dx
        let dy2 = p2.slope * dx

        ctx.bezierCurveTo(
            p1.x + dx / 3,
            p1.y + dy1 / 3,
            p2.x - dx / 3,
            p2.y - dy2 /3,
            p2.x,
            p2.y
        )
    }
    ctx.stroke()

    ctx.strokeStyle = strokeColor
    ctx.fillStyle = fillColor
    for (let i = 0; i < withSlopes.length; i++) {
        let pt = withSlopes[i]
        if (pt.hidden) {
            continue
        }
        ctx.beginPath()
        ctx.ellipse(pt.x, pt.y, 4, 4, 0, 0, Math.PI * 2)
        if (fillColor !== "none") {
            ctx.fill()
        }
        if (strokeColor !== "none") {
            ctx.stroke()
        }
    }
}

window.addEventListener("load", () => {
    document.getElementById("add-transaction").addEventListener("click", () => {
        window.location.href = "/addTransaction/"
    })
    document.getElementById("add-account").addEventListener("click", () => {
        window.location.href = "/addAccount/"
    })

    graphCanvas = document.querySelector("#expenses .chart")
    window.addEventListener("resize", resizeGraph)
    resizeGraph()

    apiGet("accounts/").then(res => {
        if (res.status === "success") {
            accounts = res.accounts
        }
    }).then(refreshDashboard)

    apiGet("categories/").then(res => {
        if (res.status === "success") {
            let categorySelect = document.getElementById("expenses-categories")
            setMultiSelectOptions(categorySelect, res.categories.map(category => {
                return {
                    name: category.name,
                    value: category.id
                }
            }))
        }
    })

    let filters = document.querySelectorAll("#expenses .filters select, #expenses-categories")
    filters.forEach(filter => {
        filter.addEventListener("change", () => updateGraph())
    })
})