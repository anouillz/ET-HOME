let accounts = []
async function refreshDashboard() {
    let userId = document.getElementById("userId").value
    let accountsInfo = []
    let accountsPromises = []
    let curMonthDay = new Date()
    let lastMonthTotal = 0
    let curMonthTotal = 0
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
                }
            })
            //document.getElementById("")
        })
        accountsPromises.push(promise)
    })

    await Promise.all(accountsPromises)
    let total = lastMonthTotal + curMonthTotal
    document.querySelector("#current-month .value").innerText = formatMoney(curMonthTotal)
    document.querySelector("#last-month .value").innerText = formatMoney(lastMonthTotal)
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