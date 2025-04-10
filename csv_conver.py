import csv
import json

with open("reviews/links.json", "r", encoding="utf-8") as f:
    data = json.load(f)
# Simpan ke CSV
with open("reviews.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["nama_destinasi", "name", "komentar", "rating", "tanggal"])
    
    for item in data:
        review = item["review"]
        writer.writerow([
            item["nama_destinasi"],
            review["name"],
            review["komentar"],
            review["rating"].replace("\n", " "),
            review["tanggal"]
        ])