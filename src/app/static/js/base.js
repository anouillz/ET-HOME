let notificationCount = 0;
let isMenuOpen = false;

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

function formatDate(date, format) {
    let result = ""
    format.split("").forEach(char => {
        switch (char) {
            case "Y":
                result += date.getFullYear().toString().padStart(4, "0")
                break
            case "m":
                result += (date.getMonth() + 1).toString().padStart(2, "0")
                break
            case "d":
                result += date.getDate().toString().padStart(2, "0")
                break
            case "H":
                result += date.getHours().toString().padStart(2, "0")
                break
            case "M":
                result += date.getMinutes().toString().padStart(2, "0")
                break
            case "S":
                result += date.getSeconds().toString().padStart(2, "0")
                break
            default:
                result += char
                break
        }
    })
    return result
}

function initMultiSelects() {
    document.querySelectorAll(".multi-select").forEach(elmt => {
        let btn = elmt.querySelector(".preview")
        btn.addEventListener("click", () => {
            if (elmt.classList.contains("open")) {
                elmt.classList.remove("open")
            } else {
                elmt.classList.add("open")
            }
        })
        window.addEventListener("mousedown", e => {
            if (e.target !== elmt && !elmt.contains(e.target)) {
                elmt.classList.remove("open")
            }
        })
        setMultiSelectOptions(elmt, [])
    })
}

function setMultiSelectOptions(elmt, options) {
    let template = elmt.querySelector(".template.choice").cloneNode(true)
    template.classList.remove("template")

    let optList = elmt.querySelector(".popup")
    optList.innerHTML = ""

    let allOpt = template.cloneNode(true)
    allOpt.classList.add("all")
    let allCb = allOpt.querySelector("input")
    allCb.value = "*"
    allCb.checked = true
    allOpt.querySelector(".text").innerText = elmt.dataset.txtAll
    optList.appendChild(allOpt)

    let checkboxes = []
    options.forEach(option => {
        let opt = template.cloneNode(true)
        let cb = opt.querySelector("input")
        cb.value = option.value
        opt.querySelector(".text").innerText = option.name
        optList.appendChild(opt)
        checkboxes.push(cb)
    })

    allCb.addEventListener("change", () => {
        checkboxes.forEach(cb2 => {
            cb2.checked = allCb.checked
        })
    })

    optList.querySelectorAll("input").forEach(cb => {
        cb.addEventListener("change", () => {
            if (!cb.checked) {
                if (cb.value !== "*") {
                    allCb.checked = false
                }
            } else if (checkboxes.every(cb2 => cb2.checked)) {
                allCb.checked = true
            }
            let value, preview
            if (allCb.checked) {
                value = "*"
                preview = elmt.dataset.txtAll
            } else {
                let values = checkboxes.filter(cb2 => cb2.checked).map(cb2 => cb2.value)
                value = values.join(",")
                preview = values.length + " "
                preview += values.length <= 1 ? elmt.dataset.singular : elmt.dataset.plural
            }
            elmt.setAttribute("value", value)
            elmt.querySelector(".preview").innerText = preview
        })
    })
}

function apiGet(endpoint, bank=false) {
    return fetch((bank ? "/bank/api/" : "/api/") + endpoint, {
        method: "GET",
        headers: {
            "Accept": "application/json"
        }
    }).then(res => {
        if (res.ok) {
            return res.json()
        }
        return res.json().catch(() => {
            return {status: "error", error: `Error ${res.status}`}
        })
    }).catch(err => {
        alert(err)
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
        if (res.ok) {
            return res.json()
        }
        return res.json().catch(() => {
            return {status: "error", error: `Error ${res.status}`}
        })
    }).catch(err => {
        alert(err)
        return {
            error: err.toString()
        }
    })
}

function apiDelete(endpoint, bank=false) {
    let csrftoken = document.querySelector("input[name='csrfmiddlewaretoken']").value
    let headers = {
        "Accept": "application/json",
        "X-CSRFToken": csrftoken
    }
    return fetch((bank ? "/bank/api/" : "/api/") + endpoint, {
        method: "DELETE",
        headers: headers
    }).then(res => {
        if (res.ok) {
            return res.json()
        }
        return res.json().catch(() => {
            return {status: "error", error: `Error ${res.status}`}
        })
    }).catch(err => {
        alert(err)
        return {
            error: err.toString()
        }
    })
}

function toggleNotificationMenu() {
    const panel = document.querySelector('.notification-panel');
    const badge = document.querySelector('.notification-badge');
    isMenuOpen = !isMenuOpen;
    
    if (isMenuOpen) {
        panel.classList.remove('hidden');
        // Reset badge when opening
        notificationCount = 0;
        badge.classList.add('hidden');
    } else {
        panel.classList.add('hidden');
    }
}

function clearAllNotifications() {
    const container = document.getElementById('notification-container');
    for(let child of container.childNodes){
        if(child.id !== undefined){
            apiPost(`notifications/${child.id}/read/`)
        }
    }
    container.innerHTML = '<div class="empty-state">No notifications yet</div>';
    notificationCount = 0;
    document.querySelector('.notification-badge').classList.add('hidden');
}

function showNotification(data) {
    const container = document.getElementById('notification-container');
    const alreadyExisting = document.getElementById(data.id);
    if(alreadyExisting != null){
        return
    }
    const notification = createNotification(data);
    
    // Remove empty state if it exists
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    // Add new notification at the top
    container.insertBefore(notification, container.firstChild);
    
    // Update badge
    updateNotificationBadge(1);
    
    // Highlight animation
    setTimeout(() => {
        notification.classList.remove('new');
    }, 2000);
}

function createIcon(text) {
    return `<div class="notification-icon-text">${text.toUpperCase()}</div>`;
}

function createNotification(data) {
    const notification = document.createElement('div');
    notification.className = `notification ${data.type} new`;
    notification.id = data.id
    notification.innerHTML = `
        ${createIcon(data.type)}
        <div class="notification-message">${data.message}</div>
        <button class="notification-close" onclick="closeNotification(this.parentElement)">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        </button>
    `;
    return notification;
}

function closeNotification(notification) {
    notification.classList.add('removing');
    notification.addEventListener('animationend', () => {
        notification.remove();
        updateNotificationBadge(-1);
        
        // Show empty state if no notifications
        const container = document.getElementById('notification-container');
        if (container.children.length === 0) {
            container.innerHTML = '<div class="empty-state">No notifications yet</div>';
        }

        apiPost(`notifications/${notification.id}/read/`)
    });
}

function fetchNotifications(){
    let timer = setInterval(function(){
        apiGet("notifications/",false).then(data => {
            for (let notification of data.notifications) {
                showNotification(notification)
            }
        })

    },3000)
}

function updateNotificationBadge(change) {
    const badge = document.querySelector('.notification-badge');
    notificationCount = Math.max(0, notificationCount + change);
    
    if (notificationCount > 0) {
        badge.textContent = notificationCount;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

window.addEventListener("load", () => {
    fetchNotifications()
    initMultiSelects()
})
