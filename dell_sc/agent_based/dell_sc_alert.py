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
    State,
    all_of,
    contains,
    exists,
)


def parse_dell_sc_alert(string_table):
    section ={'alerts': []}
    state = {
        1  : ('complete', State.OK),
        2  : ('critical', State.CRIT),
        3  : ('degraded', State.WARN),
        4  : ('down', State.CRIT),
        5  : ('emergency', State.CRIT),
        6  : ('inform', State.OK),
        7  : ('okay', State.OK),
        8  : ('unavailable', State.CRIT),
        9  : ('unknown', State.UNKNOWN),
    }
    category = {
        0  : 'connectivity',
        1  : 'disk',
        2  : 'hardware',
        3  : 'storage',
        4  : 'system',
        5  : 'unknown',
    }
    atype = {
        0  : 'alert',
        1  : 'indication',
        2  : 'unknown',
    }

    for nbr, istate, definition, icat, ctime, message, itype, ack, act in string_table:
        if act == "1" and ack == "2":
            alert_state = state.get(int(istate), ('unknown', State.UNKNOWN))
            section['alerts'].append((
                alert_state[1], "%s %s %s on %s: %s" % (
                    alert_state[0],
                    category.get(int(icat), 'unknown'),
                    definition,
                    ctime,
                    message)))
    return section
    
def discover_dell_sc_alert(section) -> DiscoveryResult:
    yield Service()

def check_dell_sc_alert(section) -> CheckResult:
    if section['alerts']:
        for alert in section['alerts']:
            yield Result(state=alert[0], notice=alert[1])
    else:
        yield Result(state=State.OK, summary='No Alerts')
    

check_plugin_dell_sc_alert = CheckPlugin(
    name="dell_sc_alert",
    sections = [ "dell_sc_alert" ],
    service_name="Dell SC Alert",
    discovery_function=discover_dell_sc_alert,
    check_function=check_dell_sc_alert,
)


snmp_section_dell_sc_alert = SimpleSNMPSection(
    name = "dell_sc_alert",
    parse_function = parse_dell_sc_alert,
    detect = all_of(
        contains(".1.3.6.1.2.1.1.1.0", "compellent"),
        exists(".1.3.6.1.4.1.674.11000.2000.500.1.2.1.0"),
    ),
    fetch = SNMPTree(
      base = '.1.3.6.1.4.1.674.11000.2000.500.1.2.46.1',
      oids = [
        '2',    # scAlertNbr
        '3',    # scAlertStatus
        '5',    # scAlertDefinition
        '6',    # scAlertCategory
        '7',    # scAlertCreateTime
        '8',    # scAlertMessage
        '9',    # scAlertType
        '10',   # scAlertAcknowledged
        '11',   # scAlertActive
      ],
    )
)
