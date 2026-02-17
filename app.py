from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'super_secret_event_key'

# Mock Databases
USERS = {
    'admin1': {'password': 'pass', 'role': 'ADMIN'},
    'vendor1': {'password': 'pass', 'role': 'VENDOR', 'name': 'Test Vendor'},
    'user1': {'password': 'pass', 'role': 'USER'}
}
MEMBERSHIPS = []
PRODUCTS = [
    {'id': 1, 'name': 'Floral Arch', 'price': 500, 'vendor_id': 'vendor1'},
    {'id': 2, 'name': 'Lighting Setup', 'price': 1500, 'vendor_id': 'vendor1'}
]
CART = []
ORDERS = []

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        role = request.form.get('role').upper()

        user = USERS.get(user_id)
        if user and user['password'] == password and user['role'] == role:
            session['user_id'] = user_id
            session['role'] = user['role']
            
            if role == 'ADMIN': return redirect(url_for('admin_dashboard'))
            elif role == 'VENDOR': return redirect(url_for('vendor_dashboard'))
            elif role == 'USER': return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid Credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ================= ADMIN ROUTES =================
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'ADMIN': return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

@app.route('/admin/membership/add', methods=['GET', 'POST'])
def add_membership():
    if session.get('role') != 'ADMIN': return redirect(url_for('login'))
    # ... (Keep previous logic from earlier step) ...
    return render_template('admin_membership_add.html')

# ================= VENDOR ROUTES =================
@app.route('/vendor/dashboard')
def vendor_dashboard():
    if session.get('role') != 'VENDOR': return redirect(url_for('login'))
    return render_template('vendor_dashboard.html')

@app.route('/vendor/orders', methods=['GET', 'POST'])
def vendor_order_status():
    if session.get('role') != 'VENDOR': return redirect(url_for('login'))
    
    # Filter orders for this specific vendor
    my_orders = [o for o in ORDERS if o['vendor_id'] == session['user_id']]
    
    if request.method == 'POST':
        order_id = int(request.form.get('order_id'))
        new_status = request.form.get('status')
        for o in ORDERS:
            if o['id'] == order_id:
                o['status'] = new_status
        flash(f'Order {order_id} status updated to: {new_status}')
        return redirect(url_for('vendor_order_status'))
        
    return render_template('vendor_order_status.html', orders=my_orders)

# ================= USER ROUTES =================
@app.route('/user/dashboard')
def user_dashboard():
    if session.get('role') != 'USER': return redirect(url_for('login'))
    return render_template('user_dashboard.html', products=PRODUCTS)

@app.route('/user/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if session.get('role') != 'USER': return redirect(url_for('login'))
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if product:
        CART.append({'product': product, 'quantity': 1})
        flash(f"{product['name']} added to cart!")
    return redirect(url_for('user_dashboard'))

@app.route('/user/cart')
def view_cart():
    if session.get('role') != 'USER': return redirect(url_for('login'))
    grand_total = sum(item['product']['price'] * int(item['quantity']) for item in CART)
    return render_template('user_cart.html', cart=CART, grand_total=grand_total)

@app.route('/user/checkout', methods=['GET', 'POST'])
def checkout():
    if session.get('role') != 'USER': return redirect(url_for('login'))
    grand_total = sum(item['product']['price'] * int(item['quantity']) for item in CART)
    
    if request.method == 'POST':
        # Create order logic
        payment_method = request.form.get('payment_method')
        new_order = {
            'id': len(ORDERS) + 1,
            'user_id': session['user_id'],
            'vendor_id': CART[0]['product']['vendor_id'] if CART else '', # Simplification: assumes 1 vendor per order
            'total': grand_total,
            'payment': payment_method,
            'status': 'Received' # Default state
        }
        ORDERS.append(new_order)
        CART.clear() # Empty the cart after checkout
        return render_template('user_thank_you.html', total=grand_total)
        
    return render_template('user_checkout.html', grand_total=grand_total)

if __name__ == '__main__':
    app.run(debug=True)
