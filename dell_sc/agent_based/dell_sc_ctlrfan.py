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


from cmk.plugins.lib.fan import check_fan

from cmk.agent_based.v2 import (
    CheckPlugin,
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


def item_dell_sc_ctlrfan(line):
    ctlr, fan = line[0].split('.')
    return "Ctlr %s Fan %s" % (ctlr, fan)

def parse_dell_sc_ctlrfan(string_table):
    return string_table

def discover_dell_sc_ctlrfan(section):
    for line in section:
        name = item_dell_sc_ctlrfan(line)
        yield Service(item=name)

def check_dell_sc_ctlrfan(item, params, section):
    state = {
        1  : ('up', State.OK),
        2  : ('down', State.CRIT),
        3  : ('degraded', State.WARN),
    }
    for line in section:
        if item_dell_sc_ctlrfan(line) == item:
            ctlrfan_state = state.get(int(line[1]), ('unknown', State.UNKNOWN))
            rpm = int(line[3] or 0)
            norm_max   = int(line[4]) if line[4] else None
            norm_min   = int(line[5]) if line[5] else None
            warn_lower = int(line[6]) if line[6] else None
            warn_upper = int(line[7]) if line[7] else None
            crit_lower = int(line[8]) if line[8] else None
            crit_upper = int(line[9]) if line[9] else None

            params_local = dict(params)
            if "lower" not in params and (warn_lower is not None and crit_lower is not None):
                params_local["lower"] = (warn_lower, crit_lower)
            if "upper" not in params and (warn_upper is not None and crit_upper is not None):
                params_local["upper"] = (warn_upper, crit_upper)

            yield from check_fan(rpm, params_local)
            if norm_max is not None and norm_min is not None:
                yield Result(state=State.OK, summary="Range: %d/%d" % (norm_min, norm_max))
            yield Result(state=ctlrfan_state[1], summary="State is %s" % ctlrfan_state[0])


check_plugin_dell_sc_ctlrfan = CheckPlugin(
    name="dell_sc_ctlrfan",
    sections = [ "dell_sc_ctlrfan" ],
    service_name="Dell SC %s",
    discovery_function=discover_dell_sc_ctlrfan,
    check_function=check_dell_sc_ctlrfan,
    check_default_parameters={
        "output_metrics": True
    },
    check_ruleset_name="hw_fans",
)


snmp_section_dell_sc_ctlrfan = SimpleSNMPSection(
    name = "dell_sc_ctlrfan",
    parse_function = parse_dell_sc_ctlrfan,
    detect = all_of(
        contains(".1.3.6.1.2.1.1.1.0", "compellent"),
        exists(".1.3.6.1.4.1.674.11000.2000.500.1.2.1.0"),
    ),
    fetch = SNMPTree(
      base = '.1.3.6.1.4.1.674.11000.2000.500.1.2.16.1',
      oids = [
        OIDEnd(),    # scCtlrFanNbr
        '3',         # scCtlrFanStatus
        '4',         # scCtlrFanName
        '5',         # scCtlrFanCurrentRpm
        '6',         # scCtlrFanNormMaxRpm
        '7',         # scCtlrFanNormMinRpm
        '8',         # scCtlrFanWarnLwrRpm
        '9',         # scCtlrFanWarnUprRpm
        '10',        # scCtlrFanCritLwrRpm
        '11',        # scCtlrFanCritUprRpm
      ],
    )
)
