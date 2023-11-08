import os
import plotly
import requests
from flask import Flask, render_template, request, jsonify, send_file, session
from plotly.offline import plot
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
import requests


# Create a Flask application
app = Flask(__name__)

app.config['SECRET_KEY'] = '*BJTLm3*$`-W"5kd'

# Static JSON data (this would normally come from a data source or be dynamically generated)
data_json = {}
co2_saving = {}


# Define a route for the index page
@app.route('/')
def indexPage():
    return send_file("templates/index.html")


@app.route('/results', methods=['GET'])
def resultsPage():
    # Get the data from the API
    duration = request.args.get('duration')

    if 'result' in session:
        data_json = session['result']
        

        # Extract data for plotting
        dates = [entry["datetime"] for entry in data_json["data"]]
        carbon_intensity = [entry["carbonIntensity"] for entry in data_json["data"]]

        # Convert duration to timedelta
        duration_timedelta = timedelta(minutes=int(duration))

        # Create a scatter plot for carbon intensity forecast
        trace_forecast = go.Scatter(
            x=dates,
            y=carbon_intensity,
            mode='lines+markers',
            name='Carbon Intensity Forecast'
        )

        # Extract start dates and ranks
        start_dates = [entry["opt_starttime"] for entry in data_json["opt"]]
        co2_saving = [entry["percentage_saved"] for entry in data_json["opt"]][0]
        

        # Convert start dates to datetime objects and add duration
        start_dates = [date[:-1] for date in start_dates]  # Entferne das 'Z' am Ende
        start_dates = [datetime.fromisoformat(date) + duration_timedelta for date in start_dates]

        # Define the layout of the plot with shaded areas
        layout = go.Layout(
            title='CO2 Consumption Forecast',
            xaxis=dict(title='Date and Time'),
            yaxis=dict(title='Carbon Intensity (gCO2/kWh)'),
            shapes=[dict(
                type="rect",
                x0=start_date,
                x1=start_date + duration_timedelta, # Hier anpassen, wie lange die Fläche geschraffiert sein soll
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
        return render_template('results.html', plot_html=plot_div, plot_json=plot_json, co2_saving=co2_saving)

    else:
        # If there's no result, handle the error (e.g., by redirecting the user, showing an error message, etc.)
        return "No result found in session", 404


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
        # Return this result back to the client
        session['result'] = result
        return jsonify(result), 200
    else:
        # The external API returned an error
        print("Failed to call API, status code:", response.status_code)
        return jsonify({'error': 'Failed to call external API', 'status_code': response.status_code}), response.status_code


if __name__ == '__main__':
    # Run the application on port 8080
    app.run(debug=True, port=8080)
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
