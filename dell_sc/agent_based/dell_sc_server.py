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
    CheckResult,
    DiscoveryResult,
    Service,
    Metric,
    Result,
    SimpleSNMPSection,
    SNMPTree,
    State,
    all_of,
    contains,
    exists,
)


def parse_dell_sc_server(string_table):
    state = {
        1  : ('up', State.OK),
        2  : ('down', State.CRIT),
        3  : ('degraded', State.WARN),
    }
    conn = {
        1  : 'up',
        2  : 'down',
        3  : 'partial',
    }
    section = {}
    for line in string_table:
        name=line[0]
        section[name] = {
            "state": state.get(int(line[1]), ('unknown', State.UNKNOWN)),
            "name": line[2],
            "conn": conn.get(int(line[3]), line[3]),
            "paths": int(line[4]),
        }
    return section

def discover_dell_sc_server(section) -> DiscoveryResult:
    for name in section.keys():
        yield Service(item=name)

def check_dell_sc_server(item, section) -> CheckResult:
    if item in section:
        data = section[item]
        yield Result(
            state=data["state"][1],
            summary="%s, Number of Paths: %d, Connectivity %s, State is %s" % (
                data["name"],
                data["paths"],
                data["conn"],
                data["state"][0])
            )


check_plugin_dell_sc_server = CheckPlugin(
    name="dell_sc_server",
    sections = [ "dell_sc_server" ],
    service_name="Dell SC Server %s",
    discovery_function=discover_dell_sc_server,
    check_function=check_dell_sc_server,
)


snmp_section_dell_sc_server = SimpleSNMPSection(
    name = "dell_sc_server",
    parse_function = parse_dell_sc_server,
    detect = all_of(
        contains(".1.3.6.1.2.1.1.1.0", "compellent"),
        exists(".1.3.6.1.4.1.674.11000.2000.500.1.2.1.0"),
    ),
    fetch = SNMPTree(
      base = '.1.3.6.1.4.1.674.11000.2000.500.1.2.27.1',
      oids = [
        '2',    # scServerNbr
        '3',    # scServerStatus
        '4',    # scServerName
        '5',    # scServerCnctvy
        '6',    # scServerPathCount
      ],
    )
)
