from __future__ import annotations

from time import perf_counter

from django.db import connection
from django.test.utils import CaptureQueriesContext

from capitalism.constants.simulation_step import SimulationStep


class SimulationDayProfilerService:
    """Profile one simulated day by capturing duration and query count per step."""

    def __init__(self, simulation):
        self.simulation = simulation

    def run(self) -> list[dict[str, object]]:
        previous_debug_cursor = connection.force_debug_cursor
        connection.force_debug_cursor = True
        results: list[dict[str, object]] = []
        try:
            for _ in range(len(self.simulation.STEP_SEQUENCE)):
                current_step = SimulationStep(self.simulation.step)
                start_time = perf_counter()
                with CaptureQueriesContext(connection) as queries_context:
                    new_step = self.simulation.finish_current_step()
                duration_milliseconds = (perf_counter() - start_time) * 1000
                results.append(
                    {
                        "step": current_step.value,
                        "duration_milliseconds": duration_milliseconds,
                        "queries": len(queries_context.captured_queries),
                    }
                )
                if new_step == SimulationStep.START_OF_DAY:
                    break
        finally:
            connection.force_debug_cursor = previous_debug_cursor

        return results
