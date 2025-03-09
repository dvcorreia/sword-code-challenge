from __future__ import annotations

from datetime import timedelta

import pytest

from clinical_recommendations.platform.healthcheck.asynchronous import AsyncHealthcheck
from tests.platform.healthcheck.asynchronous import AsyncHealtherMock


@pytest.mark.asyncio
async def test_concurrent_health_check():
    """
    Testing ready and live, they should not take more than the time of the most
    expensive computation.
    Time constrains are not tested due to weak reproducibility of results.
    """

    checker1 = AsyncHealtherMock(
        sleep_time=timedelta(seconds=0.01),
        live_status="not alive",
        ready_status="not ready. waiting for something",
    )

    checker2 = AsyncHealtherMock(
        sleep_time=timedelta(seconds=0.01), live_status=None, ready_status=None
    )

    checker3 = AsyncHealtherMock(
        sleep_time=timedelta(seconds=0.02), live_status=None, ready_status=None
    )

    healthcheck = AsyncHealthcheck()
    healthcheck.add("checker1", checker1)
    healthcheck.add("checker2", checker2)
    healthcheck.add("checker3", checker3)

    r = await healthcheck.ready()

    assert len(r.keys()) == 1
    c = r.get("checker1", None)
    assert c is not None
    assert c.message == checker1.ready_status

    r = await healthcheck.live()

    assert len(r.keys()) == 1
    c = r.get("checker1", None)
    assert c is not None
    assert c.message == checker1.live_status

    # changing live status of checker2. should be seen in the live result
    checker2.live_status = "went unhealthy. ups!"

    r = await healthcheck.live()
    assert len(r.keys()) == 2
    c1 = r.get("checker1", None)
    c2 = r.get("checker2", None)
    assert c1 is not None and c2 is not None
    assert c1.message == checker1.live_status
    assert c2.message == checker2.live_status
