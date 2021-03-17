'''
Created on 2 Mar 2020

@author: riccardo
'''
import os
import pandas as pd
import numpy as np
from os.path import join, dirname
import pandas.io.pytables

if __name__ == '__main__':
    file  = join(dirname(__file__), 'tmp.hdf')
    dorig = pd.DataFrame({'a': ['', 'asdåß']})
    d = dorig.copy()
    
    # EXAMPLE 1: save the string columns, opening back the column dtype
    # is object
    d.to_hdf(file, mode='w', format='table', key='t')
    d = pd.read_hdf(file)
    assert d.a.dtype == object
    
    # Example 2: providing the encoding parameter does not change anything
    d.to_hdf(file, mode='w', format='table', key='t', encoding='utf-8')
    d = pd.read_hdf(file)
    assert d.a.dtype == object
    
    # Example 3: providing the encoding parameter in the dataframe
    # column. IT RAISES!! WTF??
    d.a = d.a.str.encode('utf8')
    try:
        d.to_hdf(file, mode='w', format='table', key='t')
    except TypeError:
        # TypeError: Cannot serialize the column [a] because
        # its data contents are [bytes] object dtype
        pass

    # Example 4. astype('S5'): Same as above
    d.a = dorig.a.copy()
    try:
        d.a = d.a.astype('S5')
    except UnicodeEncodeError:
        pass
    
    # Example 4. This is wrong because it converts BUT
    # it stringifies the bytes object, thus resulting in strings
    # starting with b'
    d.a = dorig.a.copy()
    d.a = d.a.str.encode('utf8').astype(str)
    try:
        d.to_hdf(file, mode='w', format='table', key='t')
    except TypeError:
        # TypeError: Cannot serialize the column [a] because
        # its data contents are [bytes] object dtype
        pass

    # WE FORGET ABOUT ENCODING FOR THE MOMENT.
    # WE WANT TO IBSERVE ONE THING:

    # Write the file again.
    d = dorig.copy()
    d.to_hdf(file, mode='w', format='table', key='t',
             min_itemsize={'a': 5})
    
    # 1] This works because we append shorter (or equal) strings. Fine:
    d.iloc[1, 0] = 'asd'
    d.to_hdf(file, mode='a', format='table', key='t', append=True,
             min_itemsize={'a': 5})
    
    # 2] this does NOT work because we have longer strings. fine:
    d = dorig.copy()
    d.iloc[0, 0] = 'asdasdasd'
    try:
        d.to_hdf(file, mode='a', format='table', key='t', append=True,
                 min_itemsize={'a': 5})
    except ValueError:
        pass
    
    # BUT FUCK!! this does NOT work EITHER because we have ALL empty strings:
    d = dorig.copy()
    d.loc[:, 'a'] = ''
    try:
        d.to_hdf(file, mode='a', format='table', key='t', append=True,
                 min_itemsize={'a': 5})
    except ValueError:
        pass

    
        pass
    # This seem to work: convert to unicode (numpy unicode)
    d = dorig.copy()
    d.loc[:, 'a'] = ''
    if d.a.str.match('^$').all():
        # this RAISES if any string has non ASCII characters:
        # d.loc[:, 'a'] = '\0'  # np.array(d.a.values, dtype='U0')
        # np.array(d.a.values, dtype='S0').astype(str)
        d['a'] = d['a'].values.astype('S1')
    try:
        d.to_hdf(file, mode='a', format='table', key='t', append=True,
                 min_itemsize={'a': 5})
    except ValueError as _:
        pass
    
    
    d = pd.read_hdf(file)
    asd = 9