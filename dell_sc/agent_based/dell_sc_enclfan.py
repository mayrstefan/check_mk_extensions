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
    Result,
    SimpleSNMPSection,
    SNMPTree,
    OIDEnd,
    State,
    all_of,
    contains,
    exists,
)


def item_dell_sc_enclfan(line):
    encl, fan = line[0].split('.')
    return "Encl %s Fan %s" % (encl, fan)

def parse_dell_sc_enclfan(string_table):
    state = {
        1  : ('up', State.OK),
        2  : ('down', State.CRIT),
        3  : ('degraded', State.WARN),
    }
    section = {}
    for line in string_table:
        name = item_dell_sc_enclfan(line)
        section[name] = {
            "state": state.get(int(line[1]), ('unknown', State.UNKNOWN)),
            "location": line[2],
            "speed": line[3],
        }
    return section

def discover_dell_sc_enclfan(section) -> DiscoveryResult:
    for name in section.keys():
        yield Service(item=name)

def check_dell_sc_enclfan(item, params, section) -> CheckResult:
    if item in section:
        data = section[item]
        yield Result(state=data["state"][1], summary="%s, Speed is %s, State is %s" % (data["location"], data["speed"], data["state"][0]))


check_plugin_dell_sc_enclfan = CheckPlugin(
    name="dell_sc_enclfan",
    sections = [ "dell_sc_enclfan" ],
    service_name="Dell SC %s",
    discovery_function=discover_dell_sc_enclfan,
    check_function=check_dell_sc_enclfan,
    check_default_parameters={
        'lower' : (1000, 100),
        "output_metrics": True
    },
)


snmp_section_dell_sc_enclfan = SimpleSNMPSection(
    name = "dell_sc_enclfan",
    parse_function = parse_dell_sc_enclfan,
    detect = all_of(
        contains(".1.3.6.1.2.1.1.1.0", "compellent"),
        exists(".1.3.6.1.4.1.674.11000.2000.500.1.2.1.0"),
    ),
    fetch = SNMPTree(
      base = '.1.3.6.1.4.1.674.11000.2000.500.1.2.20.1',
      oids = [
        OIDEnd(),    # encl + fan
        '3',         # scEnclFanStatus
        '4',         # scEnclFanLocation
        '5',         # scEnclFanCurrentS
      ],
    )
)
