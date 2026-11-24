// Gift History & Future Reciprocity Ledger JS
let allHistoryRecords = [];
let allGuestsCache = [];

async function loadHistory() {
    try {
        const guests = await API.get("/guests", { page_size: 100 });
        allGuestsCache = guests.items;
        populateGuestSelector();

        allHistoryRecords = await API.get("/gift-history");
        renderFullHistoryTable(allHistoryRecords);

        // Pre-select first guest with reciprocity (e.g., Rahman Uncle)
        const rahman = allGuestsCache.find(g => g.full_name.includes("Rahman"));
        if (rahman) {
            selectGuestForComparison(rahman.id);
        }
    } catch (e) {}
}

function populateGuestSelector() {
    const select = document.getElementById("guest-reciprocity-select");
    if (!select) return;
    select.innerHTML = `<option value="">-- Select Guest or Family to Compare --</option>`;
    allGuestsCache.forEach(g => {
        select.innerHTML += `<option value="${g.id}">${g.full_name} (${g.family_group || g.relationship_type})</option>`;
    });

    const modalGuestSelect = document.getElementById("modal-return-guest");
    if (modalGuestSelect) {
        modalGuestSelect.innerHTML = `<option value="">Select Recipient Guest...</option>`;
        allGuestsCache.forEach(g => {
            modalGuestSelect.innerHTML += `<option value="${g.id}">${g.full_name} (${g.family_group || g.relationship_type})</option>`;
        });
    }
}

async function selectGuestForComparison(guestId) {
    if (!guestId) return;
    document.getElementById("guest-reciprocity-select").value = guestId;

    try {
        const comp = await API.get(`/gift-history/reciprocity/${guestId}`);
        renderComparisonView(comp);
    } catch (e) {}
}

function renderComparisonView(comp) {
    const container = document.getElementById("comparison-container");
    if (!container) return;
    container.style.display = "block";

    document.getElementById("comp-guest-name").textContent = comp.guest_name;
    document.getElementById("comp-family-name").textContent = comp.family_group ? `(${comp.family_group})` : "";
    
    // Received list
    const recList = document.getElementById("comp-received-list");
    recList.innerHTML = "";
    if (comp.gifts_received.length === 0) {
        recList.innerHTML = `<div class="text-muted" style="padding: 16px;">No recorded gifts received from this guest.</div>`;
    } else {
        comp.gifts_received.forEach(r => {
            const item = document.createElement("div");
            item.className = "card";
            item.style.marginBottom = "10px";
            item.style.padding = "14px";
            item.innerHTML = `
                <div style="font-weight: 600; font-size: 14px;">${r.gift_description}</div>
                <div style="font-size: 12px; color: var(--gold); margin: 2px 0;">Event: ${r.event_name} • Date: ${Utils.formatDate(r.event_date)}</div>
                ${r.recorded_value ? `<div class="badge badge-gold">Explicit Value: ${Number(r.recorded_value).toLocaleString()} ${r.currency}</div>` : ''}
                ${r.notes ? `<div style="font-size: 11.5px; color: var(--text-muted); margin-top: 4px;">${r.notes}</div>` : ''}
            `;
            recList.appendChild(item);
        });
    }

    // Given list
    const givList = document.getElementById("comp-given-list");
    givList.innerHTML = "";
    if (comp.gifts_given_in_return.length === 0) {
        givList.innerHTML = `
            <div style="padding: 16px; background: #fffbeb; border: 1px dashed #fcd34d; border-radius: var(--radius-md); text-align: center;">
                <p style="color: #92400e; font-size: 13px; font-weight: 600;">No return gift recorded yet.</p>
                <p style="color: #b45309; font-size: 12px; margin-top: 4px;">When Farhana's family attends their future wedding, record the gift given here.</p>
                <button class="btn btn-sm btn-gold" style="margin-top: 10px;" onclick="openReturnGiftModal(${comp.guest_id})">+ Record Gift Given</button>
            </div>
        `;
    } else {
        comp.gifts_given_in_return.forEach(g => {
            const item = document.createElement("div");
            item.className = "card";
            item.style.marginBottom = "10px";
            item.style.padding = "14px";
            item.style.borderLeft = "4px solid var(--success)";
            item.innerHTML = `
                <div style="font-weight: 600; font-size: 14px;">${g.gift_description}</div>
                <div style="font-size: 12px; color: var(--success); margin: 2px 0;">Reciprocal Event: ${g.event_name} • Date: ${Utils.formatDate(g.event_date)}</div>
                ${g.recorded_value ? `<div class="badge badge-gold">Recorded Value: ${Number(g.recorded_value).toLocaleString()} ${g.currency}</div>` : ''}
                ${g.notes ? `<div style="font-size: 11.5px; color: var(--text-muted); margin-top: 4px;">${g.notes}</div>` : ''}
            `;
            givList.appendChild(item);
        });
    }
}

function renderFullHistoryTable(records) {
    const tbody = document.getElementById("full-history-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    records.forEach(r => {
        const tr = document.createElement("tr");
        const typeBadge = r.event_type === "received" 
            ? `<span class="badge badge-purple">📥 Received</span>` 
            : `<span class="badge badge-success">📤 Given Return</span>`;

        tr.innerHTML = `
            <td><strong>${r.guest_name}</strong></td>
            <td>${typeBadge}</td>
            <td>${r.gift_description}</td>
            <td>${r.event_name}</td>
            <td>${Utils.formatDate(r.event_date)}</td>
            <td>${r.recorded_value ? Number(r.recorded_value).toLocaleString() + ' ' + r.currency : '<span class="text-muted">Not Recorded</span>'}</td>
            <td>${r.notes || "-"}</td>
        `;
        tbody.appendChild(tr);
    });
}

function openReturnGiftModal(prefillGuestId = null) {
    document.getElementById("return-gift-form").reset();
    if (prefillGuestId) {
        document.getElementById("modal-return-guest").value = prefillGuestId;
    }
    document.getElementById("return-gift-modal").classList.add("show");
}

function closeReturnGiftModal() {
    document.getElementById("return-gift-modal").classList.remove("show");
}

async function saveReturnGift(e) {
    e.preventDefault();
    const guestId = Number(document.getElementById("modal-return-guest").value);
    const eventName = document.getElementById("modal-event-name").value;
    const eventDate = document.getElementById("modal-event-date").value;
    const giftDesc = document.getElementById("modal-gift-desc").value;
    const category = document.getElementById("modal-category").value;
    const notes = document.getElementById("modal-notes").value;

    const payload = {
        guest_id: guestId || null,
        event_name: eventName,
        event_type: "given_return",
        gift_description: giftDesc,
        category: category,
        event_date: eventDate || new Date().toISOString().split("T")[0],
        notes: notes || "Reciprocal gift given by Farhana's family"
    };

    try {
        await API.post("/gift-history", payload);
        Utils.showToast("Reciprocal gift record saved!");
        closeReturnGiftModal();
        loadHistory();
    } catch (e) {}
}

document.addEventListener("DOMContentLoaded", () => {
    loadHistory();
    document.getElementById("guest-reciprocity-select")?.addEventListener("change", (e) => {
        selectGuestForComparison(e.target.value);
    });
    document.getElementById("return-gift-form")?.addEventListener("submit", saveReturnGift);
});
