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
    # Erstelle den Plot
    fig = go.Figure(data=go.Scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 13], mode='markers'))

    # Rendere den Plot als HTML
    plot_html = fig.to_html(full_html=False, default_height=500, default_width=700)

    return render_template('results.html', plot_html=plot_html)

if __name__ == '__main__':
    # Run the application on port 5000
    app.run(debug=True)
