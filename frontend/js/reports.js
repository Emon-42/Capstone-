// Reports & Analytics JS
let reportsCategoryChart = null;
let reportsStatusChart = null;

async function loadReports() {
    try {
        const summary = await API.get("/reports/summary");
        const stats = summary.stats;

        document.getElementById("rep-total-guests").textContent = stats.total_guests;
        document.getElementById("rep-total-gifts").textContent = stats.total_gift_records;
        document.getElementById("rep-cash-gifts").textContent = stats.total_cash_gifts;
        document.getElementById("rep-completion-rate").textContent = `${stats.completion_rate_percentage}%`;

        renderReportsCharts(summary);
    } catch (e) {}
}

function renderReportsCharts(summary) {
    const cats = summary.category_distribution || [];
    const stats = summary.stats;

    // Bar Chart for Categories
    const ctxBar = document.getElementById("reportsCategoryChart");
    if (ctxBar) {
        if (reportsCategoryChart) reportsCategoryChart.destroy();
        reportsCategoryChart = new Chart(ctxBar, {
            type: "bar",
            data: {
                labels: cats.map(c => c.category),
                datasets: [{
                    label: "Number of Gifts",
                    data: cats.map(c => c.count),
                    backgroundColor: "#5c55d9",
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } }
                }
            }
        });
    }

    // Pie Chart for Thank-You Statuses
    const ctxPie = document.getElementById("reportsStatusChart");
    if (ctxPie) {
        if (reportsStatusChart) reportsStatusChart.destroy();
        reportsStatusChart = new Chart(ctxPie, {
            type: "pie",
            data: {
                labels: ["Sent", "Pending", "Draft"],
                datasets: [{
                    data: [stats.thank_you_sent, stats.thank_you_pending, stats.thank_you_draft],
                    backgroundColor: ["#10b981", "#f59e0b", "#94a3b8"]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

async function exportCSV(type) {
    try {
        Utils.showToast(`Preparing ${type} CSV export...`);
        const blob = await API.download("/reports/export/csv", { type: type });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `wedding_gift_ledger_${type}_export.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        Utils.showToast("Export downloaded successfully!");
    } catch (e) {}
}

document.addEventListener("DOMContentLoaded", loadReports);
