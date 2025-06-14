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
st.title("Test Title")

fig = subplots.make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    pgo.Scatter(x=df["submission.created_utc"], y=df["rating"], name="Ratings"),
    secondary_y=False,
)
fig.add_trace(
    pgo.Scatter(
        x=df["submission.created_utc"], y=df["submission.score"], name="Upvotes"
    ),
    secondary_y=True,
)
fig.update_layout(title_text="Ratings and Upvotes of Reddit Posts over Time")
fig.update_xaxes(title_text="Time")
fig.update_yaxes(range=(-50, 50), secondary_y=False)

points = st.plotly_chart(fig, on_select="rerun")["selection"]["points"]
points = [datetime.date.fromisoformat(p["x"]) for p in points]

if len(points):
    df = df.loc[df["submission.created_utc"].isin(points)]

st.dataframe(
    df[["rating", "submission.title", "response"]],
    hide_index=True,
    column_config={
        "rating": "Rating",
        "submission.title": "Title",
        "response": "LLM Response",
    },
)
