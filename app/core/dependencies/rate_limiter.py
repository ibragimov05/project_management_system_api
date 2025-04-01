from fastapi import Depends
from fastapi_limiter.depends import RateLimiter

RATE_LIMITER = [Depends(RateLimiter(times=3, seconds=5))]
