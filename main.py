import json
import requests
import re
import praw
import os
from tqdm import tqdm
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


def make_prompt(prompt: str) -> str:
    results = json.loads(
        requests.post(
            "http://localhost:5001/api/v1/generate", json={"prompt": prompt}
        ).content.decode()
    )["results"]
    assert len(results) == 1
    return results[0]["text"]


logging.basicConfig()
logging.root.setLevel(logging.NOTSET)
responses = []
reddit = praw.Reddit("bot")
file = open("responses.json", "w")
seen_dates = set()
for submission in reddit.subreddit("news").new(limit=None):
    try:
        if len(seen_dates) >= 200:
            break
        submission_date = datetime.datetime.fromtimestamp(
            submission.created_utc, datetime.UTC
        ).date()
        if submission_date in seen_dates:
            continue
        print(submission_date)
        prompt = f"""
    Read the title and URL of an article and rate their American political alignment from -50 to 50 where -50 is the most liberal, 50 is the most conservative, and 0 is neutral.
    Title: {submission.title}
    URL: {submission.url}
    """
        response = make_prompt(prompt)
        rating = int(next(re.finditer(r"(-?[0-9]+)", response)).group(1))
        if rating < -50 or rating > 50:
            continue
        responses.append(
            {
                "submission": convert2serialize(submission),
                "prompt": prompt,
                "response": response,
                "rating": rating,
            }
        )
        seen_dates.add(submission_date)
        json.dump(responses, file, indent=2)
        file.seek(0, os.SEEK_SET)
    except Exception as e:
        print("Encountered exception", e)

file.close()
