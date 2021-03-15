"""
Created on Oct 30, 2017

@author: croaker
"""
from collections import namedtuple


def makeNamedTuple(self, rowData, rowName=None):
    """
    Makes a namedtuple from a sqlite3.Row object.

    rowName can provide a custom name for the namedtuple, else name defaults to Row

    :returns:
    None if rowData is None - fetchone() with no records returned
    A namedtuple if rowData is a single sqlite3.Row - fetchone() one record returned.
    A list of namedtuple if rowData is a list of sqlite3.Row - fetchmany() or fetchall() more than one record returned.
    An empty list if no records are returned from fetchmany() or fetchall()
    """
    # FIXME docstring
    if not rowName:
        rowName = "Row"
    if not rowData:
        return None
    if not isinstance(rowData, list):
        #            print('one')
        names = rowData.keys()
        Row = namedtuple(rowName, names)
        return Row(*rowData)
    names = rowData[0].keys()
    Row = namedtuple(rowName, names)
    ntData = []
    for row in rowData:
        ntData.append(Row(*row))
    return ntData
