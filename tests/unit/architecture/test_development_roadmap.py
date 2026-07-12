from __future__ import annotations

from pathlib import Path

from property_service.architecture.roadmap import (
    APPROVAL_GATES,
    DEFINITION_OF_DONE,
    DELIVERABLES,
    POST_LAUNCH_ITEMS,
    RISK_REGISTER,
    ROADMAP_PHASES,
    DeliverableStatus,
    PhaseStatus,
)
from property_service.architecture.roadmap_status import evaluate_roadmap, format_roadmap_report

REPO_ROOT = Path(__file__).resolve().parents[3]


class TestRoadmapStructure:
    def test_six_phases_defined(self) -> None:
        assert len(ROADMAP_PHASES) == 6
        assert ROADMAP_PHASES[0].name == "Foundation"
        assert ROADMAP_PHASES[-1].name == "Enterprise & Production"

    def test_deliverables_cover_all_phases(self) -> None:
        phases_with_items = {d.phase for d in DELIVERABLES}
        assert phases_with_items == {1, 2, 3, 4, 5, 6}

    def test_risk_register_matches_doc(self) -> None:
        assert len(RISK_REGISTER) == 6
        assert any("PostGIS" in item.risk for item in RISK_REGISTER)

    def test_post_launch_items(self) -> None:
        assert len(POST_LAUNCH_ITEMS) >= 10
        assert any(item.feature == "Elasticsearch search index" for item in POST_LAUNCH_ITEMS)

    def test_approval_gates(self) -> None:
        assert len(APPROVAL_GATES) == 6
        assert any("sahibinden" in gate.recommendation for gate in APPROVAL_GATES)

    def test_definition_of_done(self) -> None:
        assert len(DEFINITION_OF_DONE) == 8


class TestRoadmapProgress:
    def test_phase_1_mostly_complete(self) -> None:
        report = evaluate_roadmap(REPO_ROOT)
        phase_1 = next(p for p in report.phases if p.phase.number == 1)
        assert phase_1.status in {PhaseStatus.COMPLETE, PhaseStatus.IN_PROGRESS}
        assert phase_1.completed >= 8

    def test_phase_2_core_crud_complete(self) -> None:
        report = evaluate_roadmap(REPO_ROOT)
        phase_2 = next(p for p in report.phases if p.phase.number == 2)
        assert phase_2.completed >= 5

    def test_overall_progress_above_half(self) -> None:
        report = evaluate_roadmap(REPO_ROOT)
        assert report.overall_completion_pct >= 50.0

    def test_pending_items_are_explicit(self) -> None:
        report = evaluate_roadmap(REPO_ROOT)
        phase_6 = next(p for p in report.phases if p.phase.number == 6)
        incomplete_titles = {
            item.deliverable.title
            for item in phase_6.deliverables
            if item.status != DeliverableStatus.COMPLETE
        }
        assert "Read replica support" in incomplete_titles
        assert "finward-api integration" in incomplete_titles

    def test_format_report(self) -> None:
        report = evaluate_roadmap(REPO_ROOT)
        text = format_roadmap_report(report)
        assert "Phase 1: Foundation" in text
        assert "% complete" in text

    def test_consumer_docs_exist(self) -> None:
        assert (REPO_ROOT / "docs/consumers/README.md").exists()
