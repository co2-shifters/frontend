from flask import Flask, render_template, request, jsonify
from flask.helpers import send_file
import plotly.graph_objects as go
from plotly.offline import plot
from datetime import datetime

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
{
            "rank": 2,
            "optimal_start_time": "2023-11-01T09:00:00.000Z",
            "co2_consumption": 80,
            "co2_saving_percentage_max": 20
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

    # Extract start dates and ranks
    start_dates = [entry["optimal_start_time"] for entry in data_json["optimisation"]]
    ranks = [entry["rank"] for entry in data_json["optimisation"]]

    # Convert start dates to datetime objects
    start_dates = [date[:-1] for date in start_dates]  # Entferne das 'Z' am Ende
    start_dates = [datetime.fromisoformat(date) for date in start_dates]

    # Add vertical lines to the plot
    vertical_lines = [go.Scatter(x=[date, date], y=[min(carbon_intensity), max(carbon_intensity)],
                                 mode='lines', line=dict(color='red', width=2), name=f'Rank {rank} Start Date')
                      for date, rank in zip(start_dates, ranks)]

    # Define the layout of the plot
    layout = go.Layout(
        title='CO2 Consumption Forecast',
        xaxis=dict(title='Date and Time'),
        yaxis=dict(title='Carbon Intensity (gCO2/kWh)')
    )

    # Create the figure with the data, layout, and vertical lines
    fig = go.Figure(data=[trace_forecast] + vertical_lines, layout=layout)

    # Convert the figure to HTML div element
    plot_div = plot(fig, output_type='div', include_plotlyjs=True)

    # Render the results template with the plot div
    return render_template('results.html', plot_html=plot_div, ranks=ranks)


if __name__ == '__main__':
    # Run the application on port 5000
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
