// Guest Management JS
let currentPage = 1;
const pageSize = 15;

async function loadGuests() {
    const search = document.getElementById("search-input")?.value || "";
    const relationship = document.getElementById("relationship-filter")?.value || "";
    const unidentifiedOnly = document.getElementById("unidentified-checkbox")?.checked;

    const params = {
        page: currentPage,
        page_size: pageSize
    };
    if (search) params.search = search;
    if (relationship && relationship !== "all") params.relationship = relationship;
    if (unidentifiedOnly) params.is_unidentified = true;

    try {
        const res = await API.get("/guests", params);
        renderGuestTable(res.items);
        renderPagination(res.page, res.total_pages, res.total);
    } catch (e) {
        console.error(e);
    }
}

function renderGuestTable(guests) {
    const tbody = document.getElementById("guests-table-body");
    tbody.innerHTML = "";

    if (guests.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted" style="padding: 30px;">No guests found matching criteria.</td></tr>`;
        return;
    }

    guests.forEach(g => {
        const tr = document.createElement("tr");
        const statusBadge = g.is_unidentified 
            ? `<span class="badge badge-danger">? Unidentified</span>` 
            : `<span class="badge badge-success">✓ Identified</span>`;

        tr.innerHTML = `
            <td>
                <div style="font-weight: 600;">${g.full_name}</div>
                ${g.family_group ? `<div style="font-size: 11.5px; color: var(--gold);">${g.family_group}</div>` : ""}
            </td>
            <td>${g.relationship_type || "Guest"}</td>
            <td>${statusBadge}</td>
            <td>${g.phone_number || '<span class="text-muted">-</span>'}</td>
            <td>${g.total_gifts_contributed} gift(s)</td>
            <td>${Utils.getThankYouStatusBadge(g.thank_you_status)}</td>
            <td>
                <div style="display: flex; gap: 6px;">
                    <button class="btn btn-sm btn-secondary" onclick="openEditGuestModal(${g.id})">Edit</button>
                    <button class="btn btn-sm btn-secondary" style="color: var(--danger);" onclick="deleteGuest(${g.id}, '${g.full_name}')">Delete</button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderPagination(page, totalPages, total) {
    const el = document.getElementById("pagination-info");
    const container = document.getElementById("pagination-controls");
    if (el) el.textContent = `Showing page ${page} of ${totalPages} (${total} total guests)`;
    
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
    loadGuests();
}

function openAddGuestModal() {
    document.getElementById("guest-modal-title").textContent = "Add New Guest";
    document.getElementById("guest-form").reset();
    document.getElementById("guest-id").value = "";
    document.getElementById("guest-modal").classList.add("show");
}

async function openEditGuestModal(id) {
    try {
        const guest = await API.get(`/guests/${id}`);
        document.getElementById("guest-modal-title").textContent = "Edit Guest Details";
        document.getElementById("guest-id").value = guest.id;
        document.getElementById("guest-name").value = guest.full_name;
        document.getElementById("guest-relationship").value = guest.relationship_type || "";
        document.getElementById("guest-phone").value = guest.phone_number || "";
        document.getElementById("guest-email").value = guest.email || "";
        document.getElementById("guest-family").value = guest.family_group || "";
        document.getElementById("guest-unidentified").checked = guest.is_unidentified;
        document.getElementById("guest-notes").value = guest.notes || "";
        document.getElementById("guest-modal").classList.add("show");
    } catch (e) {}
}

function closeGuestModal() {
    document.getElementById("guest-modal").classList.remove("show");
}

async function saveGuest(e) {
    e.preventDefault();
    const id = document.getElementById("guest-id").value;
    const payload = {
        full_name: document.getElementById("guest-name").value,
        relationship_type: document.getElementById("guest-relationship").value,
        phone_number: document.getElementById("guest-phone").value || null,
        email: document.getElementById("guest-email").value || null,
        family_group: document.getElementById("guest-family").value || null,
        is_unidentified: document.getElementById("guest-unidentified").checked,
        notes: document.getElementById("guest-notes").value || null
    };

    try {
        if (id) {
            await API.put(`/guests/${id}`, payload);
            Utils.showToast("Guest updated successfully!");
        } else {
            await API.post("/guests", payload);
            Utils.showToast("Guest added successfully!");
        }
        closeGuestModal();
        loadGuests();
    } catch (e) {}
}

async function deleteGuest(id, name) {
    if (confirm(`Are you sure you want to delete ${name}? Note: Historical gift reciprocity records will be preserved.`)) {
        try {
            await API.delete(`/guests/${id}`);
            Utils.showToast("Guest record deleted safely.");
            loadGuests();
        } catch (e) {}
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadGuests();
    document.getElementById("search-input")?.addEventListener("input", Utils.debounce(loadGuests, 300));
    document.getElementById("relationship-filter")?.addEventListener("change", loadGuests);
    document.getElementById("unidentified-checkbox")?.addEventListener("change", loadGuests);
    document.getElementById("guest-form")?.addEventListener("submit", saveGuest);
});
