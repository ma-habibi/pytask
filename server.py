"""********************************************
File: server.py
Author: Metflekx

Desc. :
    Offer a restfull API that listens for a 
    POST request on "url/vehicles" which 
    contains a csv file.
    Obtains some resources, merges and
    returns all the data in JSON. 

TODO:
    [ ] Improve-------------------------
    [*] Fix Path
    [ ] Fix File structure (sep. modules)
    [ ] Improve Error Handling.
    [ ] Write tests.
    [ ] Implement O(1) lookups.
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
    Offers a REST-API.
    """

    def __init__(self):
        """
        get API access_token
        """

        self.access_token = self.__get_access_token()

    def __get_access_token(self):
        """
        Get access token for
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
        Merges dataframes, apply filters
        and returns in JSON.
        """
    
        # merge req and res data
        df = pd.merge(df_req, df_api,
                         on="kurzname",
                         how="outer",
                         validate="one_to_many",
                         suffixes=("", "_res"))

        # Leave out any row without 'hu'
        df = df[df["hu"].notna()]
    
        # Combine labelId and LabelId_res
        df['labelIds'] = df[
                'labelIds'].combine_first(
                        df['labelIds_res'])
        df = df.drop(
                columns=['labelIds_res'])
    
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
