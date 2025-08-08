from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/127.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# Timeout per request (in seconds)
REQUEST_TIMEOUT = 3
# Timeout for all price fetches combined (in seconds)
GLOBAL_TIMEOUT = 4


def get_amazon_price(product):
    url = f"https://www.amazon.in/s?k={product}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(res.text, "html.parser")
        price_tag = soup.select_one("span.a-price-whole")
        price = price_tag.get_text(strip=True).replace(",", "") if price_tag else "N/A"
        return {"store": "Amazon", "price": price, "link": url}
    except Exception as e:
        return {"store": "Amazon", "price": "N/A", "link": url, "error": str(e)}


def get_flipkart_price(product):
    url = f"https://www.flipkart.com/search?q={product}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(res.text, "html.parser")
        price_tag = soup.select_one("div._30jeq3")
        price = price_tag.get_text(strip=True).replace("₹", "").replace(",", "") if price_tag else "N/A"
        return {"store": "Flipkart", "price": price, "link": url}
    except Exception as e:
        return {"store": "Flipkart", "price": "N/A", "link": url, "error": str(e)}


def get_meesho_price(product):
    url = f"https://www.meesho.com/search?q={product}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
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

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_store = {executor.submit(func, product): func.__name__ for func in functions}

        for future in as_completed(future_to_store, timeout=GLOBAL_TIMEOUT):
            try:
                results.append(future.result(timeout=REQUEST_TIMEOUT))
            except TimeoutError:
                store_name = future_to_store[future].replace("get_", "").replace("_price", "").capitalize()
                results.append({"store": store_name, "price": "N/A", "error": "Timeout"})
            except Exception as e:
                store_name = future_to_store[future].replace("get_", "").replace("_price", "").capitalize()
                results.append({"store": store_name, "price": "N/A", "error": str(e)})

    # Ensure all stores are included, even if they timed out before starting
    existing_stores = {item["store"] for item in results}
    for store_func in functions:
        store_name = store_func.__name__.replace("get_", "").replace("_price", "").capitalize()
        if store_name not in existing_stores:
            results.append({"store": store_name, "price": "N/A", "error": "Skipped due to global timeout"})

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
