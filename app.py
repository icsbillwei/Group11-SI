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

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
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
    if 'email' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
