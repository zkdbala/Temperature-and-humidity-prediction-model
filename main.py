import streamlit as st
import requests
import time
import threading
import pandas as pd
import altair as alt
from utils import prediction
from dotenv import load_dotenv
import os

n = 120
data = None
break_point = 85
interval = 0.05
load_dotenv()


streamlit_style = """
			<style>
			@import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap');

			html, body, [class*="css"]  {
			font-family: 'Roboto', sans-serif;
			}
			</style>
			"""
st.markdown(streamlit_style, unsafe_allow_html=True)


st.header('Temperature and Humidity Prediction')
st.text("\n")


def load_data(n):
    global data
    response = requests.get(
        f"https://api.thingspeak.com/channels/{os.getenv('CHANNEL')}/feeds.json?api_key={os.getenv('API_KEY')}&results={n}")
    feed = response.json()["feeds"]
    data = [[[float(x["field1"]), float(x["field2"])] for x in feed]]


thread = threading.Thread(target=load_data, args=(n,))
thread.start()

progress_bar = st.progress(0)
status_text = st.empty()
status_text.write("0% Complete")

for i in range(1, break_point+1):
    time.sleep(interval)
    progress_bar.progress(i)
    status_text.write(f"{i}% Complete")

thread.join()

for i in range(break_point+1, 101):
    time.sleep(interval)
    progress_bar.progress(i)
    status_text.write(f"{i}% Complete")


def data_from_sensor():
    st.subheader("Data from Sensor")
    dataframe = pd.DataFrame(data[0], columns=["Temperature", "Humidity"])
    st.table(dataframe)

    temperature = pd.DataFrame(
        {"Time-Step": [i for i in range(0, n)], "Temperature": [x[0] for x in data[0]]})

    temperature_chart = alt.Chart(temperature).mark_line().encode(
        x="Time-Step",
        y="Temperature"
    )

    temperature_chart = temperature_chart.properties(
        height=400,
        title='Temperature Data from Sensor'
    ).configure_axis(
        titleFontSize=18
    )

    # Render the chart using Streamlit
    st.altair_chart(temperature_chart, use_container_width=True)

    humidity = pd.DataFrame(
        {"Time-Step": [i for i in range(0, n)], "Humidity": [x[1] for x in data[0]]})

    humidity_chart = alt.Chart(humidity).mark_line().encode(
        x="Time-Step",
        y="Humidity"
    )

    humidity_chart = humidity_chart.properties(
        height=400,
        title='Humidity Data from Sensor'
    ).configure_axis(
        titleFontSize=18
    )

    # Render the chart using Streamlit
    st.altair_chart(humidity_chart, use_container_width=True)
    st.write("Visualisation of Combined Data")
    st.line_chart(dataframe)


def data_from_prediction(to_predict):
    # change n value here
    output = prediction(data, to_predict)
    st.subheader("Predicted Data")
    dataframe = pd.DataFrame(output, columns=["Temperature", "Humidity"])
    st.table(dataframe)

    temperature = pd.DataFrame(
        {"Time-Step": [i for i in range(n, n+to_predict)], "Temperature": [x[0] for x in output]})

    temperature_chart = alt.Chart(temperature).mark_line().encode(
        x="Time-Step",
        y="Temperature"
    )

    temperature_chart = temperature_chart.properties(
        height=400,
        title='Predicted Temperature Data'
    ).configure_axis(
        titleFontSize=18
    )

    # Render the chart using Streamlit
    st.altair_chart(temperature_chart, use_container_width=True)

    humidity = pd.DataFrame(
        {"Time-Step": [i for i in range(n, n+to_predict)], "Humidity": [x[1] for x in output]})

    humidity_chart = alt.Chart(humidity).mark_line().encode(
        x="Time-Step",
        y="Humidity"
    )

    humidity_chart = humidity_chart.properties(
        height=400,
        title='Predicted Humidity Data'
    ).configure_axis(
        titleFontSize=18
    )

    # Render the chart using Streamlit
    st.altair_chart(humidity_chart, use_container_width=True)
    st.text("Visualisation of Combined Data")
    st.line_chart(dataframe)


data_from_sensor()
st.success('Done!')

if len(data[0]) == 120:
    try:
        to_predict = int(st.text_input(
            label="How many values do you want to predict?", placeholder="5"))

        with st.spinner('Predicting Future Data...'):
            data_from_prediction(to_predict)
        st.success('Done!')
    except:
        st.error("Please enter a valid number to continue")
else:
    st.error("Not enough data to make any prediction")

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")
