# -*- coding: utf-8 -*-
import tempfile
from subprocess import check_output, CalledProcessError, call
import re
import var as v


def _isDeviceAvailable():
    """
    Private Function to check if device is available;
    To be used by only functions inside module
    :return: True or False
    """
    result = getserialno()
    if result[1].strip() == "unknown":
        return False
    else:
        return True


def isDeviceAvailable(device_name):
    """
    Private Function to check if device is available;
    To be used by only functions inside module
    :return: True or False
    """
    if device_name is None:
        return _isDeviceAvailable()
    result = False
    for device in devices():
        if device == device_name:
            result = True
            break
    return result


def version():
    """
    Display the version of adb
    :return: result of _exec_command() execution
    """
    adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_VERSION]
    return _exec_command(adb_full_cmd)


def bugreport(dest_file="default.log", device_name=None):
    """
    Prints dumpsys, dumpstate, and logcat data to the screen, for the purposes of bug reporting
    :param device_name: Default value is None
    :return: result of _exec_command() execution
    """
    if device_name is not None:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, '-s', device_name, v.ADB_COMMAND_BUGREPORT]
    else:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_BUGREPORT]
    try:
        dest_file_handler = open(dest_file, "w")
    except IOError:
        print "IOError: Failed to create a log file"

    # We have to check if device is available or not before executing this command
    # as adb bugreport will wait-for-device infinitely and does not come out of 
    # loop
    # Execute only if device is available only
    if isDeviceAvailable(device_name):
        result = _exec_command_to_file(adb_full_cmd, dest_file_handler)
        return (result, "Success: Bug report saved to: " + dest_file)
    else:
        return (0, "Device Not Found")


def connect(device_name):
    """
    Connect to target device name
    :param device_name: string target device name
    :return: result of _exec_command() execution
    """
    if device_name is not None:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_CONNECT, device_name]
        return _exec_command(adb_full_cmd)


def reconnect(device_name):
    """
    Reconnect to target device name
    :param device_name: string target device name
    :return: result of _exec_command() execution
    """
    if device_name is not None:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_RECONNECT, device_name]
        return _exec_command(adb_full_cmd)


def disconnect(device_name):
    """
    Disconnect to target device name
    :param device_name: string target device name
    :return: result of _exec_command() execution
    """
    if device_name is not None:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_DISCONNECT, device_name]
        return _exec_command(adb_full_cmd)


def push(src, dest, device_name=None):
    """
    Push object from host to target
    :param src: string path to source object on host
    :param dest: string destination path on target
    :return: result of _exec_command() execution
    """
    if device_name is not None:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, '-s', device_name, v.ADB_COMMAND_PUSH, src, dest]
    else:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_PUSH, src, dest]
    return _exec_command(adb_full_cmd)


def pull(src, dest, device_name=None):
    """
    Pull object from target to host
    :param src: string path of object on target
    :param dest: string destination path on host
    :return: result of _exec_command() execution
    """
    if device_name is not None:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, '-s', device_name, v.ADB_COMMAND_PULL, src, dest]
    else:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_PULL, src, dest]
    return _exec_command(adb_full_cmd)


def devices(opts=[]):
    """
    Get list of all available devices including emulators
    :param opts: list command options (e.g. ["-r", "-a"])
    :return: result of _exec_command() execution
    """
    adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_DEVICES]
    result = _exec_command(adb_full_cmd)
    lines = result[1].split("\n")
    dev_list = []
    for line in lines:
        group = line.strip().split("\t")
        if len(group) >1 and group[1] == "device":
            dev_list.append(group[0])
    return dev_list


def shell(cmd, device_name=None):
    """
    Execute shell command on target
    :param cmd: string shell command to execute
    :return: result of _exec_command() execution
    """
    if device_name is not None:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, '-s', device_name, v.ADB_COMMAND_SHELL, cmd]
    else:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_SHELL, cmd]
    return _exec_command(adb_full_cmd)


def get_package_list(device_name=None):
    """
    Execute shell command on target
    :param device_name: device_name
    :return: result of package list on dedicated device
    """
    ret, result = shell(v.ADB_SCRIPT_PACKAGELIST, device_name)
    package_list = []
    if ret == 0:
        lines = result.split("\n")
        for line in lines:
            group = line.strip().split(":")
            if group[0] == "package":
                package_list.append(group[1])
    return package_list


def check_process_status(appName, device_name=None):
    """
    Execute shell command on target
    :param device_name: device_name
    :param device_name: device_name
    :return: status of app on dedicated device
    """
    result = False
    ret, output = shell(v.ADB_SCRIPT_PS, device_name)
    if output.find(appName):
        result = True
    return result


def get_process_id(appName, device_name=None):
    """
    Execute shell command on target
    :param device_name: device_name
    :param device_name: device_name
    :return: pid of app on dedicated device
    """
    result = None
    ret, output = shell(v.ADB_SCRIPT_PS, device_name)
    lines = output.strip('\r').split('\n')
    for line in lines:
        m = re.match('^\S+\s+([0-9]+).+{0}'.format(appName), line)
        if m is not None:
            result = m.group(1)
    return result


def install(apk, device_name=None, opts=[]):
    """
    Install *.apk on target
    :param apk: string path to apk on host to install
    :param opts: list command options (e.g. ["-r", "-a"])
    :return: result of _exec_command() execution
    """
    if device_name is not None:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, '-s', device_name, v.ADB_COMMAND_INSTALL, "-r", _convert_opts(opts), apk]
    else:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_INSTALL, "-r", _convert_opts(opts), apk]
    return _exec_command(adb_full_cmd)


def uninstall(app, device_name=None, opts=[]):
    """
    Uninstall app from target
    :param app: app name to uninstall from target (e.g. "com.example.android.valid")
    :param opts: list command options (e.g. ["-r", "-a"])
    :return: result of _exec_command() execution
    """
    if device_name is not None:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, '-s', device_name, v.ADB_COMMAND_UNINSTALL, _convert_opts(opts), app]
    else:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_UNINSTALL, _convert_opts(opts), app]
    return _exec_command(adb_full_cmd)


def getserialno(device_name=None):
    """
    Get serial number for all available target devices
    :return: result of _exec_command() execution
    """
    if device_name is not None:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, '-s', device_name, v.ADB_COMMAND_GETSERIALNO]
    else:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_GETSERIALNO]
    return _exec_command(adb_full_cmd)

def get_package_info(package, info_type, device_name=None):
    """
    Get serial number for all available target devices
    :return: result of _exec_command() execution
    """
    result = ""
    if device_name is not None:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, '-s', device_name, v.ADB_SCRIPT_DUMP_PACKAGEINFO.format(package)]
    else:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_SCRIPT_DUMP_PACKAGEINFO.format(package)]
    ret, output = _exec_command(adb_full_cmd)
    if ret == 0:
        lines = output.split("\n")
        for line in lines:
            group = line.split(":")
            if group[0].strip() == info_type:
                result = group[1].strip()
                break
    return result



def wait_for_device(device_name=None):
    """
    Block execution until the device is online
    :return: result of _exec_command() execution
    """
    if device_name is not None:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, '-s', device_name, v.ADB_COMMAND_WAITFORDEVICE]
    else:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_WAITFORDEVICE]
    return _exec_command(adb_full_cmd)


def sync(device_name=None):
    """
    Copy host->device only if changed
    :return: result of _exec_command() execution
    """
    if device_name is not None:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, '-s', device_name, v.ADB_COMMAND_SHELL, v.ADB_COMMAND_SYNC]
    else:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_SHELL, v.ADB_COMMAND_SYNC]
    return _exec_command(adb_full_cmd)


def start_server():
    """
    Startd adb server daemon on host
    :return: result of _exec_command() execution
    """
    adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_START_SERVER]
    return _exec_command(adb_full_cmd)


def kill_server():
    """
    Kill adb server daemon on host
    :return: result of _exec_command() execution
    """
    adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_KILL_SERVER]
    return _exec_command(adb_full_cmd)


def get_state(device_name=None):
    """
    Get state of device connected per adb
    :return: result of _exec_command() execution
    """
    if device_name is not None:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, '-s', device_name, v.ADB_COMMAND_GET_STATE]
    else:
        adb_full_cmd = [v.ADB_COMMAND_PREFIX, v.ADB_COMMAND_GET_STATE]
    return _exec_command(adb_full_cmd)


def _convert_opts(opts):
    """
    Convert list with command options to single string value
    with 'space' delimeter
    :param opts: list with space-delimeted values
    :return: string with space-delimeted values
    """
    return ' '.join(opts)


def _exec_command(adb_cmd):
    """
    Format adb command and execute it in shell
    :param adb_cmd: list adb command to execute
    :return: string '0' and shell command output if successful, otherwise
    raise CalledProcessError exception and return error code
    """
    t = tempfile.TemporaryFile()
    final_adb_cmd = []
    for e in adb_cmd:
        if e != '':  # avoid items with empty string...
            final_adb_cmd.append(e)  # ... so that final command doesn't
            # contain extra spaces
    print('\n*** Executing {0} command'.format(' '.join(adb_cmd)))

    try:
        output = check_output(final_adb_cmd, stderr=t)
    except CalledProcessError as e:
        t.seek(0)
        result = e.returncode, t.read()
    else:
        result = 0, output
        print('\n' + result[1])

    return result


def _exec_command_to_file(adb_cmd, dest_file_handler):
    """
    Format adb command and execute it in shell and redirects to a file
    :param adb_cmd: list adb command to execute
    :param dest_file_handler: file handler to which output will be redirected
    :return: string '0' and writes shell command output to file if successful, otherwise
    raise CalledProcessError exception and return error code
    """
    t = tempfile.TemporaryFile()
    final_adb_cmd = []
    for e in adb_cmd:
        if e != '':  # avoid items with empty string...
            final_adb_cmd.append(e)  # ... so that final command doesn't
            # contain extra spaces
    print('\n*** Executing ' + ' '.join(adb_cmd) + ' ' + 'command')

    try:
        output = call(final_adb_cmd, stdout=dest_file_handler, stderr=t)
    except CalledProcessError as e:
        t.seek(0)
        result = e.returncode, t.read()
    else:
        result = output
        dest_file_handler.close()

    return result
