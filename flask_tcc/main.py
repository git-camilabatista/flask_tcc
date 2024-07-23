from flask import Flask, request, jsonify

app = Flask(__name__)


users = {}
purchases = {}
payments = {}

@app.route('/users', methods=['POST'])
def register_user():
    user_id = len(users) + 1
    user_data = request.json
    users[user_id] = user_data
    return jsonify({"message": "User registered successfully", "user_id": user_id}), 201


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = users.get(user_id)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"message": "User not found"}), 404


@app.route('/purchases', methods=['POST'])
def register_purchase():
    user_id = request.json.get('user_id')
    if not user_id or user_id not in users:
        return jsonify({"message": "Invalid or missing user_id"}), 400

    purchase_id = len(purchases) + 1
    purchase_data = request.json
    purchases[purchase_id] = purchase_data
    return jsonify({"message": "Purchase registered successfully", "purchase_id": purchase_id}), 201


@app.route('/purchases/<int:purchase_id>', methods=['GET'])
def get_purchase(purchase_id):
    purchase = purchases.get(purchase_id)
    if purchase is not None:
        return jsonify(purchase), 200
    else:
        return jsonify({"message": "Purchase not found"}), 404


@app.route('/payments', methods=['POST'])
def register_payment():
    purchase_id = request.json.get('purchase_id')
    if not purchase_id or purchase_id not in purchases:
        return jsonify({"message": "Invalid or missing purchase_id"}), 400

    payment_id = len(payments) + 1
    payment_data = request.json
    payments[payment_id] = payment_data
    purchases[purchase_id]['paid'] = True  # Marca a compra como paga
    return jsonify({"message": "Payment registered successfully", "payment_id": payment_id}), 201


@app.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    payment = payments.get(payment_id)
    if payment is not None:
        return jsonify(payment), 200
    else:
        return jsonify({"message": "Payment not found"}), 404


@app.route('/paid_purchases', methods=['GET'])
def get_paid_purchases():
    paid_purchases_count = sum(1 for purchase in purchases.values() if purchase.get('paid'))
    return jsonify({"paid_purchases_count": paid_purchases_count}), 200


if __name__ == '__main__':
    app.run(debug=True)