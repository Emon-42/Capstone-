// Gift Management JS
let currentPage = 1;
const pageSize = 15;
let allGuestsCache = [];

async function loadGifts() {
    const search = document.getElementById("search-input")?.value || "";
    const category = document.getElementById("category-filter")?.value || "";
    const reviewStatus = document.getElementById("status-filter")?.value || "";
    const cashFilter = document.getElementById("cash-filter")?.value || "";

    const params = {
        page: currentPage,
        page_size: pageSize
    };
    if (search) params.search = search;
    if (category && category !== "all") params.category = category;
    if (reviewStatus && reviewStatus !== "all") params.review_status = reviewStatus;
    if (cashFilter === "cash") params.is_cash = true;
    if (cashFilter === "non_cash") params.is_cash = false;

    try {
        const res = await API.get("/gifts", params);
        renderGiftTable(res.items);
        renderPagination(res.page, res.total_pages, res.total);
    } catch (e) {
        console.error(e);
    }
}

function renderGiftTable(gifts) {
    const tbody = document.getElementById("gifts-table-body");
    tbody.innerHTML = "";

    if (gifts.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted" style="padding: 30px;">No gifts found matching criteria.</td></tr>`;
        return;
    }

    gifts.forEach(g => {
        const tr = document.createElement("tr");

        // Contributors formatting
        const contribTags = g.contributors.map(c => {
            const isJoint = g.contributors.length > 1;
            return `<span class="badge ${isJoint ? 'badge-purple' : 'badge-neutral'}">${c.guest_name}</span>`;
        }).join(" ");

        // Cash formatting
        let cashDisplay = "-";
        if (g.is_cash) {
            cashDisplay = g.cash_amount 
                ? `<span class="badge badge-gold">${Number(g.cash_amount).toLocaleString()} ${g.currency}</span>`
                : `<span class="badge badge-warning">Amount Unknown</span>`;
        }

        tr.innerHTML = `
            <td>
                <div style="font-weight: 600;">${g.gift_name}</div>
                <div class="original-note-box" title="Exact Handwritten Note as Collected">
                    📝 Note: "${g.original_note}"
                </div>
            </td>
            <td>${Utils.getCategoryBadge(g.gift_category)}</td>
            <td>${contribTags || '<span class="text-muted">Unidentified</span>'}</td>
            <td>${cashDisplay}</td>
            <td>${Utils.getReviewStatusBadge(g.review_status)}</td>
            <td>${Utils.formatDate(g.gift_date)}</td>
            <td>
                <div style="display: flex; gap: 6px;">
                    <button class="btn btn-sm btn-secondary" onclick="openEditGiftModal(${g.id})">Edit</button>
                    <button class="btn btn-sm btn-secondary" style="color: var(--danger);" onclick="deleteGift(${g.id}, '${g.gift_name}')">Delete</button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderPagination(page, totalPages, total) {
    const el = document.getElementById("pagination-info");
    const container = document.getElementById("pagination-controls");
    if (el) el.textContent = `Showing page ${page} of ${totalPages} (${total} total gift records)`;
    
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
    loadGifts();
}

async function preloadGuests() {
    try {
        const res = await API.get("/guests", { page_size: 100 });
        allGuestsCache = res.items;
        populateContributorDropdown();
    } catch (e) {}
}

function populateContributorDropdown(selectedIds = []) {
    const select = document.getElementById("gift-contributors");
    if (!select) return;
    select.innerHTML = "";
    allGuestsCache.forEach(g => {
        const opt = document.createElement("option");
        opt.value = g.id;
        opt.textContent = `${g.full_name} (${g.relationship_type || 'Guest'}${g.family_group ? ' - ' + g.family_group : ''})`;
        if (selectedIds.includes(g.id)) opt.selected = true;
        select.appendChild(opt);
    });
}

function openAddGiftModal() {
    document.getElementById("gift-modal-title").textContent = "Record New Gift";
    document.getElementById("gift-form").reset();
    document.getElementById("gift-id").value = "";
    document.getElementById("ai-suggestion-box").style.display = "none";
    populateContributorDropdown();
    document.getElementById("gift-modal").classList.add("show");
}

async function openEditGiftModal(id) {
    try {
        const gift = await API.get(`/gifts/${id}`);
        document.getElementById("gift-modal-title").textContent = "Edit Gift Record";
        document.getElementById("gift-id").value = gift.id;
        document.getElementById("gift-name").value = gift.gift_name;
        document.getElementById("gift-category").value = gift.gift_category;
        document.getElementById("gift-quantity").value = gift.quantity;
        document.getElementById("gift-is-cash").checked = gift.is_cash;
        document.getElementById("gift-cash-amount").value = gift.cash_amount || "";
        document.getElementById("gift-original-note").value = gift.original_note;
        document.getElementById("gift-status").value = gift.review_status;
        document.getElementById("gift-additional-notes").value = gift.additional_notes || "";
        
        const selIds = gift.contributors.map(c => c.guest_id);
        populateContributorDropdown(selIds);

        document.getElementById("ai-suggestion-box").style.display = "none";
        document.getElementById("gift-modal").classList.add("show");
    } catch (e) {}
}

function closeGiftModal() {
    document.getElementById("gift-modal").classList.remove("show");
}

// AI Note Processing in Modal
async function analyzeNoteWithAI() {
    const noteText = document.getElementById("gift-original-note").value.trim();
    if (!noteText) {
        Utils.showToast("Please enter an original handwritten note to analyze", "warning");
        return;
    }

    const btn = document.getElementById("ai-analyze-btn");
    btn.disabled = true;
    btn.textContent = "Analyzing Note...";

    try {
        const res = await API.post("/ai/process-note", { note_text: noteText });
        const ext = res.extracted_data;

        const box = document.getElementById("ai-suggestion-box");
        box.style.display = "block";

        let html = `
            <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                <div style="font-weight: 700; color: var(--primary); margin-bottom: 6px;">
                    ✨ AI Extraction Suggestions (Confidence: ${(ext.confidence_score * 100).toFixed(0)}%)
                </div>
                <div style="font-size: 13px;">
                    <div><strong>Giver(s):</strong> ${ext.possible_guest_names.join(", ") || "Unknown"}</div>
                    <div><strong>Gift:</strong> ${ext.gift_name} (${ext.gift_category})</div>
                    <div><strong>Is Cash:</strong> ${ext.is_cash ? "Yes" : "No"} | <strong>Amount:</strong> ${ext.cash_amount !== null ? ext.cash_amount : "Not specified"}</div>
                </div>
        `;

        if (ext.uncertain_fields.length > 0 || ext.missing_fields.length > 0) {
            html += `
                <div style="margin-top: 8px; padding: 6px 10px; background: #fffbeb; border: 1px solid #fde68a; border-radius: 6px; font-size: 12px; color: #b45309;">
                    ⚠ <strong>Review Required:</strong> ${[...ext.uncertain_fields, ...ext.missing_fields].join(", ")}
                </div>
            `;
        }

        html += `
            <div style="margin-top: 10px;">
                <button type="button" class="btn btn-sm btn-primary" onclick="applyAISuggestions('${encodeURIComponent(JSON.stringify(ext))}')">
                    Apply Suggestions to Form
                </button>
            </div>
            </div>
        `;
        box.innerHTML = html;
    } catch (e) {
    } finally {
        btn.disabled = false;
        btn.textContent = "✨ AI Extract Note";
    }
}

function applyAISuggestions(encodedData) {
    const ext = JSON.parse(decodeURIComponent(encodedData));
    document.getElementById("gift-name").value = ext.gift_name;
    document.getElementById("gift-category").value = ext.gift_category;
    document.getElementById("gift-quantity").value = ext.quantity;
    document.getElementById("gift-is-cash").checked = ext.is_cash;
    if (ext.cash_amount !== null) {
        document.getElementById("gift-cash-amount").value = ext.cash_amount;
    }
    if (ext.suggested_action === "review" || ext.missing_fields.length > 0) {
        document.getElementById("gift-status").value = "requires_review";
    } else {
        document.getElementById("gift-status").value = "confirmed";
    }

    // Try selecting matching guests in cache
    const matchedGuestIds = [];
    ext.possible_guest_names.forEach(pName => {
        const found = allGuestsCache.find(g => g.full_name.toLowerCase().includes(pName.toLowerCase()));
        if (found) matchedGuestIds.push(found.id);
    });
    if (matchedGuestIds.length > 0) {
        populateContributorDropdown(matchedGuestIds);
    }

    Utils.showToast("AI suggestions applied to form. Please review and save!");
}

async function saveGift(e) {
    e.preventDefault();
    const id = document.getElementById("gift-id").value;
    const isCash = document.getElementById("gift-is-cash").checked;
    const cashVal = document.getElementById("gift-cash-amount").value;

    const selectEl = document.getElementById("gift-contributors");
    const selectedContribs = Array.from(selectEl.selectedOptions).map(opt => Number(opt.value));

    const payload = {
        event_id: 1, // Default primary wedding event
        gift_name: document.getElementById("gift-name").value,
        gift_category: document.getElementById("gift-category").value,
        quantity: Number(document.getElementById("gift-quantity").value) || 1,
        is_cash: isCash,
        cash_amount: (isCash && cashVal) ? Number(cashVal) : null,
        currency: "BDT",
        original_note: document.getElementById("gift-original-note").value,
        review_status: document.getElementById("gift-status").value,
        additional_notes: document.getElementById("gift-additional-notes").value || null,
        contributor_ids: selectedContribs
    };

    try {
        if (id) {
            await API.put(`/gifts/${id}`, payload);
            Utils.showToast("Gift record updated successfully!");
        } else {
            await API.post("/gifts", payload);
            Utils.showToast("Gift recorded successfully!");
        }
        closeGiftModal();
        loadGifts();
    } catch (e) {}
}

async function deleteGift(id, name) {
    if (confirm(`Are you sure you want to delete gift "${name}"?`)) {
        try {
            await API.delete(`/gifts/${id}`);
            Utils.showToast("Gift record deleted.");
            loadGifts();
        } catch (e) {}
    }
}

document.addEventListener("DOMContentLoaded", () => {
    preloadGuests();
    loadGifts();
    document.getElementById("search-input")?.addEventListener("input", Utils.debounce(loadGifts, 300));
    document.getElementById("category-filter")?.addEventListener("change", loadGifts);
    document.getElementById("status-filter")?.addEventListener("change", loadGifts);
    document.getElementById("cash-filter")?.addEventListener("change", loadGifts);
    document.getElementById("gift-form")?.addEventListener("submit", saveGift);
});
