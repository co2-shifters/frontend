from flask import Flask
from flask.helpers import send_file

# Create a Flask application
app = Flask(__name__)

# Define a route and a view function
@app.route('/')
def indexPage():
    return send_file("templates/index.html")

if __name__ == '__main__':
    # Run the application on port 5000
    app.run(debug=True)
