import cpplcsu # longest common substring
import pylcs
print(help())

def lcsu_match(word):
    max_lcs = -1
    max_line = None

    with open("all_stocks.txt", "r", encoding="utf-8") as file:
        word = word.upper()
        for line in file:
            line = line.strip()
            if not line:
                continue  # skip empty lines

            parts = line.split("|")
            if len(parts) < 2:
                continue  # skip malformed lines

            company = parts[1].strip().upper()
            lcs_len = cpplcsu.longest_common_substring(word, company)

            if lcs_len > max_lcs:
                max_lcs = lcs_len
                max_line = line

    symbol = max_line.split("|")[0].strip()
    return symbol



companies = [
    "Apple Inc.",
    "Microsoft Corp.",
    "Alphabet Inc. (Google Class A)",
    "Alphabet Inc. (Google Class C)",
    "Amazon.com Inc.",
    "Tesla Inc.",
    "Nvidia Corp.",
    "Meta Platforms Inc. (Facebook)",
    "Berkshire Hathaway (Class A)",
    "Berkshire Hathaway (Class B)",
    "JPMorgan Chase & Co.",
    "Johnson & Johnson",
    "UnitedHealth Group",
    "Visa Inc.",
    "Mastercard Inc.",
    "Exxon Mobil Corp.",
    "Chevron Corp.",
    "The Coca-Cola Company",
    "PepsiCo Inc.",
    "Netflix Inc.",
    "Intel Corp.",
    "Advanced Micro Devices (AMD)",
    "IBM Corp.",
    "Walt Disney Co.",
    "McDonald's Corp.",
    "Walmart Inc.",
    "Home Depot Inc.",
    "Costco Wholesale",
    "Boeing Co.",
    "Salesforce Inc.",
    "PayPal Holdings",
    "Oracle Corp.",
    "Qualcomm Inc.",
    "Starbucks Corp.",
    "Uber Technologies",
    "Lyft Inc.",
    "Airbnb Inc."
]

for company in companies:
    print(lcsu_match(company))