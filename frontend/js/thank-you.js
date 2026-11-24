// Thank You Message Management JS
let currentStatusFilter = "all";
let currentPage = 1;
const pageSize = 15;
let allGiftsCache = [];
let allGuestsCache = [];

async function loadThankYouMessages() {
    const search = document.getElementById("search-input")?.value || "";
    const params = {
        page: currentPage,
        page_size: pageSize
    };
    if (currentStatusFilter !== "all") params.status = currentStatusFilter;
    if (search) params.search = search;

    try {
        const res = await API.get("/thank-you", params);
        renderMessages(res.items);
        renderPagination(res.page, res.total_pages, res.total);
    } catch (e) {}
}

function renderMessages(messages) {
    const container = document.getElementById("messages-grid");
    if (!container) return;
    container.innerHTML = "";

    if (messages.length === 0) {
        container.innerHTML = `<div class="card text-center text-muted" style="grid-column: 1/-1; padding: 40px;">No thank-you messages in this view.</div>`;
        return;
    }

    messages.forEach(m => {
        const card = document.createElement("div");
        card.className = "card";
        card.style.marginBottom = "16px";

        const isSent = m.status === "sent";
        const sentBadge = Utils.getThankYouStatusBadge(m.status);

        card.innerHTML = `
            <div class="card-header" style="margin-bottom: 12px;">
                <div>
                    <div style="font-weight: 700; font-size: 15px;">${m.guest_name}</div>
                    <div style="font-size: 12px; color: var(--gold);">${m.relationship_type || 'Guest'} • Gift: ${m.gift_name}</div>
                </div>
                <div>${sentBadge}</div>
            </div>
            <div style="background: var(--bg-subtle); padding: 14px; border-radius: var(--radius-md); font-size: 13.5px; white-space: pre-line; line-height: 1.6; margin-bottom: 14px; border: 1px solid var(--border-light);">
${m.message_text}
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
                <div style="font-size: 11.5px; color: var(--text-muted);">
                    Tone: <strong>${m.tone.toUpperCase()}</strong> ${m.sent_date ? '• Sent ' + Utils.formatDate(m.sent_date) + ' via ' + (m.sent_via || 'Direct') : ''}
                </div>
                <div style="display: flex; gap: 8px;">
                    <button class="btn btn-sm btn-secondary" onclick="copyMessageText('${encodeURIComponent(m.message_text)}')">📋 Copy</button>
                    <button class="btn btn-sm btn-secondary" onclick="openEditMessageModal(${m.id})">Edit</button>
                    ${!isSent ? `<button class="btn btn-sm btn-primary" onclick="markAsSentPrompt(${m.id})">✓ Mark as Sent</button>` : ''}
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

function renderPagination(page, totalPages, total) {
    const el = document.getElementById("pagination-info");
    const container = document.getElementById("pagination-controls");
    if (el) el.textContent = `Showing page ${page} of ${totalPages} (${total} total messages)`;
    
    if (container) {
        container.innerHTML = `
            <button class="btn btn-sm btn-secondary" ${page <= 1 ? "disabled" : ""} onclick="changePage(${page - 1})">Previous</button>
            <span style="font-size: 13px; font-weight: 600; padding: 0 8px;">${page}</span>
            <button class="btn btn-sm btn-secondary" ${page >= totalPages ? "disabled" : ""} onclick="changePage(${page + 1})">Next</button>
        `;
    }
}

function changePage(p) {
    currentPage = p;
    loadThankYouMessages();
}

function filterTab(status, tabBtn) {
    currentStatusFilter = status;
    currentPage = 1;
    document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
    tabBtn.classList.add("active");
    loadThankYouMessages();
}

function copyMessageText(encoded) {
    const text = decodeURIComponent(encoded);
    Utils.copyToClipboard(text);
}

async function markAsSentPrompt(id) {
    const channel = prompt("Enter delivery channel (e.g., WhatsApp, SMS, Printed Card, In Person):", "WhatsApp");
    if (channel !== null) {
        try {
            await API.post(`/thank-you/${id}/mark-sent?sent_via=${encodeURIComponent(channel)}`);
            Utils.showToast("Thank you message marked as sent!");
            loadThankYouMessages();
        } catch (e) {}
    }
}

async function preloadDropdowns() {
    try {
        const guests = await API.get("/guests", { page_size: 100 });
        allGuestsCache = guests.items;
        const gifts = await API.get("/gifts", { page_size: 100 });
        allGiftsCache = gifts.items;

        const gSelect = document.getElementById("gen-guest-select");
        if (gSelect) {
            gSelect.innerHTML = `<option value="">Select Guest...</option>`;
            allGuestsCache.forEach(g => {
                gSelect.innerHTML += `<option value="${g.id}">${g.full_name} (${g.relationship_type})</option>`;
            });
        }

        const giftSelect = document.getElementById("gen-gift-select");
        if (giftSelect) {
            giftSelect.innerHTML = `<option value="">Select Gift...</option>`;
            allGiftsCache.forEach(gift => {
                giftSelect.innerHTML += `<option value="${gift.id}">${gift.gift_name} (${gift.gift_category})</option>`;
            });
        }
    } catch (e) {}
}

function openGenerateModal() {
    document.getElementById("generator-modal").classList.add("show");
}

function closeGeneratorModal() {
    document.getElementById("generator-modal").classList.remove("show");
}

async function generateWithAI() {
    const guestId = document.getElementById("gen-guest-select").value;
    const giftId = document.getElementById("gen-gift-select").value;
    const tone = document.getElementById("gen-tone-select").value;
    const note = document.getElementById("gen-custom-note").value;

    if (!guestId || !giftId) {
        Utils.showToast("Please select both a guest and their gift.", "warning");
        return;
    }

    try {
        const res = await API.post("/thank-you/generate", {
            guest_id: Number(guestId),
            gift_id: Number(giftId),
            tone: tone,
            custom_note: note || null
        });

        document.getElementById("gen-preview-box").style.display = "block";
        document.getElementById("gen-preview-text").value = res.message_text;
        Utils.showToast("Message generated! Notice: cash amounts are respectfully omitted.");
    } catch (e) {}
}

async function saveGeneratedMessage() {
    const guestId = Number(document.getElementById("gen-guest-select").value);
    const giftId = Number(document.getElementById("gen-gift-select").value);
    const tone = document.getElementById("gen-tone-select").value;
    const msgText = document.getElementById("gen-preview-text").value;

    try {
        // Find existing message or update
        const res = await API.get("/thank-you", { page_size: 100 });
        const existing = res.items.find(m => m.guest_id === guestId && m.gift_id === giftId);
        if (existing) {
            await API.put(`/thank-you/${existing.id}`, {
                message_text: msgText,
                tone: tone,
                status: "pending"
            });
        }
        Utils.showToast("Thank you message saved to ledger!");
        closeGeneratorModal();
        loadThankYouMessages();
    } catch (e) {}
}

document.addEventListener("DOMContentLoaded", () => {
    preloadDropdowns();
    loadThankYouMessages();
    document.getElementById("search-input")?.addEventListener("input", Utils.debounce(loadThankYouMessages, 300));
});
