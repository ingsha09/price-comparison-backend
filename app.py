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

# Separate connect + read timeouts (connect=2s, read=3s)
TIMEOUT = (2, 3)


def get_amazon_price(product):
    url = f"https://www.amazon.in/s?k={product}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(res.text, "html.parser")

        price_tag = soup.select_one("span.a-price-whole") or soup.select_one(".a-price > .a-offscreen")
        if price_tag:
            price = price_tag.get_text(strip=True).replace("₹", "").replace(",", "")
        else:
            price = "N/A"

        return {"store": "Amazon", "price": price, "link": url}
    except Exception as e:
        return {"store": "Amazon", "price": "N/A", "link": url, "error": str(e)}


def get_flipkart_price(product):
    url = f"https://www.flipkart.com/search?q={product}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(res.text, "html.parser")

        price_tag = soup.select_one("div._30jeq3") or soup.select_one("._25b18c")
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
        res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(res.text, "html.parser")

        price_tag = soup.select_one("h5.sc-eDvSVe") or soup.find("span", string=lambda t: t and "₹" in t)
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

    functions = [get_amazon_price, get_flipkart_price, get_meesho_price]
    results = []

    # Limit workers to number of stores for less overhead
    with ThreadPoolExecutor(max_workers=len(functions)) as executor:
        future_to_func = {executor.submit(func, product): func.__name__ for func in functions}

        for future in as_completed(future_to_func):
            try:
                results.append(future.result())
            except Exception as e:
                results.append({"store": future_to_func[future], "price": "N/A", "error": str(e)})

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
