// Reusable Utility Helpers
const Utils = {
    showToast(message, type = "success") {
        let container = document.getElementById("toast-container");
        if (!container) {
            container = document.createElement("div");
            container.id = "toast-container";
            document.body.appendChild(container);
        }

        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        
        const icon = type === "success" ? "✓" : (type === "warning" ? "⚠" : "✕");
        toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
        
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateX(100%)";
            toast.style.transition = "all 0.3s ease";
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    },

    formatCurrency(amount, currency = "BDT") {
        if (amount === null || amount === undefined || amount === "") {
            return '<span class="text-muted">Unrecorded</span>';
        }
        return `${Number(amount).toLocaleString()} ${currency}`;
    },

    formatDate(dateStr) {
        if (!dateStr) return "-";
        const d = new Date(dateStr);
        return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    },

    getCategoryBadge(category) {
        const catMap = {
            "Household Items": "badge-neutral",
            "Clothing": "badge-purple",
            "Cash": "badge-gold",
            "Jewelry": "badge-warning",
            "Electronics": "badge-success",
            "Decorative Items": "badge-neutral",
            "Unknown": "badge-danger",
            "Other": "badge-neutral"
        };
        const cls = catMap[category] || "badge-neutral";
        return `<span class="badge ${cls}">${category}</span>`;
    },

    getReviewStatusBadge(status) {
        if (status === "confirmed") {
            return `<span class="badge badge-success">✓ Confirmed</span>`;
        } else if (status === "requires_review") {
            return `<span class="badge badge-warning">⚠ Review Needed</span>`;
        } else {
            return `<span class="badge badge-danger">? Unidentified</span>`;
        }
    },

    getThankYouStatusBadge(status) {
        if (status === "sent") {
            return `<span class="badge badge-success">✓ Sent</span>`;
        } else if (status === "pending") {
            return `<span class="badge badge-warning">⏳ Pending</span>`;
        } else {
            return `<span class="badge badge-neutral">Draft</span>`;
        }
    },

    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            Utils.showToast("Copied to clipboard!");
        }).catch(err => {
            Utils.showToast("Failed to copy text", "danger");
        });
    },

    debounce(func, wait = 300) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};
