#!/usr/bin/python3

"""
Upgrade script to enable authentication for CUPS-Get-Document in
default policy
"""

import os
import sys
from shutil import copy


def get_cupsd_conf():
    """
    Get all lines from cupsd.conf
    """
    if not os.path.exists('/etc/cups/cupsd.conf'):
        return None

    lines = []
    with open('/etc/cups/cupsd.conf', encoding="utf-8") as conf:
        lines = conf.readlines()

    return lines


def get_default_policy(lines):
    """
    Get the default policy lines

    :param list lines: lines from cupsd.conf
    """
    default_policy = []
    in_policy = False

    for line in lines:
        if not in_policy and not line.lstrip().startswith('<Policy default>'):
            continue

        default_policy.append(line)

        if line.lstrip().startswith('</Policy>'):
            return default_policy

        in_policy = True

    return default_policy


def get_limit_with_document(lines):
    """
    Get <Limit> scope which defines CUPS-Get-Document operation

    :param list lines: Lines containing the default policy
    """
    limit = []
    in_limit = False

    for line in lines:
        if not in_limit and not line.lstrip().startswith('<Limit'):
            continue

        if (not in_limit and line.lstrip().startswith('<Limit') and
            not 'CUPS-Get-Document' in line.lstrip().split('#')[0][1:-1]):
            continue

        limit.append(line)

        if line.lstrip().startswith('</Limit>'):
            return limit

        in_limit = True

    return limit


def check_for_authtype(lines):
    """
    Check if <Limit> defining CUPS-Get-Document defines
    any authentication

    :param list lines: Lines of <Limit> scope which defines CUPS-Get-Document
    """
    for line in lines:
        if line.lstrip().startswith('AuthType'):
            return True
    return False


def migrate_cupsd_conf(lines):
    """
    Make changes to cupsd.conf contents to use authentication
    for CUPS-Get-Document

    :param list lines: Lines from cupsd.conf
    """
    new_lines = []
    in_policy = False
    create_document_limit = False

    for line in lines:
        if (in_policy and line.lstrip().startswith('<Limit') and
            not line.lstrip().startswith('<Limit CUPS-Get-Document>') and
            'CUPS-Get-Document' in line.lstrip().split('#')[0][1:-1]):
            line = line.replace(' CUPS-Get-Document', '')
            create_document_limit = True

        if in_policy and line.lstrip().startswith('</Policy>') and create_document_limit:
            new_lines.append('\n')
            new_lines.append((len(line) - len(line.lstrip()) + 2) * ' ' +
                             '# added during upgrade\n')
            new_lines.append((len(line) - len(line.lstrip()) + 2) * ' ' +
                             '<Limit CUPS-Get-Document>\n')
            new_lines.append((len(line) - len(line.lstrip()) + 4) * ' ' +
                             'AuthType Default\n')
            new_lines.append((len(line) - len(line.lstrip()) + 4) * ' ' +
                             'Require user @OWNER @SYSTEM\n')
            new_lines.append((len(line) - len(line.lstrip()) + 4) * ' ' +
                             'Order deny,allow\n')
            new_lines.append((len(line) - len(line.lstrip()) + 2) * ' ' +
                             '</Limit>\n')
            create_document_limit = False

        new_lines.append(line)

        if not in_policy:
            if line.lstrip().startswith('<Policy default>'):
                in_policy = True
            continue

        if line.lstrip().startswith('<Limit CUPS-Get-Document>'):
            new_lines.append((len(line) - len(line.lstrip()) + 2) * ' ' +
                             '# added during upgrade\n')
            new_lines.append((len(line) - len(line.lstrip()) + 2) * ' ' +
                             'AuthType Default\n')
            continue

        if line.lstrip().startswith('</Policy>'):
            in_policy = False
            continue

    return new_lines


def apply_changes(lines):
    """
    Backup the original file if there is no .rpmsave already and
    apply changes to the actual cupsd.conf

    :param list lines: New lines for cupsd.conf
    """
    if not os.path.exists('/etc/cups/cupsd.conf.rpmsave'):
        copy('/etc/cups/cupsd.conf', '/etc/cups/cupsd.conf.rpmsave')

    with open('/etc/cups/cupsd.conf', 'w', encoding='utf-8') as conf:
        conf.writelines(lines)



content = get_cupsd_conf()
if content is None:
    sys.exit(1)

if check_for_authtype(get_limit_with_document(get_default_policy(content))):
    sys.exit(0)

new_content = migrate_cupsd_conf(content)

apply_changes(new_content)

sys.exit(0)
