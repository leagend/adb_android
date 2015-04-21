import os
import subprocess

ADB_COMMAND_PREFIX = 'adb'
ADB_COMMAND_SHELL = 'shell'
ADB_COMMAND_PULL = 'pull'
ADB_COMMAND_PUSH = 'push'
ADB_COMMAND_RM = 'rm -r'
ADB_COMMAND_CHMOD = 'chmod -R 777'
ADB_COMMAND_UNINSTALL = 'uninstall'
ADB_COMMAND_INSTALL = 'install'
ADB_COMMAND_FORWARD = 'forward'

def push(src, dest):
    """Pushes files and folders to device."""
    if (src is not None) and (dest is not None):
        adb_full_cmd = [ ADB_COMMAND_PREFIX, ADB_COMMAND_PUSH, src, dest ]
        print('*** executing ' + str(adb_full_cmd))
        return exec_result_handler(adb_full_cmd)
    else:
        return False

def pull(src, dest):
    """Pulls files and folders to device."""
    if (src is not None) and (dest is not None):
        adb_full_cmd = [ ADB_COMMAND_PREFIX, ADB_COMMAND_PULL, src, dest ]
        print('*** executing ' + str(adb_full_cmd))
        return exec_result_handler(adb_full_cmd)
    else:
        return False

def exec_result_handler(adb_full_cmd):
    """Executes adb command and handles result code.

    Based on adb command execution result returns
    True (0) or False (!=0).

    """
    if adb_full_cmd is not None:
        exec_res = subprocess.call(adb_full_cmd)
        if exec_res == 0:
            return True
        else:
            return False
    else:
        return False