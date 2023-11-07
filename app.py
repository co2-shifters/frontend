import os

import plotly
from flask import Flask, render_template, request, jsonify, send_file
from plotly.offline import plot
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta

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


if __name__ == '__main__':
    # Run the application on port 8080
    app.run(debug=True, port=8080)
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

