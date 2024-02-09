from flask import Flask, render_template, request, redirect, url_for, render_template_string

app = Flask(__name__)

# Hardcoded username and password (for demonstration purposes)
correct_username = 'user'
correct_password = 'pass'

# HTML template embedded in the Python code
landing_page_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Landing Page</title>
</head>
<body>
    <h1>Landing Page</h1>
    <a href="{{ url_for('auth_page') }}">Go to Auth Page</a>
</body>
</html>
"""

# Auth page template
auth_page_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auth Page</title>
</head>
<body>
    <h1>Auth Page</h1>
    <form method="post" action="{{ url_for('login') }}#internal">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        <br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required>
        <br>
        <button type="submit">Login</button>
    </form>
</body>
</html>
"""

# Internal page template
internal_page_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Internal Page</title>
</head>
<body>
    <h1>Internal Page</h1>
    <p>Welcome to the internal page!</p>
</body>
</html>
"""

@app.route('/')
def landing_page():
    return render_template_string(landing_page_html)

@app.route('/auth#internal', methods=['POST'])
def login():
    entered_username = request.form.get('username')
    entered_password = request.form.get('password')

    # Check if entered credentials match the hardcoded values
    if entered_username == correct_username and entered_password == correct_password:
        # Redirect to the internal page with a hash in the login route
        return redirect(url_for('internal_page') + '#success')
    else:
        # Display an error message
        return "Invalid credentials. Please try again."

@app.route('/auth#internal', methods=['GET'])
def auth_page():
    return render_template_string(auth_page_html)

@app.route('/internal#success')
def internal_page():
    return render_template_string(internal_page_html)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
