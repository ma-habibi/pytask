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

# Built-ins
from io import BytesIO
from datetime import date # for today
import argparse

# Third-party
import requests
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill


GREEN = "007500"
ORANGE = "FFA500"
RED = "b30000"

def df_towb(df):
    """ writes a pandas
    dataframe df into a
    openpyxl's workbook
    in memory.
    """

    xlbuf = BytesIO() # create buffer
    df.to_excel(xlbuf, index=False) # out xlsx
    xlbuf.seek(0) # seek begin
    wb = load_workbook(xlbuf) # load wb.
    return wb

def get_colors(df):
    """ Make a new column colortmp
    in df Obtain the row color
    according to the hu value.
    """

    df["colortmp"] = None
    today = int(str(
        date.today()).replace(
            "-", ""))
    twelve_m = today - 10000
    three_m = today - 300
    for i, huval in enumerate(df["hu"]):
        if isinstance(huval, str):
            huval = int(
                    huval.replace(
                        "-", ""))
            if huval < twelve_m:
                if huval < three_m:
                    df.at[i, "colortmp"] = GREEN
                    continue
                df.at[i, "colortmp"] = ORANGE
                continue
            df.at[i, "colortmp"] = RED

def tint_labelids(ws):
    """ If labelIds are given
    and at least one colorCode
    could be resolved, use the
    first colorCode to tint the
    cell's text
    (if labelIds is given in -k)

    Given a openpyxl.workbook wb
    Paint the labelId cell to the
    color assiciated with it and
    return the new painted workbook.
    """

    i = 2 # skip the keys
    j = 0
    while i < ws.max_row and\
            j < ws.max_column:
        if ws[1][j].value != "labelIds":
            j += 1
            continue

        color = ws[i][j].value
        if color is not None:
            # delete hashtag
            color = str(color)[1:]

            fill = PatternFill(
                    start_color=color,
                    end_color=color,
                    fill_type="solid")
            ws[i][j].fill = fill

        i += 1

def paint_rows(ws) -> int:
    """ Use the values stored
    in colortmp, to paint each
    row according to hu value.
    returns the index at which
    the colortmp exist.
    in a call to paint_rows the
    return value must be used
    to delete tmp column.
    """

    # find the colortmp index
    cti = 0
    while cti < ws.max_column and\
    ws[1][cti].value != "colortmp":
        cti += 1

    i = 2
    while i < ws.max_row + 1:
        # Get color
        color = ws[i][cti].value
        if isinstance(color, str):
            # Paint row
            j = 0
            fill = PatternFill(
                    start_color=color,
                    end_color=color,
                    fill_type="solid")
            while j < ws.max_column:
                ws[i][j].fill = fill
                j += 1

        i += 1

    # return index of tmp col
    return cti + 1

def client():
    """Transmits a CSV to
    a REST-API
    (s. Server-section below),
    handles the response and
    generates an Excel-File
    taking the input parameters
    into account.
    """

    # handle args
    parser = argparse.ArgumentParser(
            description=\
                    "VERO pytask:"
                    " write vehicles data"
                    " to a xlsx file.")

    # handle -k flag
    # Columns always contain rnr field
    cols = ["rnr"]
    parser.add_argument(
            "-k",
            "--keys",
            nargs="+",
            help="Columns to write"
            " out : arbitary amount"
            " of strings")

    parser.add_argument(
            "-c",
            "--colored",
            action="store_true",
            help="Disable colord output.",
            default=False)

    args = parser.parse_args()

    # Call server and retrieve json data
    response = requests.post(
      url="http://127.0.0.1:5000/vehicles",
      files={"file": open("vehicles.csv", "rb")})

    df = pd.read_json(response.json())

    # additional columns
    for arg in args.keys:
        # Check input in O(n)
        if arg not in df.columns:
            print(f"no column matching the"
                  f"{arg}, will leave out")
            continue
        cols.append(arg)

    # Write colors to a tmp. column.
    if (args.colored):
        get_colors(df)
        cols.append("colortmp")

    # Sort byt gruppe
    df = df.sort_values(by=["gruppe"])

    df = df[[col for col in cols]]
    del cols

    wb = df_towb(df)
    del df

    # Get worksheet
    ws = wb["Sheet1"]

    # Tint cell with the resolved
    # label id value
    tint_labelids(ws)

    # Paint each row for colored
    if (args.colored):
        ws.delete_cols(
                paint_rows(ws), 
                amount=1)

    # output
    wb.save(f"vehicles_"
            f"{str(date.today())}"
            ".xlsx")

client()
