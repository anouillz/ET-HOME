function formatMoney(amount) {
    let fmt = new Intl.NumberFormat("fr-CH", {style: "currency", currency: "CHF"})
    return fmt.format(amount)
}

function formatPercentage(ratio, withSign=false) {
    let fmt = new Intl.NumberFormat("fr-CH", {maximumFractionDigits: 1})
    let txt = fmt.format(ratio * 100) + "%"
    if (withSign && ratio >= 0) {
        txt = "+" + txt
    }
    return txt
}

function notify(msg) {

}

function apiGet(endpoint, bank=false) {
    return fetch((bank ? "/bank/api/" : "/api/") + endpoint, {
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

function apiPost(endpoint, data, bank=false) {
    let csrftoken = document.querySelector("input[name='csrfmiddlewaretoken']").value
    let headers = {
        "Accept": "application/json",
        "X-CSRFToken": csrftoken
    }
    if (!(data instanceof FormData)) {
        data = JSON.stringify(data)
        headers["Content-Type"] = "application/json"
    }
    return fetch((bank ? "/bank/api/" : "/api/") + endpoint, {
        method: "POST",
        body: data,
        headers: headers
    }).then(res => {
        return res.json()
    }).catch(err => {
        notify("An error occured: " + err)
        return {
            error: err.toString()
        }
    })
}