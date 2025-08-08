from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

def scrape_amazon(product):
    try:
        url = f"https://www.amazon.in/s?k={product.replace(' ', '+')}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        product_div = soup.find("div", {"data-component-type": "s-search-result"})
        if not product_div:
            return {"store": "Amazon", "price": "N/A", "link": url}

        price_tag = product_div.find("span", {"class": "a-price-whole"})
        link_tag = product_div.find("a", {"class": "a-link-normal"}, href=True)

        price = price_tag.get_text(strip=True).replace(",", "") if price_tag else "N/A"
        link = "https://www.amazon.in" + link_tag["href"] if link_tag else url

        return {"store": "Amazon", "price": price, "link": link}
    except Exception as e:
        return {"store": "Amazon", "price": "N/A", "link": url, "error": str(e)}


def scrape_flipkart(product):
    try:
        url = f"https://www.flipkart.com/search?q={product.replace(' ', '+')}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        price_tag = soup.find("div", {"class": "_30jeq3"})
        product_tag = soup.find("a", {"class": "_1fQZEK"}) or soup.find("a", {"class": "s1Q9rs"})

        price = price_tag.get_text(strip=True).replace("₹", "").replace(",", "") if price_tag else "N/A"
        link = "https://www.flipkart.com" + product_tag["href"] if product_tag else url

        return {"store": "Flipkart", "price": price, "link": link}
    except Exception as e:
        return {"store": "Flipkart", "price": "N/A", "link": url, "error": str(e)}


def scrape_meesho(product):
    url = f"https://www.meesho.com/search?q={product.replace(' ', '+')}"
    return {"store": "Meesho", "price": "N/A", "link": url}


@app.route("/")
def home():
    return "Price Comparison API is running!"


@app.route("/compare")
def compare():
    product = request.args.get("product")
    if not product:
        return jsonify({"error": "Please provide a product name, e.g. /compare?product=iphone"}), 400

    results = [
        scrape_amazon(product),
        scrape_flipkart(product),
        scrape_meesho(product)
    ]
    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
