from flask import Flask, request, jsonify
import aiohttp
import asyncio
import re

app = Flask(__name__)

# Helper: Extract first number from HTML text
def extract_price(text):
    match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)', text.replace("\n", " "))
    return match.group(1).replace(",", "") if match else "N/A"

# Async fetch with timeout and error handling
async def fetch_price(session, url, store_name, price_selector=None):
    try:
        async with session.get(url, timeout=10) as response:
            html = await response.text()

            if price_selector and price_selector in html:
                price = extract_price(html)
            else:
                price = "N/A"

            return {"store": store_name, "price": price, "link": url}

    except Exception as e:
        return {"store": store_name, "price": "N/A", "link": url, "error": str(e)}

# Main scraping function
async def scrape_prices(product_name):
    product_encoded = product_name.replace(" ", "+")
    urls = [
        {
            "name": "Amazon",
            "url": f"https://www.amazon.in/s?k={product_encoded}",
            "selector": "a-price-whole"
        },
        {
            "name": "Flipkart",
            "url": f"https://www.flipkart.com/search?q={product_encoded}",
            "selector": "_30jeq3"  # Flipkart price class
        },
        {
            "name": "Meesho",
            "url": f"https://www.meesho.com/search?q={product_encoded}",
            "selector": "sc-eDvSVe"  # May need updating
        }
    ]

    async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
        tasks = [
            fetch_price(session, store["url"], store["name"], store["selector"])
            for store in urls
        ]
        return await asyncio.gather(*tasks)

@app.route("/")
def home():
    return "Price Comparison API is running!"

@app.route("/compare", methods=["GET"])
def compare():
    product = request.args.get("product")
    if not product:
        return jsonify({"error": "Please provide a 'product' query parameter"}), 400

    results = asyncio.run(scrape_prices(product))
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
