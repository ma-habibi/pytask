"""********************************************
File: server.py
Author: Mahdi Habibi

Desc. :
    Offer a restfull API that listens for a 
    POST request on "url/vehicles" which 
    contains a csv file.
    Obtains some resources, merges and
    returns all the data in JSON. 

Improve:
    [ ] Implement O(1) lookups.
********************************************"""

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_caching import Cache
import requests
import pandas as pd


# Init
app = Flask(__name__)
api = Api(app)

# Configure Caching
cache = Cache(app,
              config={"CACHE_TYPE": "SimpleCache",
                      "CACHE_DEFAULT_TIMEOUT": 1200})

class Vehicles(Resource):
    """
    Offers a REST-API.
    """

    def __init__(self):
        """
        get API access_token
        """

        self.access_token = self.__get_access_token()

    @cache.cached(timeout=1200, 
                  key_prefix="access_token")
    def __get_access_token(self):
        """
        Get access token for
        the API
        """
    
        try:
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

        except requests.RequestException as e:
            print(F"ERROR: server failed fetching access token: {e}")
            return None

    @cache.cached(timeout=300, 
                  key_prefix="vehicles_data")
    def __fetch(self):
        """
        Gets resources to read into
        df_api.
        """
    
        # Request the resources
        res = (requests.get(
                "https://api.baubuddy.de"
                "/dev/index.php/v1/vehicles"
                "/select/active",
                headers = {
                    "Authorization":
                    f"Bearer {self.access_token}"}))
        df_api = pd.DataFrame(res.json())

        return df_api
    
    @staticmethod
    def __accept(csv_content):
        """
        Takes in data from the clinet.
        Reads into a pandas dataframe
        and returns the df.
        """

        return pd.read_csv(csv_content,
                           delimiter=';')

    @staticmethod
    def __combine_overlaps(df, columns_req):
        """
        Helps merging overlapping data
        by combining the duplicate columns.
        """

        for column in columns_req:
            duplicate_column = column+"_res"
            if duplicate_column in df.columns:
                df[column] = df[
                        column].combine_first(
                                df[duplicate_column])
                df = df.drop(
                        columns=[duplicate_column])

        return df

    def __process(self, df_api, df_req):
        """
        Merges dataframes, apply filters
        and returns in JSON.
        """
    
        # Obtain columns to combine overlaps
        columns_req = df_req.columns

        # merge req and res data
        df = pd.merge(df_req, df_api,
                         on=["kurzname"],
                         how="outer",
                         suffixes=("", "_res"))

        # Leave out any row without 'hu'
        df = df[df["hu"].notna()]
    
        # Combine all overlaping columns
        df = self.__combine_overlaps(df, columns_req)

        # For each labelId in the
        # vehicle's JSON array
        # labelIds resolve its colorCode
        for i, row in df.iterrows():
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
                df.at[i, "labelIds"]=\
                res.json()[0]["colorCode"]
    
        # return data-structure in JSON format
        return df.to_json()
    
    def post(self):
        """
        Listens for a POST request
        and accepts a csv,
        downloads a certain set of
        resources, merges them with the
        csv, applies filtering, and
        returns them in Json.
        """

        file = request.files["file"]
        if file is None:
            return jsonify(
                    {"Error": "No such file"}), 400
        if not file.filename.endswith(".csv"):
            return jsonify(
                    {"Error": "file must end with '.csv'"}), 400

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
    app.run()
