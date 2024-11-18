#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) 2017 Heinlein Support GmbH
#          Robert Sander <r.sander@heinlein-support.de>

#
# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.


from cmk.agent_based.v2 import (
    CheckPlugin,
    Service,
    Result,
    SimpleSNMPSection,
    SNMPTree,
    State,
    all_of,
    contains,
    exists,
)


def parse_dell_sc_sysinfo(string_table):
    return string_table

def discover_dell_sc_sysinfo(section):
    yield Service()

def check_dell_sc_sysinfo(section):
    state = {
        1  : ('Other', State.UNKNOWN),
        2  : ('Unknown', State.UNKNOWN),
        3  : ('OK', State.OK),
        4  : ('non Critical', State.WARN),
        5  : ('Critical', State.CRIT),
        6  : ('non Recoverable', State.CRIT),
    }

    version = section[0][0]
    servicetag = section[0][1]
    build = section[0][3]
    globalState = state.get(int(section[0][2]), ('Unknown', 3))

    yield Result(state=globalState[1], summary="Version %s, ServiceTag %s, Build %s, State %s" % (
        version,
        servicetag,
        build,
        globalState[0])
    )


check_plugin_dell_sc_sysinfo = CheckPlugin(
    name="dell_sc_sysinfo",
    sections = [ "dell_sc_sysinfo" ],
    service_name="Dell SC SysInfo",
    discovery_function=discover_dell_sc_sysinfo,
    check_function=check_dell_sc_sysinfo,
)


snmp_section_dell_sc_sysinfo = SimpleSNMPSection(
    name = "dell_sc_sysinfo",
    parse_function = parse_dell_sc_sysinfo,
    detect = all_of(
        contains(".1.3.6.1.2.1.1.1.0", "compellent"),
        exists(".1.3.6.1.4.1.674.11000.2000.500.1.2.1.0"),
    ),
    fetch = SNMPTree(
      base = '.1.3.6.1.4.1.674.11000.2000.500.1.2',
      oids = [
        '4.0',    # productIDVersion
        '5.0',    # productIDSerialNumber
        '6.0',    # productIDGlobalStatus
        '7.0',    # productIDBuildNumber
      ],
    )
)
