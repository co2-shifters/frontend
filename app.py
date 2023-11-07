from flask import Flask, render_template
from flask.helpers import send_file
import plotly.graph_objects as go

# Create a Flask application
app = Flask(__name__)

# Define a route and a view function
@app.route('/')
def indexPage():
    return send_file("templates/index.html")


def resultsPage():
    #plot results in a graph

    return render_template('results.html', plot_html=plot_html)

if __name__ == '__main__':
    # Run the application on port 5000
    app.run(debug=True)
