"""********************************************
File: server-client.py
Author: Metflekx

Desc. :
    Write two python scripts that
    have to achieve the common goal
    to downloads a certain set of resources
    , merges them with CSV-transmitted
    resources, and converts them to a
    formatted excel file. In particular,
    the script should:
********************************************"""

import sys # For argv
import requests

import pandas as pd

def get_access_token() -> str:
    """Get access token for
    the API
    """

    url = "https://api.baubuddy.de/index.php/login"
    payload = {
        "username": "365",
        "password": "1"
    }
    headers = {
        "Authorization":
          "Basic QVBJX0V4cGxvcmVyOjEyMzQ1NmlzQUxhbWVQYXNz",
        "Content-Type":
          "application/json"
    }
    res = requests.request(
      "POST", url,
      json=payload,
      headers=headers)
    return res.json()['oauth']['access_token']

def server(csvpath):
    """ This script should offer
    a REST-API, that accepts a CSV,
    downloads a certain set of
    resources, merges them with the
    CSV, applies filtering, and
    returns them in an appropriate
    data-structure

    Takes path to a csv: reqpath, 
    makes a reqdf data frame that, 
    gets and reads resources into 
    apidf. merges into resdf, applies
    filtering and returns resdf in json.
    """

    # TODO:
    # [ ] make sure the result is distinct
    # [ ] REST-API (e.g. FastAPI, Flask, Django …)
            # offering a POST Call which accepts a
            # transmitted CSV containing vehicle information

    # Read the data sent over request
    reqdf = pd.read_csv(csvpath, delimiter=';')
    # Request the resources
    acctoken = get_access_token()


    res = (requests.get(
            "https://api.baubuddy.de"
            "/dev/index.php/v1/vehicles"
            "/select/active", 
            headers = {
                "Authorization":
                f"Bearer {acctoken}"}))
    apidf = pd.DataFrame(res.json())

    # Filter out any resources
    # that do not have a value
    # set for hu field
    apidf = apidf[apidf["hu"].notna()]

    # merge req and res data
    resdf = pd.merge(reqdf, apidf,
                     on="kurzname",
                     how="outer",
                     validate="one_to_many",
                     suffixes=('', '_res'))

    # Combine labelId and LabelId_res
    resdf['labelIds'] = resdf[
            'labelIds'].combine_first(
                    resdf['labelIds_res'])
    resdf = resdf.drop(
            columns=['labelIds_res'])
    print(resdf[["labelIds", "hu"]].head())
    print(resdf["labelIds"].unique())

    # For each labelId in the
    # vehicle's JSON array
    # labelIds resolve its colorCode
    for _, row in resdf.iterrows():
        # Skip NaN
        if pd.notna(row['labelIds']):
            res = requests.get(
                "https://api.baubuddy.de/"
                "dev/index.php/v1/labels/"
                f"{row['labelIds']}",
            headers = {
              "Authorization":
                f"Bearer {acctoken}"})

            # bad response
            if res.status_code != 200:
                continue

            # add a column colorCode
            # to resdf
            resdf["colorCode"] =\
            res.json()[0]["colorCode"]

    print(resdf["colorCode"].unique())

    sys.exit(0)

    # return data-structure in JSON format
    return resdf.to_json()


def client():
    """Transmits a CSV to
    a REST-API
    (s. Server-section below),
    handles the response and
    generates an Excel-File
    taking the input parameters
    into account.
    """

    # Call server and get the merged
    # data in json
    resdf = server("vehicles.csv")

    print(resdf.head())

    # Take an input parameter -k/--keys that can receive an arbitrary amount of string arguments

    # Take an input parameter -c/--colored that receives a boolean flag and defaults to True

    # Transmit CSV containing vehicle information to the POST Call of the server (example data: vehicles.csv)

    # Convert the servers response into an excel file that contains all resources and make sure that:

        # Rows are sorted by response field gruppe
        # Columns always contain rnr field
        # Only keys that match the input arguments are considered as additional columns (i.e. when the script is invoked with kurzname and info, print two extra columns)
        # If labelIds are given and at least one colorCode could be resolved, use the first colorCode to tint the cell's text (if labelIds is given in -k)
        # If the -c flag is True, color each row depending on the following logic:
            # If hu is not older than 3 months --> green (#007500)
            # If hu is not older than 12 months --> orange (#FFA500)
            # If hu is older than 12 months --> red (#b30000)
        # The file should be named vehicles_{current_date_iso_formatted}.xlsx

client()

    # # Rows are sorted by response field gruppe
    # mrgdf.sort_values(by="gruppe")
    # # Columns always contain rnr field
    # cols = ['rnr']
    # # Only keys that match the input arguments are considered as additional columns
    # for arg in sys.argv[1:]: # slice to skip .py file
    #     # Check for valid input:
    #     # O(N) lookup OK since
    #     # n is samll for columns
    #     if arg not in mrgdf.columns:
    #         print(f"no column matching the {arg}, will leave out")
    #         continue
    #     cols.append(arg)
    #
    # # If labelIds are given and at least one colorCode
    # # could be resolved, use the first colorCode to tint
    # # the cell's text (if labelIds is given in -k)
    #
    # # Out
    # mrgdf = mrgdf[[col for col in cols]]
    #
    # mrgdf = mrgdf[mrgdf["labelIds"].notna()]
    #
    # # TMP
    # print(mrgdf.head())

    # mrgdf.to_excel("out.xlsx")

    # with open('vehicles.csv', 'r') as f:
    #     reader = csv.DictReader(f, delimiter=';')
    #     jsondata = json.dumps(list(reader), ensure_ascii=False, indent=4)
    # print(jsondata)
