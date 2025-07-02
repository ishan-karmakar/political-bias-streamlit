import json
import datetime
import streamlit as st
import plotly.graph_objects as pgo
from plotly import subplots
import pandas as pd

with open("responses.json") as file:
    data = json.load(file)

df = pd.json_normalize(data)
df["submission.created_utc"] = df["submission.created_utc"].apply(
    lambda d: datetime.datetime.fromtimestamp(d, datetime.UTC).date()
)

st.set_page_config(layout="wide")
st.title("Political Bias of Reddit r/news over Time")

fig = subplots.make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    pgo.Scatter(
        x=df["submission.created_utc"],
        y=df["rating.label"],
        name="Ratings",
        mode="markers",
    ),
    secondary_y=False,
)
fig.update_xaxes(title_text="Time")

points = st.plotly_chart(fig, on_select="rerun")["selection"]["points"]
points = [datetime.date.fromisoformat(p["x"]) for p in points]

if len(points):
    df = df.loc[df["submission.created_utc"].isin(points)]

st.dataframe(
    df[["submission.title", "rating.label", "rating.score"]],
    hide_index=True,
    column_config={
        "submission.title": "Title",
        "rating.label": "Predicted Alignment",
        "rating.score": "Alignment Confidence",
    },
)
