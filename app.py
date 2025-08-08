from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Price Comparison API is running!"

@app.route("/compare")
def compare():
    product = request.args.get("product", "")
    # Temporary fake data until scraping is ready
    data = [
        {"store": "Amazon", "price": "74999", "link": "https://amazon.in"},
        {"store": "Flipkart", "price": "73999", "link": "https://flipkart.com"},
        {"store": "Meesho", "price": "72999", "link": "https://meesho.com"}
    ]
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
