from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session management

# Temporary storage for users (will be replaced with proper database later)
users = {}

# Temporary storage for users (will be replaced with proper database later)
users = {}

# Login at /, signup at /signup, forgot password at /forgot_password, reset password at /reset_password/<email>, logout at /logout, index at /index
# Three specifications implemented: login, signup, forgot password (First 3 specifications from A1)

# Please install dependencies first from requirements.txt
# Then it should run with python app.py

# For simplicity and ease of get it running the secret key is hardcoded here but in production it would be accessed via env variable
app.secret_key = 'secret'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        # Get email and password from form
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if email and password are provided
        if not email or not password:
            flash('Please provide both email and password', 'error')
            return render_template('login.html')
        
        # Redirect to index if email and password are correct
        if email in users and check_password_hash(users[email]['password'], password):
            session['email'] = email
            return redirect(url_for('index'))
        
        # Show error message if email or password is incorrect
        flash('Invalid email or password', 'error')
        return render_template('login.html')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            # Show error message if email or password is not provided
            flash('Please provide both email and password', 'error')
            return render_template('signup.html')
            
        if email in users:
            # Show error message if email already exists
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

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    # Handle forgot password form submission, initially ask for email
    if request.method == 'POST':
        email = request.form.get('email')

        if email not in users:
            flash('Email not found', 'error')
            return render_template('forgot_password.html')

        # Redirect to reset password page if email exists
        return redirect(url_for('reset_password', email=email))

    return render_template('forgot_password.html')

@app.route('/reset_password/<email>', methods=['GET', 'POST'])
def reset_password(email):
    # Handle reset password form submission, follows forgot password
    if request.method == 'POST':
        password = request.form.get('password')

        if not password:
            flash('Please enter a new password', 'error')
            return render_template('reset_password.html', email=email)

        if email not in users:
            flash('Invalid reset request', 'error')
            return redirect(url_for('login'))

        # Update the password
        users[email]['password'] = generate_password_hash(password)
        flash('Password has been reset successfully', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', email=email)

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/index')
def index():
    # Placeholder main application page
    if 'email' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
