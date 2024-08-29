"""********************************************
File: server.py
Author: Metflekx

Desc. :

TODO:
    [*] Make It Work--------------------
    [*] Make a restAPI that takes csv
    [*] Make server work.
    [*] Merge branch restapi with master
    [*] Make client work.
    
    [ ] Improve-------------------------
    [ ] Fix File structure.
    [ ] Improve Error Handling.
    [ ] Write tests.
    [ ] Improve Lookups.
********************************************"""

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import requests
import pandas as pd


# Init
app = Flask(__name__)
api = Api(app)

class Vehicles(Resource):
    """
    This script should offer
    a REST-API, that accepts a CSV,
    downloads a certain set of
    resources, merges them with the
    CSV, applies filtering, and
    returns them in an appropriate
    data-structure.
    """

    def __init__(self):
        self.access_token = self.__get_access_token()

    def __get_access_token(self):
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

    def __fetch(self):
        """
        Takes path to a csv: csv_path
        makes a reqdf data frame that,
        gets and reads resources into
        apidf. merges into resdf, applies
        filtering and returns resdf in json.
        """
    
        # Request the resources
        res = (requests.get(
                "https://api.baubuddy.de"
                "/dev/index.php/v1/vehicles"
                "/select/active",
                headers = {
                    "Authorization":
                    f"Bearer {self.access_token}"}))
        apidf = pd.DataFrame(res.json())
    
        # Filter out any resources
        # that do not have a value
        # set for hu field
        apidf = apidf[apidf["hu"].notna()]
        return apidf
    
    def __accept(self, csv_content):
        """
        Takes in data from the clinet.
        Reads into a pandas dataframe
        and returns the df.
        """

        return pd.read_csv(csv_content, 
                           delimiter=';')

    def __process(self, df_api, df_req):
        """
        merges dataframes, apply filters
        and returns in JSON.
        """
    
        # merge req and res data
        df_res = pd.merge(df_req, df_api,
                         on="kurzname",
                         how="outer",
                         validate="one_to_many",
                         suffixes=("", "_res"))
    
        # Combine labelId and LabelId_res
        df_res['labelIds'] = df_res[
                'labelIds'].combine_first(
                        df_res['labelIds_res'])
        df_res = df_res.drop(
                columns=['labelIds_res'])
    
        # For each labelId in the
        # vehicle's JSON array
        # labelIds resolve its colorCode
        for i, row in df_res.iterrows():
            # Skip NaN
            if pd.notna(row["labelIds"]):
                res = requests.get(
                    "https://api.baubuddy.de/"
                    "dev/index.php/v1/labels/"
                    f"{row['labelIds']}",
                headers = {
                  "Authorization":
                    f"Bearer {self.access_token}"})
    
                # bad response
                if res.status_code != 200:
                    continue
    
                # set colorCode
                df_res.at[i, "labelIds"]=\
                res.json()[0]["colorCode"]
    
        # return data-structure in JSON format
        return df_res.to_json()
    
    def post(self):
        """ CREATE A BOOK
            Takes a form and creates
            a book in the database.
        """

        file = request.files["file"]

        # fetch
        df_api = self.__fetch()

        # accept
        df_req = self.__accept(
                file.filename)

        # merge and filter
        df_res = self.__process(df_api, df_req)

        return df_res


api.add_resource(Vehicles, '/vehicles')

if __name__ == '__main__':
    app.run(debug=True)
