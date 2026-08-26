"""SSRF Defense and Network Security Pipeline.

Protects the document acquisition engine from Server-Side Request Forgery (SSRF)
by validating schemes, resolving DNS, and blocking private, loopback, link-local,
and cloud-provider metadata IP ranges.
"""

import ipaddress
import socket
from urllib.parse import urlparse

from tathvyn.common.exceptions import SecurityViolationError, SSRFAttemptError

# Blocked IPv4 and IPv6 networks (RFC 1918, RFC 3927, Loopback, Multicast, Link-local)
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),  # Carrier-grade NAT
    ipaddress.ip_network("127.0.0.0/8"),  # Loopback
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local / Cloud Metadata (169.254.169.254)
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),  # TEST-NET-1
    ipaddress.ip_network("192.168.0.0/16"),  # Private LAN
    ipaddress.ip_network("198.18.0.0/15"),  # Benchmark testing
    ipaddress.ip_network("198.51.100.0/24"),  # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),  # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),  # Multicast
    ipaddress.ip_network("240.0.0.0/4"),  # Reserved
    ipaddress.ip_network("255.255.255.255/32"),
    # IPv6 blocked ranges
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("::1/128"),  # Loopback
    ipaddress.ip_network("fc00::/7"),  # Unique local
    ipaddress.ip_network("fe80::/10"),  # Link-local
    ipaddress.ip_network("ff00::/8"),  # Multicast
]

# Explicit cloud metadata hostnames
_BLOCKED_HOSTNAMES = {
    "metadata.google.internal",
    "metadata.internal",
    "instance-data",
    "169.254.169.254",
    "localhost",
}


def is_ip_blocked(ip_addr: str) -> bool:
    """Check if an IP address string belongs to any blocked or private CIDR range.

    Returns False if ip_addr is not a parseable IP string (e.g. a domain name).
    """
    try:
        ip_obj = ipaddress.ip_address(ip_addr)
        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_reserved
        ):
            return True
        return any(ip_obj in network for network in _BLOCKED_NETWORKS)
    except ValueError:
        return False


def validate_url_security(url: str) -> str:
    """Validate URL scheme and resolve hostname against SSRF blocklist.

    Args:
        url: The candidate web URL.

    Raises:
        SecurityViolationError: If scheme is not http/https or URL is malformed.
        SSRFAttemptError: If resolved IP belongs to a blocked private/cloud metadata range.

    Returns:
        str: The validated canonical URL.
    """
    if not url or len(url) > 2048:
        raise SecurityViolationError("URL is empty or exceeds maximum length of 2048 characters.")

    parsed = urlparse(url)
    if parsed.scheme.lower() not in ("http", "https"):
        raise SecurityViolationError(
            f"Unsupported URL scheme '{parsed.scheme}'. Only 'http' and 'https' are allowed."
        )

    hostname = parsed.hostname
    if not hostname:
        raise SecurityViolationError(f"Invalid URL '{url}': hostname could not be parsed.")

    # 1. Block known metadata hostnames immediately
    if hostname.lower() in _BLOCKED_HOSTNAMES:
        raise SSRFAttemptError(url=url, resolved_ip=hostname)

    # 2. Check if hostname is a literal blocked IP address
    if is_ip_blocked(hostname):
        raise SSRFAttemptError(url=url, resolved_ip=hostname)

    # 3. DNS Resolution: check all resolved IPs
    try:
        addr_info = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
        for entry in addr_info:
            sockaddr = entry[4]
            ip_str = str(sockaddr[0])
            if is_ip_blocked(ip_str):
                raise SSRFAttemptError(url=url, resolved_ip=ip_str)
    except socket.gaierror as e:
        # DNS resolution failure is handled as a network/security violation
        raise SecurityViolationError(f"DNS resolution failed for hostname '{hostname}': {e}") from e

    return url
