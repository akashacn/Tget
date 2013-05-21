'''
Created on 2013-5-21

@author: zpfalpc23
'''

def infrange(prefix, start = 1):
    yield prefix
    while True:
        yield prefix + "." + str(start)
        start += 1