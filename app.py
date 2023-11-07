import os
import plotly
import requests
from flask import Flask, render_template, request, jsonify, send_file
from plotly.offline import plot
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
import requests


# Create a Flask application
app = Flask(__name__)

# Static JSON data (this would normally come from a data source or be dynamically generated)
data_json = {
    "zone": "CH",
    "forecast": [
        {
            "carbonIntensity": 95,
            "datetime": "2023-11-01T06:00:00.000Z"
        },
        {
            "carbonIntensity": 90,
            "datetime": "2023-11-01T07:00:00.000Z"
        },
        {
            "carbonIntensity": 107,
            "datetime": "2023-11-01T08:00:00.000Z"
        },
        {
            "carbonIntensity": 85,
            "datetime": "2023-11-01T09:00:00.000Z"
        },
        {
            "carbonIntensity": 98,
            "datetime": "2023-11-01T10:00:00.000Z"
        },
        {
            "carbonIntensity": 100,
            "datetime": "2023-11-01T11:00:00.000Z"
        },
        {
            "carbonIntensity": 105,
            "datetime": "2023-11-01T12:00:00.000Z"
        },
        {
            "carbonIntensity": 92,
            "datetime": "2023-11-01T13:00:00.000Z"
        },
        {
            "carbonIntensity": 88,
            "datetime": "2023-11-01T14:00:00.000Z"
        },
        {
            "carbonIntensity": 94,
            "datetime": "2023-11-01T15:00:00.000Z"
        },
        {
            "carbonIntensity": 96,
            "datetime": "2023-11-01T16:00:00.000Z"
        },
        {
            "carbonIntensity": 102,
            "datetime": "2023-11-01T17:00:00.000Z"
        },
        {
            "carbonIntensity": 97,
            "datetime": "2023-11-01T18:00:00.000Z"
        },
        {
            "carbonIntensity": 89,
            "datetime": "2023-11-01T19:00:00.000Z"
        },
        {
            "carbonIntensity": 91,
            "datetime": "2023-11-01T20:00:00.000Z"
        },
        {
            "carbonIntensity": 86,
            "datetime": "2023-11-01T21:00:00.000Z"
        },
        {
            "carbonIntensity": 93,
            "datetime": "2023-11-01T22:00:00.000Z"
        },
        {
            "carbonIntensity": 99,
            "datetime": "2023-11-01T23:00:00.000Z"
        },
        {
            "carbonIntensity": 101,
            "datetime": "2023-11-02T00:00:00.000Z"
        },
        {
            "carbonIntensity": 103,
            "datetime": "2023-11-02T01:00:00.000Z"
        }
    ],

    "optimisation": [
        {
            "rank": 1,
            "optimal_start_time": "2023-11-01T07:00:00.000Z",
            "co2_consumption": 90,
            "co2_saving_percentage_max": 30
        },
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

    # Extract start dates and ranks
    start_dates = [entry["optimal_start_time"] for entry in data_json["optimisation"]]
    ranks = [entry["rank"] for entry in data_json["optimisation"]]

    # Convert start dates to datetime objects
    start_dates = [date[:-1] for date in start_dates]  # Entferne das 'Z' am Ende
    start_dates = [datetime.fromisoformat(date) for date in start_dates]

    # Define the layout of the plot with shaded areas
    layout = go.Layout(
        title='CO2 Consumption Forecast',
        xaxis=dict(title='Date and Time'),
        yaxis=dict(title='Carbon Intensity (gCO2/kWh)'),
        shapes=[dict(
            type="rect",
            x0=start_date,
            x1=start_date + timedelta(hours=1),  # Hier anpassen, wie lange die Fläche geschraffiert sein soll
            y0=min(carbon_intensity),
            y1=max(carbon_intensity),
            fillcolor="rgba(255, 0, 0, 0.2)",  # Hier kannst du die Farbe anpassen (hier rot mit 20% Deckkraft)
            layer="below",
            line=dict(width=0)
        ) for start_date in start_dates])

    # Create the figure with the data, layout, and shaded areas
    fig = go.Figure(data=[trace_forecast], layout=layout)

    # Convert the figure to HTML div element
    plot_div = plot(fig, output_type='div', include_plotlyjs=True)

    plot_json = json.dumps(fig.data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('results.html', plot_html=plot_div, ranks=ranks, plot_json=plot_json)


@app.route('/submit', methods=['POST'])
def submit():
    # Get the JSON data from the request
    data = request.get_json()

    # Log data to the console for testing purposes
    print("Received data:", data)

    # Define the URL of the external API
    api_url = 'https://cr-electricity-maps-jfxxckhsja-oa.a.run.app'

    # Send the data to the external API
    response = requests.post(api_url, json=data)

    # Check if the request to the external API was successful
    if response.status_code == 200:
        # The external API returned a successful response
        result = response.json()
        print("API response:", result)
        # You can now return this result back to the client or process it further
        response = requests.get(request.url_root + 'results')
        return jsonify(result), 200, {response}
    else:
        # The external API returned an error
        print("Failed to call API, status code:", response.status_code)
        return jsonify(
            {'error': 'Failed to call external API', 'status_code': response.status_code}), response.status_code

if __name__ == '__main__':
    # Run the application on port 8080
    app.run(debug=True, port=8080)
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
