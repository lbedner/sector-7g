"""Load testing: drives any API endpoint (``api``) at a chosen load, and
keeps each run's results and analysis in Redis (``common``).
"""

# Shared code, not a service (``ownership``).
PART_OF = "shared"
