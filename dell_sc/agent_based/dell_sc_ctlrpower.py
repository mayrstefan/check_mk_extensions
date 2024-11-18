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


def item_dell_sc_ctlrpower(line):
    encl, power = line[0].split('.')
    return "Ctlr %s Power %s" % (encl, power)

def parse_dell_sc_ctlrpower(string_table):
    section = {}
    state = {
        1  : ('up', State.OK),
        2  : ('down', State.CRIT),
        3  : ('degraded', State.WARN),
    }
    for line in string_table:
        name = item_dell_sc_ctlrpower(line)
        ctlrpower_state = state.get(int(line[1]), ('unknown', State.UNKNOWN))
        section[name] = {
             'state': ctlrpower_state[1],
             'desc': ctlrpower_state[0],
             'supply': line[2],
        }
    return section

def discover_dell_sc_ctlrpower(section) -> DiscoveryResult:
    for name in section.keys():
        yield Service(item=name)

def check_dell_sc_ctlrpower(item, section) -> CheckResult:
    if item in section:
        yield Result(state=section[item]['state'], summary="State is %s from %s" % (section[item]['desc'], section[item]['supply']))


check_plugin_dell_sc_ctlrpower = CheckPlugin(
    name="dell_sc_ctlrpower",
    sections = [ "dell_sc_ctlrpower" ],
    service_name="Dell SC %s",
    discovery_function=discover_dell_sc_ctlrpower,
    check_function=check_dell_sc_ctlrpower,
)


snmp_section_dell_sc_ctlrpower = SimpleSNMPSection(
    name = "dell_sc_ctlrpower",
    parse_function = parse_dell_sc_ctlrpower,
    detect = all_of(
        contains(".1.3.6.1.2.1.1.1.0", "compellent"),
        exists(".1.3.6.1.4.1.674.11000.2000.500.1.2.1.0"),
    ),
    fetch = SNMPTree(
      base = '.1.3.6.1.4.1.674.11000.2000.500.1.2.17.1',
      oids = [
            OIDEnd(),    # scCtlrPowerNbr
            '3',    # scCtlrPowerStatus
            '4',    # scCtlrPowerName
      ],
    )
)
