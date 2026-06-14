# SPDX-License-Identifier: AGPL-3.0-or-later
"""Choice sets for the LB ACL routing model. Values match the HAProxy ACL match keywords."""

from utilities.choices import ChoiceSet


class LBRoutingMatchTypeChoices(ChoiceSet):
    """How a routing rule matches incoming traffic — the HAProxy ACL criterion."""

    HOST = "host"
    SNI = "sni"
    PATH_PREFIX = "path_prefix"
    CHOICES = [
        (HOST, "Host header (hdr(host))", "blue"),
        (SNI, "TLS SNI (req.ssl_sni)", "purple"),
        (PATH_PREFIX, "Path prefix (path_beg)", "green"),
    ]
