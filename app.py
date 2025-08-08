from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/127.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_amazon_price(product):
    url = f"https://www.amazon.in/s?k={product}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # Amazon price selector
        price_tag = soup.select_one("span.a-price-whole")
        if price_tag:
            price = price_tag.get_text(strip=True).replace(",", "")
        else:
            price = "N/A"

        return {"store": "Amazon", "price": price, "link": url}
    except Exception as e:
        return {"store": "Amazon", "price": "N/A", "link": url, "error": str(e)}

def get_flipkart_price(product):
    url = f"https://www.flipkart.com/search?q={product}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # Flipkart price selector
        price_tag = soup.select_one("div._30jeq3")
        if price_tag:
            price = price_tag.get_text(strip=True).replace("₹", "").replace(",", "")
        else:
            price = "N/A"

        return {"store": "Flipkart", "price": price, "link": url}
    except Exception as e:
        return {"store": "Flipkart", "price": "N/A", "link": url, "error": str(e)}

def get_meesho_price(product):
    url = f"https://www.meesho.com/search?q={product}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # Meesho price selector
        price_tag = soup.select_one("h5.sc-eDvSVe")
        if price_tag:
            price = price_tag.get_text(strip=True).replace("₹", "").replace(",", "")
        else:
            price = "N/A"

        return {"store": "Meesho", "price": price, "link": url}
    except Exception as e:
        return {"store": "Meesho", "price": "N/A", "link": url, "error": str(e)}

@app.route("/")
def home():
    return "Price Comparison API is running!"

@app.route("/compare")
def compare():
    product = request.args.get("product")
    if not product:
        return jsonify({"error": "Please provide a product name"}), 400

    results = [
        get_amazon_price(product),
        get_flipkart_price(product),
        get_meesho_price(product),
    ]
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
