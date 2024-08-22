from flask import Flask, request, jsonify, abort
from pydantic import BaseModel, ValidationError
from typing import Dict

app = Flask(__name__)


class UserBase(BaseModel):
    email: str


class User(UserBase):
    password: str


class UserResponse(UserBase):
    user_id: int
    message: str


class PurchaseBase(BaseModel):
    user_id: int
    item_name: str
    price: float


class Purchase(PurchaseBase):
    paid: bool = False


class PurchaseResponse(Purchase):
    purchase_id: int
    message: str


class Payment(BaseModel):
    user_id: int
    purchase_id: int


class PaymentResponse(Payment):
    payment_id: int
    message: str


# "Database"
users: Dict[int, User] = {}
purchases: Dict[int, Purchase] = {}
payments: Dict[int, Payment] = {}


def get_valid_user(user_id):
    user = users.get(user_id)
    if user:
        return user
    abort(404, description='User not found')


# Error handling for Pydantic validation errors
@app.errorhandler(ValidationError)
def handle_validation_error(error):
    response = jsonify(error.errors())
    response.status_code = 400
    return response


@app.errorhandler(404)
def handle_not_found_error(error):
    response = jsonify({'detail': str(error.description)})
    response.status_code = 404
    return response


# Users
@app.route('/users', methods=['POST'])
def register_user():
    user_data = request.json
    try:
        user = User(**user_data)
    except ValidationError as e:
        return handle_validation_error(e)

    if any(
        existing_user['email'] == user.email for existing_user in users.values()
    ):
        abort(400, description='User already registered')

    user_id = len(users) + 1
    users[user_id] = user.dict()
    user_response = UserResponse(
        user_id=user_id,
        email=user.email,
        message='User registered successfully',
    )
    return jsonify(user_response.dict())


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify(get_valid_user(user_id))


# Purchases
@app.route('/purchases', methods=['POST'])
def register_purchase():
    purchase_data = request.json
    try:
        purchase = Purchase(**purchase_data)
    except ValidationError as e:
        return handle_validation_error(e)

    if purchase.user_id not in users:
        abort(400, description='Invalid or missing user_id')

    purchase_id = len(purchases) + 1
    purchases[purchase_id] = Purchase.model_validate(purchase.model_dump())
    purchase_response = PurchaseResponse(
        purchase_id=purchase_id,
        message='Purchase registered successfully',
        user_id=purchase.user_id,
        item_name=purchase.item_name,
        price=purchase.price,
        paid=purchase.paid,
    )
    return jsonify(purchase_response.dict())


@app.route('/purchases/<int:purchase_id>', methods=['GET'])
def get_purchase(purchase_id):
    x_user_id = request.headers.get('x_user_id', type=int)
    if x_user_id is None:
        abort(400, description='Missing x_user_id header')

    _ = get_valid_user(x_user_id)
    purchase = purchases.get(purchase_id)
    if purchase and purchase.user_id == x_user_id:
        return jsonify(purchase.dict())

    abort(404, description='Purchase not found')


@app.route('/purchases', methods=['GET'])
def get_all_purchases():
    x_user_id = request.headers.get('x_user_id', type=int)
    if x_user_id is None:
        abort(400, description='Missing x_user_id header')

    _ = get_valid_user(x_user_id)
    user_purchases = {
        pid: p.dict() for pid, p in purchases.items() if p.user_id == x_user_id
    }
    if user_purchases:
        return jsonify(user_purchases)

    abort(404, description='No purchases found')


# Payments
@app.route('/payments', methods=['POST'])
def register_payment():
    payment_data = request.json
    try:
        payment = Payment(**payment_data)
    except ValidationError as e:
        return handle_validation_error(e)

    if payment.purchase_id not in purchases:
        abort(400, description='Invalid or missing purchase_id')

    if any(p['purchase_id'] == payment.purchase_id for p in payments.values()):
        abort(400, description='Payment already registered for this purchase')

    payment_id = len(payments) + 1
    payments[payment_id] = payment.dict()
    purchases[payment.purchase_id].paid = True
    payment_response = PaymentResponse(
        payment_id=payment_id,
        user_id=payment.user_id,
        purchase_id=payment.purchase_id,
        message='Payment registered successfully',
    )
    return jsonify(payment_response.dict())


@app.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    x_user_id = request.headers.get('x_user_id', type=int)
    if x_user_id is None:
        abort(400, description='Missing x_user_id header')

    _ = get_valid_user(x_user_id)
    payment = payments.get(payment_id)
    if payment and payment.get('user_id') == x_user_id:
        return jsonify(payment)

    abort(404, description='Payment not found')


@app.route('/payments', methods=['GET'])
def get_all_payments():
    x_user_id = request.headers.get('x_user_id', type=int)
    if x_user_id is None:
        abort(400, description='Missing x_user_id header')

    _ = get_valid_user(x_user_id)
    user_payments = {
        pid: p for pid, p in payments.items() if p.get('user_id') == x_user_id
    }
    if user_payments:
        return jsonify(user_payments)

    abort(404, description='No payments found')


# Admin
@app.route('/admin/users', methods=['GET'])
def get_all_users():
    return jsonify(users)


@app.route('/admin/paid_purchases', methods=['GET'])
def get_paid_purchases():
    paid_purchases_count = sum(
        1 for purchase in purchases.values() if purchase.paid
    )
    paid_purchases_total = sum(
        purchase.price for purchase in purchases.values() if purchase.paid
    )
    
    return jsonify({
        'paid_purchases_count': paid_purchases_count,
        'paid_purchases_total': paid_purchases_total,
    })


@app.route('/admin/total_purchases', methods=['GET'])
def get_total_purchases():
    total_purchases_count = len(purchases)
    return jsonify({'total_purchases_count': total_purchases_count})


if __name__ == '__main__':
    app.run(debug=True, port=8002)
