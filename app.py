from flask import Flask, render_template, request, jsonify
from flask.helpers import send_file
import plotly.graph_objects as go
from plotly.offline import plot

# Create a Flask application
app = Flask(__name__)

# Static JSON data (this would normally come from a data source or be dynamically generated)
data_json = {
    "zone": "CH",
    "forecast": [
        {
            "carbonIntensity": 90,
            "datetime": "2023-11-01T07:00:00.000Z"
        },
        {
            "carbonIntensity": 107,
            "datetime": "2023-11-01T08:00:00.000Z"
        }
    ],
    "optimisation": [
        {
            "rank": 1,
            "optimal_start_time": "2023-11-01T09:00:00.000Z",
            "co2_consumption": 90,
            "co2_saving_percentage_max": 30
        }
    ]
}

# Define a route for the index page
@app.route('/')
def indexPage():
    return send_file("templates/index.html")


@app.route('/results', methods=['GET'])
def resultsPage():
    # Extract data for plotting
    dates = [entry["datetime"] for entry in data_json["forecast"]]
    carbon_intensity = [entry["carbonIntensity"] for entry in data_json["forecast"]]

    # Create a scatter plot for carbon intensity forecast
    trace_forecast = go.Scatter(
        x=dates,
        y=carbon_intensity,
        mode='lines+markers',
        name='Carbon Intensity Forecast'
    )

    # If you want to include optimisation data as well, do the same extraction for it
    # ...

    # Define the layout of the plot
    layout = go.Layout(
        title='CO2 Consumption Forecast',
        xaxis=dict(title='Date and Time'),
        yaxis=dict(title='Carbon Intensity (gCO2/kWh)')
    )

    # Create the figure with the data and layout
    fig = go.Figure(data=[trace_forecast], layout=layout)

    # Convert the figure to HTML div element
    plot_div = plot(fig, output_type='div', include_plotlyjs=True)

    # Render the results template with the plot div
    return render_template('results.html', plot_html=plot_div)


if __name__ == '__main__':
    # Run the application on port 5000
    app.run(debug=True)