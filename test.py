import csv
import requests
import json
from time import sleep

prefix = 'FW'
seasonal_adjustments = [
    {"code": "U", "text": "Unadjusted"},
    {"code": "S", "text": "Seasonally Adjusted"}
    ]

categories = []
with open('categories.csv', 'rU') as infile:
    reader = csv.DictReader(infile, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        categories.append(row)
infile.closed

detail_code = "000000"
# TOO MANY OF THESE!!!
# with open('detail_codes.csv', 'rU') as infile:
#     reader = csv.DictReader(infile, delimiter='\t', quoting=csv.QUOTE_NONE)
#     for row in reader:
#         details.append(row)

data_type = "8"

case_types = []
with open('case_types.csv', 'rU') as infile:
    reader = csv.DictReader(infile, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        case_types.append(row)
infile.closed

areas = []
with open('areas.csv', 'rU') as infile:
    reader = csv.DictReader(infile, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        areas.append(row)
infile.closed

# 532,032 of these
all_series = []

for season in seasonal_adjustments:

    for category in categories:

        for case_type in case_types:

            for area in areas:

                series_id = prefix + season["code"] + category["code"] + detail_code + data_type + case_type["case_code"] + area["area_code"]

                ## Actually...don't think I want to be passing all this around. Rather, I'll parse the codes out of the series_id later.
                # series_id = {
                #     "series_id": prefix + season["code"] + category["code"] + detail_code + data_type + case_type["case_code"] + area["area_code"],
                #     "season_code": season["code"],
                #     "category_code": category["code"],
                #     "case_type_code": case_type["case_code"],
                #     "area_code": area["area_code"]
                # }

                all_series.append(series_id)
                
# 21,282 of these
series_groups = [all_series[x:x+25] for x in xrange(0, len(all_series), 25)]

headers = {'Content-type': 'application/json'}

for group in series_groups:

    # ids = []

    # for series in group:

    #     ids.append(series["series_id"])

    data = json.dumps({
        "seriesid": group,
        "startyear": "2011",
        "endyear": "2012"
    })

    response = requests.post('http://api.bls.gov/publicAPI/v1/timeseries/data/', data = data, headers = headers)
    json_data = json.loads(response.content)

    for series in json_data['Results']['series']:

        for item in series['data']:

            row = {
                "series_id": series["seriesID"],
                "year": item['year'],
                "period": item['period'],
                "value": item['value'],
                "has_footnotes": False
            }

            if len(item["footnotes"]) > 2:
                row["has_footnotes"] = True

            with open('data.csv', 'a') as outfile:
                writer = csv.DictWriter(outfile, ["series_id", "year", "period", "value", "has_footnotes"])
                writer.writerow(row)
            outfile.close()
        

    # check to see if there are any messages?

