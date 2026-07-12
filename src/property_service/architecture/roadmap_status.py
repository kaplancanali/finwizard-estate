from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from property_service.architecture.roadmap import (
    DELIVERABLES,
    ROADMAP_PHASES,
    DeliverableStatus,
    PhaseStatus,
    RoadmapDeliverable,
    RoadmapPhase,
)

@dataclass
class DeliverableReport:
    deliverable: RoadmapDeliverable
    status: DeliverableStatus
    missing: list[str]


@dataclass
class PhaseReport:
    phase: RoadmapPhase
    status: PhaseStatus
    completed: int
    partial: int
    pending: int
    deliverables: list[DeliverableReport]


@dataclass
class RoadmapReport:
    phases: list[PhaseReport]
    overall_completion_pct: float


def evaluate_roadmap(repo_root: Path | None = None) -> RoadmapReport:
    root = repo_root or _default_repo_root()
    route_index = _load_route_index(root)
    phase_reports: list[PhaseReport] = []

    for phase in ROADMAP_PHASES:
        items = [d for d in DELIVERABLES if d.phase == phase.number]
        reports = [_evaluate_deliverable(root, item, route_index) for item in items]
        completed = sum(1 for r in reports if r.status == DeliverableStatus.COMPLETE)
        partial = sum(1 for r in reports if r.status == DeliverableStatus.PARTIAL)
        pending = sum(1 for r in reports if r.status == DeliverableStatus.PENDING)
        phase_reports.append(
            PhaseReport(
                phase=phase,
                status=_phase_status(completed, partial, pending, len(reports)),
                completed=completed,
                partial=partial,
                pending=pending,
                deliverables=reports,
            )
        )

    total = len(DELIVERABLES)
    done = sum(r.completed + 0.5 * r.partial for r in phase_reports)
    return RoadmapReport(
        phases=phase_reports,
        overall_completion_pct=round((done / total) * 100, 1) if total else 0.0,
    )


def format_roadmap_report(report: RoadmapReport) -> str:
    lines = [f"Property Service Roadmap — {report.overall_completion_pct}% complete", ""]
    for phase_report in report.phases:
        phase = phase_report.phase
        lines.append(
            f"Phase {phase.number}: {phase.name} ({phase.weeks}) — {phase_report.status.value} "
            f"[{phase_report.completed} done, {phase_report.partial} partial, {phase_report.pending} pending]"
        )
        for item in phase_report.deliverables:
            if item.status != DeliverableStatus.COMPLETE:
                suffix = f" — missing: {', '.join(item.missing)}" if item.missing else ""
                note = f" ({item.deliverable.notes})" if item.deliverable.notes else ""
                lines.append(f"  - [{item.status.value}] {item.deliverable.title}{note}{suffix}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _evaluate_deliverable(
    root: Path,
    deliverable: RoadmapDeliverable,
    route_index: str,
) -> DeliverableReport:
    if deliverable.notes and deliverable.notes.startswith("Not implemented"):
        return DeliverableReport(deliverable, DeliverableStatus.PENDING, ["not implemented"])

    missing: list[str] = []
    checks = 0
    passed = 0

    for artifact in deliverable.artifact_checks:
        checks += 1
        path = root / artifact
        if path.exists():
            passed += 1
        else:
            missing.append(artifact)

    for pattern in deliverable.source_checks:
        checks += 1
        if pattern in route_index:
            passed += 1
        else:
            missing.append(pattern)

    for pattern in deliverable.test_globs:
        checks += 1
        if _glob_exists(root, pattern):
            passed += 1
        else:
            missing.append(pattern)

    if checks == 0:
        if deliverable.notes:
            return DeliverableReport(deliverable, DeliverableStatus.PARTIAL, [deliverable.notes])
        return DeliverableReport(deliverable, DeliverableStatus.PENDING, ["no checks defined"])

    if passed == checks:
        return DeliverableReport(deliverable, DeliverableStatus.COMPLETE, [])
    if passed > 0:
        return DeliverableReport(deliverable, DeliverableStatus.PARTIAL, missing)
    return DeliverableReport(deliverable, DeliverableStatus.PENDING, missing)


def _phase_status(completed: int, partial: int, pending: int, total: int) -> PhaseStatus:
    if total == 0:
        return PhaseStatus.PENDING
    if completed == total:
        return PhaseStatus.COMPLETE
    if completed + partial > 0:
        return PhaseStatus.IN_PROGRESS
    return PhaseStatus.PENDING


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_route_index(root: Path) -> str:
    presentation_root = root / "src/property_service/presentation"
    main_py = root / "src/property_service/main.py"
    chunks: list[str] = []
    if presentation_root.exists():
        for path in presentation_root.rglob("*.py"):
            chunks.append(path.read_text(encoding="utf-8"))
    if main_py.exists():
        chunks.append(main_py.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def _route_registered(root: Path, route: str) -> bool:
    return route in _load_route_index(root)


def _glob_exists(root: Path, pattern: str) -> bool:
    return any(root.glob(pattern))
