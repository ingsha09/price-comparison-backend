from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Price Comparison API is running!"

@app.route("/compare")
def compare():
    product = request.args.get("product", "").strip()
    if not product:
        return jsonify({"error": "Please provide a product name using ?product=..."})
    
    # --- TODO: Replace this with actual scraping later ---
    # For now, returning fake data to test frontend integration
    data = [
        {"store": "Amazon", "price": "74999", "link": f"https://amazon.in/s?k={product}"},
        {"store": "Flipkart", "price": "73999", "link": f"https://flipkart.com/search?q={product}"},
        {"store": "Meesho", "price": "72999", "link": f"https://meesho.com/search?q={product}"}
    ]
    
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
