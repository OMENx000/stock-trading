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
                    document.getElementById(infoDisplayId).textContent = "Sorry, stock not found.";
                }
            })
            .catch(err => {
                console.error("Error fetching stock data:", err);
                document.getElementById(infoDisplayId).textContent = "Error fetching data.";
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
    if (typeof marketOpen !== "undefined" && marketOpen) {
        setInterval(fetchAndUpdate, 10000);
    }
}

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Show overlay
    let showBtn = document.getElementById('show');
    if (showBtn) {
        showBtn.addEventListener('click', function() {
            document.getElementById('form-overlay').style.display = 'flex';
            document.getElementById('hidden-input').focus();
        });
    }

    // Hide overlay on click outside
    let overlay = document.getElementById('search-form-overlay');
    if (overlay) {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    }

    // Hide overlay on ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === "Escape") {
            let overlayEl = document.getElementById('search-form-overlay');
            if (overlayEl) overlayEl.style.display = 'none';
        }
    });

    // Toggle login/register forms
    const container = document.getElementById("container");
    const registerBtn = document.getElementById("register");
    const loginBtn = document.getElementById("login");

    if (registerBtn && container) {
        registerBtn.addEventListener("click", () => {
            container.classList.add("active");
        });
    }
    if (loginBtn && container) {
        loginBtn.addEventListener("click", () => {
            container.classList.remove("active");
        });
    }

    let searchInput = document.getElementById('search-input');
    const resultBox = document.getElementById('result-box');

    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener('keyup', function () {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(function () {
                let query = searchInput.value.trim().toLowerCase();

                if (query.length > 0) {
                    const xhr = new XMLHttpRequest();
                    xhr.open('GET', `/search?q=${encodeURIComponent(query)}`, true);
                    xhr.onreadystatechange = function () {
                        if (xhr.readyState === 4 && xhr.status === 200) {
                            const data = JSON.parse(xhr.responseText);
                            console.log(data);
                            

                            // filter results based on input
                            const filtered = data.filter(stock =>
                                stock.company.toLowerCase().includes(query) ||
                                stock.symbol.toLowerCase().includes(query)
                            );

                            resultBox.innerHTML = '';

                            filtered.forEach(stock => {
                                const link = document.createElement('a');
                                link.href = `/company/stock?symbol=${stock.symbol}`;
                                link.textContent = `${stock.company} (${stock.symbol})`;
                                link.className = 'result-item';
                                console.log(link);
                                
                                resultBox.appendChild(link);
                            });

                            resultBox.style.display = filtered.length ? 'block' : 'none';
                        }
                    };
                    xhr.send();
                } else {
                    resultBox.style.display = 'none';
                    resultBox.innerHTML = '';
                }
            }, 500);
        });
    }

});