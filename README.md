# Author's Notes

To whom it may concern,

Feel free to read through my solution to the problem provided by VERO.
Find the scripts at `/src/clinet/client.py` and `/src/server/server.py`.

## HOW TO RUN

#### Navigate to directory.

```sh
cd pytask
```

#### Make virtual environment and install the requirements.

```sh
python -m venv venv
```

```sh
source venv/bin/activate && pip install -r requirement.txt
```

#### Get the server running.
```sh
python /src/server/server.py
```

#### Run the client script

To produce xlsx output run the code with the arguments speciefied in the task.

e.g:
```sh
python run/run.py vehicles.csv -k kurzname info labelIds -c
```

Get some help:
```sh
python run/run.py -h
```

```txt
usage: run.py [-h] [-k KEYS [KEYS ...]] [-c] filename

client.py(VERO pytask): write vehicles data to a xlsx file.

positional arguments:
  filename

optional arguments:
  -h, --help            show this help message and exit
  -k KEYS [KEYS ...], --keys KEYS [KEYS ...]
                        Columns to write out : arbitary amount of strings
```

-Mahdi Habibi
