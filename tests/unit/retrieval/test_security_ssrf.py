"""Tests for SSRF Defense and Network Security Pipeline."""

import pytest

from tathvyn.common.exceptions import SecurityViolationError, SSRFAttemptError
from tathvyn.retrieval.security import is_ip_blocked, validate_url_security


def test_public_urls_allowed() -> None:
    """Verify valid public URLs pass security inspection."""
    assert (
        validate_url_security("https://www.reuters.com/world/article")
        == "https://www.reuters.com/world/article"
    )
    assert (
        validate_url_security("https://en.wikipedia.org/wiki/James_Webb_Space_Telescope")
        == "https://en.wikipedia.org/wiki/James_Webb_Space_Telescope"
    )


def test_blocked_ip_ranges() -> None:
    """Verify private, loopback, and link-local IPs are blocked."""
    assert is_ip_blocked("127.0.0.1") is True
    assert is_ip_blocked("10.0.0.1") is True
    assert is_ip_blocked("192.168.1.1") is True
    assert is_ip_blocked("172.16.0.1") is True
    assert is_ip_blocked("169.254.169.254") is True  # Cloud metadata IP
    assert is_ip_blocked("::1") is True
    assert is_ip_blocked("fe80::1") is True
    assert is_ip_blocked("8.8.8.8") is False  # Public Google DNS


def test_ssrf_attempt_rejections() -> None:
    """Verify SSRFAttemptError is raised on blocked target hosts."""
    # Loopback IP
    with pytest.raises(SSRFAttemptError):
        validate_url_security("http://127.0.0.1:8000/secret")

    # Cloud metadata endpoint
    with pytest.raises(SSRFAttemptError):
        validate_url_security("http://169.254.169.254/latest/meta-data/")

    # Private LAN
    with pytest.raises(SSRFAttemptError):
        validate_url_security("http://192.168.1.50/admin")

    # Localhost hostname
    with pytest.raises(SSRFAttemptError):
        validate_url_security("http://localhost:5432")


def test_invalid_scheme_rejection() -> None:
    """Verify non-HTTP schemes (file, gopher, ftp) raise SecurityViolationError."""
    with pytest.raises(SecurityViolationError):
        validate_url_security("file:///etc/passwd")

    with pytest.raises(SecurityViolationError):
        validate_url_security("ftp://example.org/resource")

    with pytest.raises(SecurityViolationError):
        validate_url_security("gopher://evil.com")
