# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
All of the py.test fixtures used by astropy.table are defined here.

The fixtures can not be defined in the modules that use them, because
those modules are imported twice: once with `from __future__ import
unicode_literals` and once without.  py.test complains when the same
fixtures are defined more than once.

`conftest.py` is a "special" module name for py.test that is always
imported, but is not looked in for tests, and it is the recommended
place to put fixtures that are shared between modules.  These fixtures
can not be defined in a module by a different name and still be shared
between modules.
"""

from copy import deepcopy
from collections import OrderedDict
import pickle

import numpy as np

from ...tests.helper import pytest
from ... import table
from ...table import table_helpers, Table
from ... import time
from ... import units as u
from ... import coordinates
from .. import pprint


@pytest.fixture(params=[table.Column, table.MaskedColumn])
def Column(request):
    # Fixture to run all the Column tests for both an unmasked (ndarray)
    # and masked (MaskedArray) column.
    return request.param


class MaskedTable(table.Table):
    def __init__(self, *args, **kwargs):
        kwargs['masked'] = True
        table.Table.__init__(self, *args, **kwargs)


class MyRow(table.Row):
    pass


class MyColumn(table.Column):
    pass


class MyMaskedColumn(table.MaskedColumn):
    pass


class MyTableColumns(table.TableColumns):
    pass


class MyTableFormatter(pprint.TableFormatter):
    pass


class MyTable(table.Table):
    Row = MyRow
    Column = MyColumn
    MaskedColumn = MyMaskedColumn
    TableColumns = MyTableColumns
    TableFormatter = MyTableFormatter

# Fixture to run all the Column tests for both an unmasked (ndarray)
# and masked (MaskedArray) column.
@pytest.fixture(params=['unmasked', 'masked', 'subclass'])
def table_types(request):
    class TableTypes:
        def __init__(self, request):
            if request.param == 'unmasked':
                self.Table = table.Table
                self.Column = table.Column
            elif request.param == 'masked':
                self.Table = MaskedTable
                self.Column = table.MaskedColumn
            elif request.param == 'subclass':
                self.Table = MyTable
                self.Column = MyColumn
    return TableTypes(request)


# Fixture to run all the Column tests for both an unmasked (ndarray)
# and masked (MaskedArray) column.
@pytest.fixture(params=[False, True])
def table_data(request):
    class TableData:
        def __init__(self, request):
            self.Table = MaskedTable if request.param else table.Table
            self.Column = table.MaskedColumn if request.param else table.Column
            self.COLS = [
                self.Column(name='a', data=[1, 2, 3], description='da',
                            format='fa', meta={'ma': 1}, unit='ua'),
                self.Column(name='b', data=[4, 5, 6], description='db',
                            format='fb', meta={'mb': 1}, unit='ub'),
                self.Column(name='c', data=[7, 8, 9], description='dc',
                            format='fc', meta={'mc': 1}, unit='ub')]
            self.DATA = self.Table(self.COLS)
    return TableData(request)


class SubclassTable(table.Table):
    pass


@pytest.fixture(params=[True, False])
def tableclass(request):
    return table.Table if request.param else SubclassTable


@pytest.fixture(params=list(range(0, pickle.HIGHEST_PROTOCOL + 1)))
def protocol(request):
    """
    Fixture to run all the tests for all available pickle protocols.
    """
    return request.param


# Fixture to run all tests for both an unmasked (ndarray) and masked
# (MaskedArray) column.
@pytest.fixture(params=[False, True])
def table_type(request):
    # return MaskedTable if request.param else table.Table
    try:
        request.param
        return MaskedTable
    except AttributeError:
        return table.Table


# Stuff for testing mixin columns

MIXIN_COLS = {'quantity': [0, 1, 2, 3] * u.m,
              'time': time.Time([2000, 2001, 2002, 2003], format='jyear'),
              'skycoord': coordinates.SkyCoord(ra=[0, 1, 2, 3] * u.deg,
                                               dec=[0, 1, 2, 3] * u.deg),
              'arraywrap': table_helpers.ArrayWrapper([0, 1, 2, 3]),
              'ndarray': np.array([(7, 'a'), (8, 'b'), (9, 'c'), (9, 'c')],
                           dtype='<i4,|S1').view(table.NdarrayMixin),
              }

@pytest.fixture(params=sorted(MIXIN_COLS))
def mixin_cols(request):
    """
    Fixture to return a set of columns for mixin testing which includes
    an index column 'i', two string cols 'a', 'b' (for joins etc), and
    one of the available mixin column types.
    """
    cols = OrderedDict()
    mixin_cols = deepcopy(MIXIN_COLS)
    cols['i'] = table.Column([0, 1, 2, 3], name='i')
    cols['a'] = table.Column(['a', 'b', 'b', 'c'], name='a')
    cols['b'] = table.Column(['b', 'c', 'a', 'd'], name='b')
    cols['m'] = mixin_cols[request.param]

    return cols

@pytest.fixture(params=[False, True])
def T1(request):
    T = Table.read([' a b c d',
                 ' 2 c 7.0 0',
                 ' 2 b 5.0 1',
                 ' 2 b 6.0 2',
                 ' 2 a 4.0 3',
                 ' 0 a 0.0 4',
                 ' 1 b 3.0 5',
                 ' 1 a 2.0 6',
                 ' 1 a 1.0 7',
                 ], format='ascii')
    T.meta.update({'ta': 1})
    T['c'].meta.update({'a': 1})
    T['c'].description = 'column c'
    if request.param:
        T.add_index('a')
    return T
