// Auth state management
const Auth = {
    getUser() {
        const u = localStorage.getItem("user");
        return u ? JSON.parse(u) : { full_name: "Farhana Rahman", role: "admin", username: "admin" };
    },

    setUser(userData, token) {
        localStorage.setItem("user", JSON.stringify(userData));
        if (token) localStorage.setItem("token", token);
    },

    logout() {
        localStorage.removeItem("user");
        localStorage.removeItem("token");
        window.location.href = "index.html";
    },

    initUserDisplay() {
        const user = this.getUser();
        const nameEl = document.querySelector(".user-name");
        const roleEl = document.querySelector(".user-role");
        const avatarEl = document.querySelector(".user-avatar");
        
        if (nameEl) nameEl.textContent = user.full_name || "Farhana Rahman";
        if (roleEl) roleEl.textContent = (user.role || "Admin").toUpperCase();
        if (avatarEl) {
            const initials = (user.full_name || "FR").split(" ").map(n => n[0]).join("").substring(0, 2);
            avatarEl.textContent = initials;
        }
    }
};

document.addEventListener("DOMContentLoaded", () => {
    Auth.initUserDisplay();
    // Mobile navigation toggle
    const toggleBtn = document.querySelector(".menu-toggle-btn");
    const sidebar = document.querySelector(".sidebar");
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });
    }
});
