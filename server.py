from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# PayPal credentials (live)
PAYPAL_CLIENT_ID = "AT5efiux8yeLyxfgkHmV45IR9fUhpe1ePFeC0ZGEds7-BsGOY5b-QfTtMZMkZpJSHj2nXpmziGemhI9l"
PAYPAL_SECRET = "EL56Cc-oE98wOtjvQVJYpy7Mz1coywcYpKRw8k60oJ_8Rk1D0fTJQbLPFB5fgeYR3QTKdxmhKvDHFiPG"

# Crypto settings
USDT_RECEIVER = "TGSXXqT6xf2rhtDRKEmvW5ZQ6T5B8puiA1"
USDT_MIN_AMOUNT = 2.0

def get_paypal_token():
    url = "https://api-m.paypal.com/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data, auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET))
    return response.json().get("access_token")

def check_paypal_payment(user_email):
    token = get_paypal_token()
    if not token:
        return False
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api-m.paypal.com/v1/reporting/transactions?start_date=2024-01-01T00:00:00-0700&end_date=2030-01-01T00:00:00-0700&fields=all"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return False
    transactions = resp.json().get("transaction_details", [])
    for tx in transactions:
        payer_info = tx.get("payer_info", {})
        if user_email.lower() in payer_info.get("email_address", "").lower():
            amount = float(tx.get("transaction_info", {}).get("transaction_amount", {}).get("value", 0))
            if amount >= 2:
                return True
    return False

def check_trc20_payment(txid):
    url = f"https://apilist.tronscanapi.com/api/transaction-info?hash={txid}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return False
    data = resp.json()
    if "tokenInfo" not in data:
        return False
    if data.get("confirmed", False) != True:
        return False
    to_addr = data.get("toAddress", "")
    amount = float(data.get("tokenTransferInfo", {}).get("amount_str", "0")) / 1e6
    if to_addr == USDT_RECEIVER and amount >= USDT_MIN_AMOUNT:
        return True
    return False

@app.route("/verify-payment", methods=["POST"])
def verify():
    user_id = request.json.get("id", "").strip()
    if not user_id:
        return jsonify(success=False)

    if "@" in user_id:
        success = check_paypal_payment(user_id)
    else:
        success = check_trc20_payment(user_id)

    return jsonify(success=success)

if __name__ == "__main__":
    import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
