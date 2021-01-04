import requests
import json
import re
import csv
import sys
import os

def get_places(keyword, lat, lng):
    place_results = requests.get(
        "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
        params={
            "key": os.environ["GOOGLE_MAPS_API_KEY"],
            "keyword": keyword,
            "location": "{},{}".format(lat, lng),
            "radius": 5000,
        },
    ).json()

    return place_results["results"]


def get_place_details(place_id):
    place_details = requests.get(
        "https://maps.googleapis.com/maps/api/place/details/json",
        params={
            "key": os.environ["GOOGLE_MAPS_API_KEY"],
            "place_id": place_id,
            "fields": "url",
        },
    ).json()

    return place_details["result"]


def get_location_categories(cid):
    response = requests.get(
        "https://www.google.com/maps?cid={}&hl=en".format(cid),
        proxies={"http": os.environ["PROXY_URL"], "https": os.environ["PROXY_URL"]},
        timeout=10,
    )

    start = response.text.find("window.APP_INITIALIZATION_STATE=")
    end = response.text.find("window.APP_FLAGS", start)

    if start > 0 and end > 0:
        content = json.loads(
            response.text[start + len("window.APP_INITIALIZATION_STATE=") : end - 1]
        )
        content = json.loads(content[3][6][5:])
        return content[6][13]

    return []


def find_categories(keyword, lat, lng):
    writer = csv.writer(open("categories.csv", "w"), dialect="excel")
    writer.writerow(["URL", "Name", "Categories"])

    for place in get_places(keyword, lat, lng):
        details = get_place_details(place["place_id"])

        try:
            categories = get_location_categories(details["url"].split("=")[1])
        except:
            continue

        writer.writerow([details["url"], place["name"], ", ".join(categories)])


if __name__ == "__main__":
    find_categories(sys.argv[1], sys.argv[2], sys.argv[3])