#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

#
# (c) 2013 Heinlein Support GmbH
#          Robert Sander <r.sander@heinlein-support.de>
#

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  This file is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from cmk.rulesets.v1 import Help, Label, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    FixedValue,
    InputHint,
    Integer,
    LevelDirection,
    ServiceState,
    SimpleLevels,
    SingleChoice,
    SingleChoiceElement,
    String,
    TimeMagnitude,
    TimeSpan,
)
from cmk.rulesets.v1.rule_specs import ActiveCheck, Topic

_DAY = 24.0 * 3600.0

def _valuespec_service_desc() -> String:
    return String(
                title = Title("Service Description"),
                prefill = DefaultValue("IMAP"),
            )

def _valuespec_settings() -> Dictionary:
    return Dictionary(
        title = Title("Optional Values"),
        elements = {
            "port": DictElement(
                parameter_form=Integer(
                    title = Title("Port number"),
                    # minvalue = 1,
                    # maxvalue = 65535,
                    prefill = DefaultValue(143),
                )),
            "ip_version": DictElement(
                parameter_form=SingleChoice(
                    title = Title("IP-Version"),
                    elements = [
                        SingleChoiceElement(
                            name="ipv4",
                            title = Title("IPv4"),
                        ),
                        SingleChoiceElement(
                            name="ipv6",
                            title = Title("IPv6"),
                        ),
                    ],
                )),
            "send": DictElement(
                parameter_form=String(
                    title = Title("String to send to the server"),
                )),
            "expect": DictElement(
                parameter_form=String(
                    title = Title("String to expect in server response"),
                )),
            "quit": DictElement(
                parameter_form=String(
                    title = Title("String to send server to initiate a clean close of the connection"),
                )),
            "refuse": DictElement(
                parameter_form=ServiceState(
                    title = Title("Accept TCP refusals with states ok, warn, crit"),
                    prefill = DefaultValue(ServiceState.CRIT),
                )),
            "mismatch": DictElement(
                parameter_form=ServiceState(
                    title = Title("Accept expected string mismatches with states ok, warn, crit"),
                    prefill = DefaultValue(ServiceState.WARN),
                )),
            "jail": DictElement(
                parameter_form=FixedValue(
                    value="jail",
                    title = Title("Hide output from TCP socket"),
                )),
            "maxbytes": DictElement(
                parameter_form=Integer(
                    title = Title("Close connection once more than this number of bytes are received"),
                )),
            "delay": DictElement(
                parameter_form=Integer(
                    title = Title("Seconds to wait between sending string and polling for response"),
                )),
            "ssl": DictElement(
                parameter_form=FixedValue (
                    value="ssl",
                    title = Title("Use SSL for the connection"),
                )),
            "certificate_age": DictElement(
                parameter_form=SimpleLevels[float](
                    title = Title("Minimum number of days a certificate has to be valid."),
                    form_spec_template=TimeSpan(displayed_magnitudes=[TimeMagnitude.DAY]),
                    level_direction=LevelDirection.LOWER,
                    prefill_fixed_levels=InputHint((90.0 * _DAY, 60 * _DAY)),
                )),
            "warning": DictElement(
                parameter_form=Integer(
                    title = Title("Response time to result in warning status"),
                    unit_symbol = "sec",
                    prefill = DefaultValue(10),
                )),
            "critical": DictElement(
                parameter_form=Integer(
                    title = Title("Response time to result in critical status"),
                    unit_symbol = "sec",
                    prefill = DefaultValue(15),
                )),
            "timeout": DictElement(
                parameter_form=Integer(
                    title = Title("Seconds before connection times out"),
                    unit_symbol = "sec",
                    prefill = DefaultValue(10),
            )),
        },
      ),

def _form_active_checks_imap() -> Dictionary:
    return Dictionary(
        elements={
            "service_desc": DictElement(
                parameter_form=_valuespec_service_desc(),
                required=True,
            ),
            "hostname": DictElement(
                required=True,
                parameter_form=String(
                    title = Title("DNS Hostname or IP address"),
                    prefill = DefaultValue("$HOSTADDRESS$"),
            )),
            "settings": DictElement(
                parameter_form=_valuespec_settings(),
                required=True,
            ),
        },
    )

rule_spec_imap = ActiveCheck(
    title=Title("Check IMAP"),
    topic=Topic.NETWORKING,
    name="imap",
    parameter_form=_form_active_checks_imap,
)