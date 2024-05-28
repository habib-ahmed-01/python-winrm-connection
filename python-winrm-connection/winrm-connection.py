#!/usr/bin/env python3
# -*- coding: utf-8; py-indent-offset: 4 -*-
#
# Author:  Habibul Bashar Ahmed [M327731]
# Contact: Monitoring Team [ICINGA]

import sys
import argparse
import logging
import winrm


__author__ = 'Habibul Bashar Ahmed'
__version__ = '01'

DESCRIPTION = """This script establishes a WinRM connection to Windows machines,
                 allowing for the remote execution of commands. It supports both
                 Basic Authentication and Domain Authentication for secure access."""


# Parse command line
def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument(
        '-V', '--version',
        action='version',
        version='{0}: v{1} by {2}'.format('%(prog)s', __version__, __author__),
    )

    parser.add_argument(
        '-H', '--host',
        dest='host',
        help='Provide Hostname or IP',
        type=str,
        required=True
    )

    parser.add_argument(
        '-u', '--user',
        dest='username',
        help='Username or Domain User',
        type=str,
        required=True
    )

    parser.add_argument(
        '-pass', '--password',
        dest='password',
        help='Password for Username or Domain',
        type=str,
        required=True
    )

    parser.add_argument(
        '-ic', '--icingacmd',
        dest='command',
        help='The Command that needs to be executed on remote machine',
        type=str,
    )

    parser.add_argument(
        '--transport',
        dest='transport',
        default='ntlm',
        help='Choose authentication type. (default:ntlm)',
        type=str,
        choices=['ntlm','basic']
    )

    parser.add_argument(
        '--protocol',
        dest='protocol',
        default='https',
        help='Choose protocol (default:https)',
        type=str,
        choices=['http','https']
    )

    parser.add_argument(
        '-p', '--port',
        dest='port',
        default=5986,
        help='Port for communication (default:5986)',
        type=int,
        choices=[5985,5986]
    )

    parser.add_argument(
        '--timeout',
        dest='operation_timeout_sec',
        default=60,
        help='Explicit timeout for execution (default:60s)',
        type=int,
    )

    return parser.parse_args()



# Create a winrm Session
def create_winrm_session(endpoint, USERNAME, PASSWORD, TRANSPORT, TIMEOUT):

    try:
        winrm_session = winrm.Session(target=endpoint, auth=(USERNAME,PASSWORD), transport=TRANSPORT, server_cert_validation='ignore', operation_timeout_sec=TIMEOUT, read_timeout_sec=TIMEOUT+10)
        return winrm_session

    except Exception as e:
        print(f"CONNECTION FAILED: {e}")



# Execute Command
def execute_command(session, command):

    try:
        # Run a Shell command
        result = session.run_cmd(command)
        parse_results_nagios_format(result=result)

    # Handle transport errors (e.g., network issues)
    except winrm.exceptions.WinRMTransportError as e:
        parse_results_nagios_format(error=e, error_exception="Transport Error:")

    # Handle authentication errors
    except winrm.exceptions.InvalidCredentialsError as e:
        parse_results_nagios_format(error=e, error_exception="Invalid Credentials:")

    # Handle other generic errors
    except Exception as e:
        # print("An error occurred:", str(e))
        parse_results_nagios_format(error=e, error_exception="An error occurred:")



# Parse Results or Errors
def parse_results_nagios_format(result=None, error=None, error_exception=None):

    if result:
        if result.status_code == 0:
            print(result.std_out.decode('utf-8').strip())
            sys.exit(0)
        else:
            print(result.std_out.decode('utf-8').strip())
            print(result.std_err.decode('utf-8').strip())
            sys.exit(result.status_code)

    elif error:
        print(error_exception, str(error))

    else:
        print("Code review needed. Contact:Habibul Bashar Ahmed")



if __name__=='__main__':

    # Getting results from command line and storing in results
    results = parse_args()

    # Creating a dictionary
    arguments = results.__dict__

    # Https or Not
    if (arguments['port'] == 5986) and (arguments['protocol'] == 'https'):
        # Creating a Endpoint string
        endpoint = f"https://{arguments['host']}:5986/wsman"

    else:
        # Creating a Endpoint string
        endpoint = f"http://{arguments['host']}:5985/wsman"

    USERNAME = arguments['username']
    PASSWORD = arguments['password']
    TRANSPORT = arguments['transport']
    TIMEOUT = arguments['operation_timeout_sec']
    COMMAND = arguments['command']

    # Call winrm session
    if COMMAND:
        session_instance = create_winrm_session(endpoint, USERNAME, PASSWORD, TRANSPORT, TIMEOUT)
        if session_instance:
            r = execute_command(session_instance, COMMAND)
    else:
        print(f"No Command provided. Use [--help] for display usage.")
        sys.exit(2)
