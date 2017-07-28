def work( storage, message ) :
    from os import popen
    result = popen( message ).read()
    return result
