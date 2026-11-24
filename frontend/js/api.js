// Centralized API Client
const API = {
    async request(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const headers = {
            "Content-Type": "application/json",
            ...(options.headers || {})
        };

        const token = localStorage.getItem("token");
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (!response.ok) {
                let errorMsg = `Error ${response.status}: ${response.statusText}`;
                try {
                    const errorJson = await response.json();
                    errorMsg = errorJson.detail || errorMsg;
                } catch (e) {}
                throw new Error(errorMsg);
            }

            // Return blob for csv exports
            if (options.isBlob) {
                return await response.blob();
            }

            return await response.json();
        } catch (error) {
            console.error(`API Call Failed [${endpoint}]:`, error);
            Utils.showToast(error.message, "danger");
            throw error;
        }
    },

    get(endpoint, params = {}) {
        const query = new URLSearchParams(params).toString();
        const url = query ? `${endpoint}?${query}` : endpoint;
        return this.request(url, { method: "GET" });
    },

    post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: "POST",
            body: JSON.stringify(data)
        });
    },

    put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: "PUT",
            body: JSON.stringify(data)
        });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: "DELETE" });
    },

    download(endpoint, params = {}) {
        const query = new URLSearchParams(params).toString();
        const url = query ? `${endpoint}?${query}` : endpoint;
        return this.request(url, { method: "GET", isBlob: true });
    }
};
