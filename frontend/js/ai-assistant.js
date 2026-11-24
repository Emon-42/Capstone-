// AI Assistant JS
async function askQuestion(prefillQuery = null) {
    const input = document.getElementById("ai-query-input");
    const query = prefillQuery || input.value.trim();
    if (!query) return;

    if (!prefillQuery) input.value = "";

    appendChatMessage(query, "user");
    showThinkingIndicator();

    try {
        const res = await API.post("/ai/assistant", { query: query });
        removeThinkingIndicator();
        appendChatMessage(res.answer, "assistant", res.insights, res.suggested_actions);
    } catch (e) {
        removeThinkingIndicator();
        appendChatMessage("Sorry, I could not process your query right now. Please check backend connection.", "assistant");
    }
}

function appendChatMessage(text, sender, insights = [], actions = []) {
    const chatContainer = document.getElementById("chat-messages");
    if (!chatContainer) return;

    const msgDiv = document.createElement("div");
    msgDiv.style.marginBottom = "18px";
    msgDiv.style.display = "flex";
    msgDiv.style.flexDirection = "column";
    msgDiv.style.alignItems = sender === "user" ? "flex-end" : "flex-start";

    let innerContent = `
        <div style="max-width: 80%; padding: 14px 18px; border-radius: 14px; font-size: 13.5px; line-height: 1.5; ${
            sender === "user" 
                ? "background: var(--primary); color: #fff; border-bottom-right-radius: 4px;" 
                : "background: #fff; color: var(--text-primary); border: 1px solid var(--border); box-shadow: var(--shadow-sm); border-bottom-left-radius: 4px;"
        }">
            <div>${text}</div>
    `;

    if (insights && insights.length > 0) {
        innerContent += `
            <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid var(--border-light); font-size: 12px; color: var(--gold);">
                <strong>💡 Note / Insight:</strong> ${insights.join(" • ")}
            </div>
        `;
    }

    if (actions && actions.length > 0) {
        innerContent += `
            <div style="margin-top: 8px; font-size: 12px;">
                <strong>Recommended Next Steps:</strong>
                <ul style="padding-left: 18px; margin-top: 4px;">
                    ${actions.map(a => `<li>${a}</li>`).join("")}
                </ul>
            </div>
        `;
    }

    innerContent += `</div>`;
    msgDiv.innerHTML = innerContent;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showThinkingIndicator() {
    const chatContainer = document.getElementById("chat-messages");
    const indicator = document.createElement("div");
    indicator.id = "thinking-indicator";
    indicator.style.padding = "10px 16px";
    indicator.style.fontSize = "12.5px";
    indicator.style.color = "var(--text-muted)";
    indicator.innerHTML = `<em>Assistant is analyzing ledger database...</em>`;
    chatContainer.appendChild(indicator);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeThinkingIndicator() {
    document.getElementById("thinking-indicator")?.remove();
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("ai-query-form")?.addEventListener("submit", (e) => {
        e.preventDefault();
        askQuestion();
    });
});
