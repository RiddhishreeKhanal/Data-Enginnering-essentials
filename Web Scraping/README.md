# Web Scraping Project – Ekantipur News

This project is a beginner-friendly web scraping script developed using Python and Playwright.  
The script extracts news-related data from **ekantipur.com** and stores the results in JSON format.

This project was created as a learning exercise to understand browser automation, page navigation, and data extraction from dynamic websites.

---

## 📌 Features
- Automates a browser using Playwright
- Scrapes news titles and related information
- Saves extracted data into a structured JSON file
- Handles dynamic content loading

---

## 🛠 Technologies Used
- Python
- Playwright
- JSON

---

## 📂 Project Structure
web-scraping
```bash
│── scraper.py
│── output.json
│── README.md
│── pyproject.toml
│── uv.lock
│── requirements.txt
```
## ▶️ How to Run the Project

1. Install Playwright:
```bash
pip install playwright
playwright install
```

2. Run the script:
```bash
python scraper.py
```

3. The scraped data will be saved in:
```bash
output.json
```
