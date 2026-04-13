"""
Version tracking (§8.1 — Dr. Segal Guidelines).

Version format: MAJOR.MINOR as a string ("1.00") and as a tuple
  version_info = (major: int, minor: int)

Bump MAJOR for breaking architecture changes; MINOR for features/fixes.
"""

__version__ = "1.00"

version_info: tuple[int, int] = (1, 0)
