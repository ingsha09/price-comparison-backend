from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def scrape_amazon(product):
    url = f"https://www.amazon.in/s?k={product.replace(' ', '+')}"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    product_div = soup.find("div", {"data-component-type": "s-search-result"})
    if product_div:
        price_tag = product_div.find("span", {"class": "a-price-whole"})
        if price_tag:
            price = price_tag.get_text(strip=True).replace(",", "")
            link = "https://www.amazon.in" + product_div.h2.a["href"]
            return {"store": "Amazon", "price": price, "link": link}
    return {"store": "Amazon", "price": "N/A", "link": url}


def scrape_flipkart(product):
    url = f"https://www.flipkart.com/search?q={product.replace(' ', '+')}"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    price_tag = soup.find("div", {"class": "_30jeq3"})
    product_tag = soup.find("a", {"class": "_1fQZEK"})
    if price_tag and product_tag:
        price = price_tag.get_text(strip=True).replace("₹", "").replace(",", "")
        link = "https://www.flipkart.com" + product_tag["href"]
        return {"store": "Flipkart", "price": price, "link": link}
    return {"store": "Flipkart", "price": "N/A", "link": url}


def scrape_meesho(product):
    # Meesho uses dynamic JS — fallback to search page
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
