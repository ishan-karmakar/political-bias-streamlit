import json
import datetime
import streamlit as st
import plotly.graph_objects as pgo
import pandas as pd
from collections import OrderedDict

with open("responses.json") as file:
    data = json.load(file)

dates = []
left = []
center = []
right = []
aggregations = OrderedDict()
for record in data:
    dt = datetime.datetime.fromtimestamp(
        record["submission"]["created_utc"], datetime.UTC
    ).date()
    if not len(dates) or dt != dates[-1]:
        dates.append(dt)
        left.append(0)
        right.append(0)
        center.append(0)
    match record["rating"]["label"]:
        case "left":
            left[-1] += 1
        case "right":
            right[-1] += 1
        case "center":
            center[-1] += 1

df = pd.json_normalize(data)
df["submission.created_utc"] = df["submission.created_utc"].apply(
    lambda d: datetime.datetime.fromtimestamp(d, datetime.UTC).date()
)

st.set_page_config(layout="wide")
st.title("Political Bias of Reddit r/news over Time")

st.write(
    """\
This project uses the PRAW API to get the latest submissions from the r/news subreddit.  
The titles of the submissions are fed into a [political bias model](https://huggingface.co/matous-volf/political-leaning-politics) and are categorized as left leaning, center, or right leaning.  
The data is then stored into a JSON file and is read by the Streamlit app to be graphed by Plotly.
"""
)

fig = pgo.Figure(
    data=[
        pgo.Bar(name="Left", x=dates, y=left, marker_color="#00aef3"),
        pgo.Bar(name="Center", x=dates, y=center, marker_color="white"),
        pgo.Bar(name="Right", x=dates, y=right, marker_color="#E81B23"),
    ]
)
fig.update_layout(barmode="stack")

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
