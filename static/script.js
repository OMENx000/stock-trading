// Function to fetch stock info and display it below the symbol input
function fetchStockInfo(symbolInputId, quantityInputId, infoDisplayId) {

    // When quantity input is clicked
    document.getElementById(quantityInputId).addEventListener("click", function () {

        // Get the symbol value
        let symbol = document.getElementById(symbolInputId).value.trim();

        // If no symbol entered, show message
        if (!symbol) {
            document.getElementById(infoDisplayId).textContent = "Please enter a symbol first.";
            return;
        }

        // Fetch stock data from our API
        fetch(`/lookup?symbol=${symbol}`)
            .then(response => response.json())
            .then(data => {
                // If data has name and price, display them
                if (data.name && data.price !== undefined) {
                    document.getElementById(infoDisplayId).innerHTML =
                        `<strong>${data.name}<br />$${data.price}</strong><br /><br />`;
                } else {
                    document.getElementById(infoDisplayId).textContent = "Sorry";
                }
            })
            .catch(err => {
                console.error("Error fetching stock data:", err);
                document.getElementById(infoDisplayId).textContent = "Sorry";
            });
    });
}


// Function to update all stock prices from table cells only if market is open
function updatePrices(priceCellPrefix, lookupUrl) {

    function fetchAndUpdate() {
        // Find all table cells with the given prefix in their ID
        document.querySelectorAll(`td[id^='${priceCellPrefix}']`).forEach(cell => {

            // Get symbol from ID (remove prefix part)
            let symbol = cell.id.replace(priceCellPrefix, "");

            // Fetch stock data
            fetch(`${lookupUrl}?symbol=${symbol}`)
                .then(response => response.json())
                .then(data => {
                    if (data.price !== undefined) {
                        cell.textContent = `$${data.price}`;
                    } else {
                        cell.textContent = "N/A";
                    }
                })
                .catch(err => {
                    console.error("Error fetching data:", err);
                    cell.textContent = "Error";
                });
        });
    }

    // Run once when page loads
    fetchAndUpdate();

    // Update every 10 seconds only if market is open
    if (marketOpen)
    {
        setInterval(fetchAndUpdate, 10000);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('show').addEventListener('click', function() {
        document.getElementById('form-overlay').style.display = 'flex';
        document.getElementById('hidden-input').focus();
    });

    document.getElementById('search-form-overlay').addEventListener('click', function(e) {
        if (e.target === this) {
            this.style.display = 'none';
        }
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === "Escape") {
            document.getElementById('search-form-overlay').style.display = 'none';
        }
    });
});