import asyncio
import aiohttp
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

# Fake browser headers to avoid getting blocked
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9"
}

# Asynchronous function to fetch price
async def fetch_price(session, url, selector, store):
    try:
        async with session.get(url, headers=HEADERS, timeout=5) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            price_element = soup.select_one(selector)
            price = price_element.get_text(strip=True) if price_element else "N/A"
            return {"store": store, "link": url, "price": price}
    except Exception as e:
        return {"store": store, "link": url, "price": "N/A", "error": str(e)}

# Main scraper function
async def scrape_all(product):
    async with aiohttp.ClientSession() as session:
        tasks = [
            # Amazon
            fetch_price(
                session,
                f"https://www.amazon.in/s?k={product}",
                "span.a-price-whole",
                "Amazon"
            ),
            # Flipkart
            fetch_price(
                session,
                f"https://www.flipkart.com/search?q={product}",
                "div._30jeq3",  # Flipkart price selector
                "Flipkart"
            ),
            # Meesho
            fetch_price(
                session,
                f"https://www.meesho.com/search?q={product}",
                "h5.sc-eDvSVe",  # Meesho price selector (may need update)
                "Meesho"
            )
        ]
        return await asyncio.gather(*tasks)

# API endpoint
@app.route("/compare")
def compare_prices():
    product = request.args.get("product", "").strip()
    if not product:
        return jsonify({"error": "No product specified"}), 400
    
    results = asyncio.run(scrape_all(product))
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
