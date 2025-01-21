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
        if(child.id != undefined){
            apiGet("read_notification/"+child.id)
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

    apiGet("read_notification/"+notification.id)
    });
}

function fetchNotifications(){
    var timer = setInterval(function(){
        apiGet("get_notifications",false).then(data => {
            for(let notification of data.notifications){
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

fetchNotifications()