from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session management

# Temporary storage for users (will be replaced with proper database later)
users = {}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password', 'error')
            return render_template('login.html')
            
        if email in users and check_password_hash(users[email]['password'], password):
            session['email'] = email
            return redirect(url_for('index'))
        
        flash('Invalid email or password', 'error')
        return render_template('login.html')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password', 'error')
            return render_template('signup.html')
            
        if email in users:
            flash('Email already exists', 'error')
            return render_template('signup.html')
            
        # Store hashed password
        hashed_password = generate_password_hash(password)
        users[email] = {
            'password': hashed_password
        }
        
        flash('Account created successfully', 'success')
        return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if 'email' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)