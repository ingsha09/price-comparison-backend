from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import random

app = Flask(__name__)

HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Accept-Language": "en-US,en;q=0.9"
    }
]

def get_soup(url, timeout=8):
    """Fetch page and return BeautifulSoup object"""
    try:
        headers = random.choice(HEADERS_LIST)
        res = requests.get(url, headers=headers, timeout=timeout)
        res.raise_for_status()
        return BeautifulSoup(res.text, "html.parser")
    except Exception as e:
        return None

def get_amazon_price(product):
    url = f"https://www.amazon.in/s?k={product}"
    soup = get_soup(url, timeout=6)
    if not soup:
        return {"store": "Amazon", "price": "N/A", "link": url}

    price_tag = soup.select_one("span.a-price-whole")
    if price_tag:
        price = price_tag.get_text(strip=True).replace(",", "")
    else:
        price = "N/A"

    return {"store": "Amazon", "price": price, "link": url}

def get_flipkart_price(product):
    url = f"https://www.flipkart.com/search?q={product}"
    soup = get_soup(url, timeout=10)
    if not soup:
        return {"store": "Flipkart", "price": "N/A", "link": url}

    price_tag = soup.select_one("div._30jeq3") or soup.select_one("div._25b18c ._30jeq3")
    if price_tag:
        price = price_tag.get_text(strip=True).replace("₹", "").replace(",", "")
    else:
        price = "N/A"

    return {"store": "Flipkart", "price": price, "link": url}

def get_meesho_price(product):
    url = f"https://www.meesho.com/search?q={product}"
    soup = get_soup(url, timeout=8)
    if not soup:
        return {"store": "Meesho", "price": "N/A", "link": url}

    # Meesho price selectors (updated)
    price_tag = soup.select_one("h5.sc-eDvSVe") or soup.select_one("span.sc-eDvSVe")
    if not price_tag:
        price_tag = soup.find("span", string=lambda x: x and "₹" in x)

    if price_tag:
        price = price_tag.get_text(strip=True).replace("₹", "").replace(",", "")
    else:
        price = "N/A"

    return {"store": "Meesho", "price": price, "link": url}

@app.route("/")
def home():
    return "Price Comparison API is running!"

@app.route("/", methods=["GET"])
def price_comparison():
    product = request.args.get("product", "")
    if not product:
        return jsonify({"error": "No product specified"}), 400

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(
            lambda func: func(product),
            [get_amazon_price, get_flipkart_price, get_meesho_price]
        ))

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
