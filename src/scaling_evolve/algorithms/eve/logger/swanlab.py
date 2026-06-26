"""SwanLab logger for Eve runs."""

from __future__ import annotations

import json
import logging
from typing import Any

from scaling_evolve.algorithms.eve.logger.base import EveLogger
from scaling_evolve.algorithms.eve.populations.entry import PopulationEntry
from scaling_evolve.algorithms.eve.workflow.phase2 import Phase2Result

_LOG = logging.getLogger(__name__)


def _load_swanlab_sdk() -> Any | None:
    try:
        import swanlab
    except ImportError:
        return None
    return swanlab


class SwanLabEveLogger(EveLogger):
    """Logs Eve telemetry directly to SwanLab.

    Constructor parameters mirror :class:`WandbEveLogger` where applicable so
    the two are interchangeable via Hydra config swaps.

    .. note::

        SwanLab does not support ``wandb.Table``.  Phase-2 result tables are
        serialised as JSON strings and logged as text metrics instead.
    """

    def __init__(
        self,
        *,
        run_id: str,
        full_config: dict[str, object],
        enabled: bool = False,
        project: str = "scaling-evolve",
        name: str | None = None,
        description: str | None = None,
        log_dir: str | None = None,
        api_key: str | None = None,
        excluded_score_fields: list[str] | tuple[str, ...],
        **kwargs: Any,
    ) -> None:
        self._sdk: Any | None = None
        self._run: Any | None = None
        self._run_id = run_id
        super().__init__(excluded_score_fields=excluded_score_fields)
        if not enabled:
            return

        sdk = _load_swanlab_sdk()
        if sdk is None:
            _LOG.warning("swanlab not installed; skipping SwanLab logging.")
            return

        if api_key:
            try:
                sdk.login(api_key=api_key)
            except Exception as error:  # noqa: BLE001
                _LOG.warning("SwanLab login failed: %s", error)
                return

        try:
            run = sdk.init(
                project=project,
                name=name or run_id,
                description=description,
                config=full_config,
                log_dir=log_dir,
                **kwargs,
            )
        except Exception as error:  # noqa: BLE001
            _LOG.warning("SwanLab init failed for `%s`: %s", run_id, error)
            return
        if run is None:
            return

        self._sdk = sdk
        self._run = run
        _LOG.info(
            "SwanLab run initialised: project=%s, name=%s",
            project,
            name or run_id,
        )

    def on_iteration(
        self,
        *,
        iteration: int,
        solver_entries: list[PopulationEntry],
        optimizer_entries: list[PopulationEntry],
        phase2_results: list[Phase2Result],
    ) -> None:
        if self._sdk is None or self._run is None:
            return

        payload = self._build_iteration_payload(
            iteration=iteration,
            solver_entries=solver_entries,
            optimizer_entries=optimizer_entries,
            phase2_results=phase2_results,
        )

        # SwanLab has no Table type — serialise result tables as JSON strings
        # so the data is still captured in the dashboard.
        if self.phase2_solver_rows:
            payload["tables/phase2_solvers"] = json.dumps(
                self.phase2_solver_rows, sort_keys=True, default=str
            )
        if self.phase2_optimizer_rows:
            payload["tables/phase2_optimizers"] = json.dumps(
                self.phase2_optimizer_rows, sort_keys=True, default=str
            )

        self._run.log(payload, step=iteration)

    def finish(
        self,
        *,
        solver_entries: list[PopulationEntry],
        optimizer_entries: list[PopulationEntry],
        iterations_completed: int,
    ) -> None:
        if self._sdk is None or self._run is None:
            return

        # SwanLab Run objects do not expose a ``summary`` dict.
        # Log the finish summary as a final step so it is still recorded.
        summary = self._build_finish_summary(
            solver_entries=solver_entries,
            optimizer_entries=optimizer_entries,
            iterations_completed=iterations_completed,
        )
        try:
            self._run.log(
                {f"summary/{k}": v for k, v in summary.items()},
                step=iterations_completed,
            )
        except Exception:  # noqa: BLE001
            _LOG.debug("Could not log SwanLab finish summary.", exc_info=True)

        try:
            self._run.finish()
        except Exception:  # noqa: BLE001
            _LOG.debug("SwanLab finish() raised.", exc_info=True)
