from transformers.pipelines import pipeline
import json
import praw
import os
import datetime
import logging


def convert2serialize(obj):
    if isinstance(obj, dict):
        return {k: convert2serialize(v) for k, v in obj.items()}
    elif hasattr(obj, "_ast"):
        return convert2serialize(obj._ast())
    elif not isinstance(obj, str) and hasattr(obj, "__iter__"):
        return [convert2serialize(v) for v in obj]
    elif hasattr(obj, "__dict__"):
        return {
            k: convert2serialize(v)
            for k, v in obj.__dict__.items()
            if not callable(v) and not k.startswith("_")
        }
    else:
        return obj


logging.basicConfig()
logging.root.setLevel(logging.INFO)

pipe = pipeline(
    "text-classification",
    model="matous-volf/political-leaning-politics",
    tokenizer="launch/POLITICS",
)
responses = []
reddit = praw.Reddit("bot")
file = open("responses.json", "w")
for submission in reddit.subreddit("news").new(limit=None):
    submission_date = datetime.datetime.fromtimestamp(
        submission.created_utc, datetime.UTC
    ).date()
    rating = pipe(submission.title)[0]
    rating["label"] = {"LABEL_0": "left", "LABEL_1": "center", "LABEL_2": "right"}[
        rating["label"]
    ]
    responses.append(
        {
            "submission": convert2serialize(submission),
            "rating": rating,
        }
    )
    json.dump(responses, file, indent=2)
    file.seek(0, os.SEEK_SET)
file.close()
