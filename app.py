"""
Flask web application for decoding vehicle information.

This module depends on `decoder.py` for the business logic.  All
vehicle‑specific types and helper functions (such as the `Car` data
class and API interactions) live in that module.  The Flask layer
collects user input from an HTML form, invokes the decoder helpers
and returns JSON responses.
"""

from __future__ import annotations

from flask import Flask, render_template, request, jsonify

from decoder import (
    decode_vin,
    parse_vin_result,
    Car,
)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index() -> str:
    """Serve the home page with the decoding form."""
    return render_template("index.html")


@app.route("/decode", methods=["POST"])
def decode() -> tuple[str, int] | tuple[dict, int]:
    """Handle form submissions for VIN decoding.

    The endpoint returns a JSON response containing either a `car` key
    when decoding succeeds or an `error` key when input is invalid or
    a lookup fails.  The `car` value is a dictionary containing only
    defined fields (see `Car.to_dict`).
    """
    vin = request.form.get("vin", "").strip().upper()
    year = request.form.get("year", "").strip()
    if vin:
        try:
            raw = decode_vin(vin, year or None)
            car = parse_vin_result(vin, raw)
            return jsonify({"car": car.to_dict()}), 200
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500
    else:
        return jsonify({"error": "Please provide a VIN."}), 400


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)