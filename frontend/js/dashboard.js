// Dashboard JS Logic
let categoryChart = null;
let completionChart = null;

async function loadDashboard() {
    try {
        const stats = await API.get("/dashboard/stats");
        
        document.getElementById("stat-total-guests").textContent = stats.total_guests;
        document.getElementById("stat-total-gifts").textContent = stats.total_gift_records;
        document.getElementById("stat-total-contributors").textContent = stats.total_contributors;
        document.getElementById("stat-thank-you-sent").textContent = stats.thank_you_sent;
        document.getElementById("stat-thank-you-pending").textContent = stats.thank_you_pending;
        document.getElementById("stat-unidentified-gifts").textContent = stats.unidentified_gifts;
        document.getElementById("stat-review-needed").textContent = stats.gifts_requiring_review;

        renderCharts(stats);
        loadRecentActivity();
        loadPendingThankYous();
        loadUnidentifiedGifts();
    } catch (err) {
        console.error("Dashboard load failed:", err);
    }
}

async function renderCharts(stats) {
    const summary = await API.get("/reports/summary");
    const categories = summary.category_distribution || [];
    
    // Category Doughnut Chart
    const ctxCat = document.getElementById("categoryChart");
    if (ctxCat) {
        if (categoryChart) categoryChart.destroy();
        categoryChart = new Chart(ctxCat, {
            type: "doughnut",
            data: {
                labels: categories.map(c => c.category),
                datasets: [{
                    data: categories.map(c => c.count),
                    backgroundColor: [
                        "#5c55d9", "#c28829", "#10b981", "#f59e0b",
                        "#0ea5e9", "#ec4899", "#8b5cf6", "#94a3b8"
                    ],
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "right" }
                }
            }
        });
    }

    // Completion Rate Chart
    const ctxComp = document.getElementById("completionChart");
    if (ctxComp) {
        if (completionChart) completionChart.destroy();
        const sent = stats.thank_you_sent;
        const pending = stats.thank_you_pending + stats.thank_you_draft;
        completionChart = new Chart(ctxComp, {
            type: "doughnut",
            data: {
                labels: ["Thanked", "Pending"],
                datasets: [{
                    data: [sent, pending],
                    backgroundColor: ["#10b981", "#e2e8f0"],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "75%",
                plugins: {
                    legend: { display: false }
                }
            }
        });
        document.getElementById("completion-rate-text").textContent = `${stats.completion_rate_percentage}%`;
    }
}

async function loadRecentActivity() {
    try {
        const activities = await API.get("/dashboard/recent-activity");
        const list = document.getElementById("activity-list");
        if (!list) return;
        
        list.innerHTML = "";
        if (activities.length === 0) {
            list.innerHTML = `<li class="text-muted">No recent activities.</li>`;
            return;
        }

        activities.slice(0, 5).forEach(act => {
            const item = document.createElement("li");
            item.className = "timeline-item";
            item.innerHTML = `
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                    <div class="timeline-title">${act.title}</div>
                    <div class="timeline-desc">${act.description}</div>
                    <div class="timeline-time">${act.timestamp}</div>
                </div>
            `;
            list.appendChild(item);
        });
    } catch (e) {}
}

async function loadPendingThankYous() {
    try {
        const res = await API.get("/thank-you", { status: "pending", page_size: 4 });
        const tbody = document.getElementById("pending-thank-you-table");
        if (!tbody) return;

        tbody.innerHTML = "";
        if (res.items.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">All guests have been thanked! 🎉</td></tr>`;
            return;
        }

        res.items.forEach(m => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${m.guest_name}</strong></td>
                <td>${m.gift_name}</td>
                <td><span class="badge badge-warning">Pending</span></td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="quickSendThankYou(${m.id})">Send</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {}
}

async function loadUnidentifiedGifts() {
    try {
        const res = await API.get("/gifts", { review_status: "requires_review", page_size: 4 });
        const tbody = document.getElementById("unidentified-gifts-table");
        if (!tbody) return;

        tbody.innerHTML = "";
        if (res.items.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">No gifts requiring review.</td></tr>`;
            return;
        }

        res.items.forEach(g => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${g.gift_name}</strong></td>
                <td><div class="original-note-box">${g.original_note}</div></td>
                <td>${Utils.getReviewStatusBadge(g.review_status)}</td>
                <td>
                    <a href="gifts.html?highlight=${g.id}" class="btn btn-sm btn-secondary">Review</a>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {}
}

async function quickSendThankYou(msgId) {
    try {
        await API.post(`/thank-you/${msgId}/mark-sent?sent_via=WhatsApp`);
        Utils.showToast("Thank you message marked as sent via WhatsApp!");
        loadDashboard();
    } catch (e) {}
}

document.addEventListener("DOMContentLoaded", loadDashboard);
