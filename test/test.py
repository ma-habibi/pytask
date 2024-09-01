import sys
import os
import unittest

sys.path.insert(0, 
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(
                            __file__), 
                        '../src/client')))

import client

def test():
    client.client()

if __name__ == "__main__":
    test()
# python test.py ../vehicles.csv -k kurzname fuck info hu labelIds gruppe gruppe_res kurzname_res -c
