from typing import Any

from fastapi import Depends
from fastapi_limiter.depends import RateLimiter

RATE_LIMITER: list[Any] = [Depends(RateLimiter(times=3, seconds=5))]
