// Settings JS
async function loadSettings() {
    try {
        const res = await API.get("/settings");
        const s = res.settings;

        document.getElementById("set-family-name").value = s.family_name || "";
        document.getElementById("set-wedding-name").value = s.wedding_name || "";
        document.getElementById("set-wedding-date").value = s.wedding_date || "";
        document.getElementById("set-currency").value = s.preferred_currency || "BDT";
        document.getElementById("set-signature").value = s.message_signature || "";

        document.getElementById("db-status-badge").textContent = res.database_status;
        document.getElementById("db-type-badge").textContent = res.database_type;
        document.getElementById("ai-status-badge").textContent = res.ai_status;
    } catch (e) {}
}

async function saveSettings(e) {
    e.preventDefault();
    const payload = {
        settings: {
            family_name: document.getElementById("set-family-name").value,
            wedding_name: document.getElementById("set-wedding-name").value,
            wedding_date: document.getElementById("set-wedding-date").value,
            preferred_currency: document.getElementById("set-currency").value,
            message_signature: document.getElementById("set-signature").value
        }
    };

    try {
        await API.put("/settings", payload);
        Utils.showToast("Settings updated successfully!");
        loadSettings();
    } catch (e) {}
}

document.addEventListener("DOMContentLoaded", () => {
    loadSettings();
    document.getElementById("settings-form")?.addEventListener("submit", saveSettings);
});
