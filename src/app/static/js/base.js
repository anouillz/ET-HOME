function formatMoney(amount) {
    let fmt = new Intl.NumberFormat("fr-CH", {style: "currency", currency: "CHF"})
    return fmt.format(amount)
}

function notify(msg) {

}

function apiGet(endpoint) {
    return fetch("api/" + endpoint, {
        method: "GET",
        headers: {
            "Accept": "application/json"
        }
    }).then(res => {
        return res.json()
    }).catch(err => {
        notify("An error occurred: " + err)
        return {
            error: err.toString()
        }
    })
}

function apiPost(endpoint, data) {
    return fetch("api/" + endpoint, {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    }).then(res => {
        return res.json()
    }).catch(err => {
        notify("An error occured: " + err)
        return {
            error: err.toString()
        }
    })
}