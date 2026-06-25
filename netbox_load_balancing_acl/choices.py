# SPDX-License-Identifier: AGPL-3.0-or-later
"""Choice sets for the LB ACL routing model. Values match the HAProxy ACL/action keywords."""

from utilities.choices import ChoiceSet


class LBRoutingMatchTypeChoices(ChoiceSet):
    """How a routing rule matches incoming traffic — the HAProxy ACL criterion.

    The generic tokens (host/sni/path_prefix) carry the OPNsense os-haproxy vocabulary;
    the host_* variants carry the pfSense pkg-haproxy ACL expressions verbatim, so an
    adopted pfSense frontend round-trips the exact `expression` it stores.
    """

    HOST = "host"
    SNI = "sni"
    PATH_PREFIX = "path_prefix"
    # pfSense pkg-haproxy host ACL expression variants
    HOST_STARTS_WITH = "host_starts_with"
    HOST_CONTAINS = "host_contains"
    HOST_MATCHES = "host_matches"
    CHOICES = [
        (HOST, "Host header (hdr(host))", "blue"),
        (SNI, "TLS SNI (req.ssl_sni)", "purple"),
        (PATH_PREFIX, "Path prefix (path_beg)", "green"),
        (HOST_STARTS_WITH, "Host starts with", "cyan"),
        (HOST_CONTAINS, "Host contains", "teal"),
        (HOST_MATCHES, "Host matches (exact)", "indigo"),
    ]


class LBRoutingActionTypeChoices(ChoiceSet):
    """The HAProxy frontend action this rule expresses.

    A frontend's action list is more than host-routing: besides ``use_backend`` (route
    matched traffic to a pool), real frontends carry unconditional header rewrites and a
    scheme/redirect. Modeling each action type natively lets an adopted pfSense frontend
    reproduce its full ``a_actionitems`` array at 0-diff instead of clobbering the
    non-routing actions.
    """

    USE_BACKEND = "use_backend"
    SET_HEADER_REQUEST = "http-request_set-header"
    SET_HEADER_RESPONSE = "http-response_set-header"
    REDIRECT = "http-request_redirect"
    CHOICES = [
        (USE_BACKEND, "Route to backend pool (use_backend)", "blue"),
        (SET_HEADER_REQUEST, "Set request header", "orange"),
        (SET_HEADER_RESPONSE, "Set response header", "yellow"),
        (REDIRECT, "HTTP redirect", "red"),
    ]
