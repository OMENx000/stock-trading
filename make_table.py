from cs50 import SQL
db = SQL("sqlite:///finance.db")

# open and process the file
with open("D:\\code\\finance\\all_stock.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines:
    line = line.split("|")
    symbol, company = line[0].strip(), line[1].removesuffix("\n")
    
    db.execute("INSERT INTO stocks(symbol, company) VALUES (?, ?)", symbol, company)

print("Done task")