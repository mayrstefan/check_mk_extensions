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


def parse_dell_sc_volume(string_table):
    return string_table

def discover_dell_sc_volume(section):
    for line in section:
        name = line[0]
        yield Service(item=name)

def check_dell_sc_volume(item, section):
    state = {
        1  : ('up', State.OK),
        2  : ('down', State.CRIT),
        3  : ('degraded', State.WARN),
    }
    for line in section:
        if line[0] == item:
            volume_state = state.get(int(line[1]), ('unknown', State.UNKNOWN))
            yield Result(state=volume_state[1], summary="%s, State is %s" % (line[2],volume_state[0]))


check_plugin_dell_sc_volume = CheckPlugin(
    name="dell_sc_volume",
    sections = [ "dell_sc_volume" ],
    service_name="Dell SC Volume %s",
    discovery_function=discover_dell_sc_volume,
    check_function=check_dell_sc_volume,
)


snmp_section_dell_sc_volume = SimpleSNMPSection(
    name = "dell_sc_volume",
    parse_function = parse_dell_sc_volume,
    detect = all_of(
        contains(".1.3.6.1.2.1.1.1.0", "compellent"),
        exists(".1.3.6.1.4.1.674.11000.2000.500.1.2.1.0"),
    ),
    fetch = SNMPTree(
      base = '.1.3.6.1.4.1.674.11000.2000.500.1.2.26.1',
      oids = [
        '2',    # scVolumeNbr
        '3',    # scVolumeStatus
        '4',    # scVolumeName
      ],
    )
)
