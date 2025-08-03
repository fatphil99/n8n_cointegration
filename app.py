from flask import Flask, request, jsonify
from flask_cors import CORS
from statsmodels.tsa.stattools import coint
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/cointegration', methods=['POST'])
def cointegration():
    data = request.get_json(silent=True) or {}
    all_prices = data.get('all_prices')
    asset_names = data.get('symbols')

    if not isinstance(all_prices, list) or not isinstance(asset_names, list):
        return jsonify({"error": "Request must include lists 'all_prices' and 'symbols'"}), 400
    if not asset_names:
        return jsonify({"error": "'symbols' must not be empty"}), 400
    if len(all_prices) % len(asset_names) != 0:
        return jsonify({"error": f"Length of all_prices ({len(all_prices)}) is not a multiple of symbols ({len(asset_names)})"}), 400

    n = len(all_prices) // len(asset_names)
    try:
        price_series = [
            [float(x) for x in all_prices[i * n : (i + 1) * n]]
            for i in range(len(asset_names))
        ]
    except Exception as e:
        return jsonify({"error": f"Failed to convert price values to floats: {e}"}), 400

    results = []
    for i in range(len(asset_names)):
        for j in range(i + 1, len(asset_names)):
            score, pvalue, _ = coint(price_series[i], price_series[j])
            results.append({
                "asset1": asset_names[i],
                "asset2": asset_names[j],
                "pvalue": pvalue,
                "cointegrated": pvalue < 0.05
            })

    return jsonify(results), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f" * Starting Flask server on port {port} ...")
    app.run(host='0.0.0.0', port=port)
