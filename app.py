from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/127.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

TIMEOUT = 4  # Faster timeout

# Session for reusing TCP connections
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10)
session.mount("http://", adapter)
session.mount("https://", adapter)


def get_amazon_price(product):
    url = f"https://www.amazon.in/s?k={product}"
    try:
        res = session.get(url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(res.text, "html.parser")
        price_tag = soup.select_one("span.a-price-whole")
        price = price_tag.get_text(strip=True).replace(",", "") if price_tag else "N/A"
        return {"store": "Amazon", "price": price, "link": url}
    except Exception as e:
        return {"store": "Amazon", "price": "N/A", "link": url, "error": str(e)}


def get_flipkart_price(product):
    url = f"https://www.flipkart.com/search?q={product}"
    try:
        res = session.get(url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(res.text, "html.parser")
        price_tag = soup.select_one("div._30jeq3")
        price = price_tag.get_text(strip=True).replace("₹", "").replace(",", "") if price_tag else "N/A"
        return {"store": "Flipkart", "price": price, "link": url}
    except Exception as e:
        return {"store": "Flipkart", "price": "N/A", "link": url, "error": str(e)}


def get_meesho_price(product):
    url = f"https://www.meesho.com/search?q={product}"
    try:
        res = session.get(url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(res.text, "html.parser")
        price_tag = soup.select_one("h5.sc-eDvSVe")
        price = price_tag.get_text(strip=True).replace("₹", "").replace(",", "") if price_tag else "N/A"
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

    functions = [get_amazon_price, get_flipkart_price, get_meesho_price]
    results = []

    # Run all scrapers in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(func, product) for func in functions]
        for future in as_completed(futures):
            results.append(future.result())

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
