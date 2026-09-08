async function loadFarmHistory() {

    const token =
        await getKrishiSaathiToken();

    if (!token) return;

    const response =
        await fetch("/api/farm-records", {

            headers: {
                "Authorization":
                    `Bearer ${token}`
            }

        });

    const result =
        await response.json();

    const container =
        document.getElementById(
            "farmHistory"
        );

    if (!response.ok) {

        container.innerHTML =
            "<p>Unable to load farm history.</p>";

        return;
    }

    if (!result.records ||
        result.records.length === 0) {

        container.innerHTML = `
            <div class="empty-history">
                <h3>🌱 No farm records yet</h3>
                <p>
                    Generate your first Farm Plan
                    to see it here.
                </p>
            </div>
        `;

        return;
    }

    container.innerHTML =
        result.records.map(record => {

            const crop =
                record.crop || "Crop not selected";

            const location =
                record.location || "Location not provided";

            const date =
                new Date(
                    record.created_at
                ).toLocaleDateString();

            return `

                <div class="history-card">

                    <div class="history-header">

                        <h3>
                            🌾 ${crop}
                        </h3>

                        <span>
                            ${date}
                        </span>

                    </div>

                    <p>
                        📍 ${location}
                    </p>

                    <p>
                        📦 Quantity:
                        ${record.quantity || "Not specified"}
                    </p>

                    <button
                        onclick='viewFarmRecord(${JSON.stringify(record)})'
                    >
                        View Plan
                    </button>

                </div>

            `;

        }).join("");

}


function viewFarmRecord(record) {

    alert(
        "Crop: " + record.crop +
        "\nLocation: " + record.location +
        "\nCreated: " +
        new Date(
            record.created_at
        ).toLocaleString()
    );

}
