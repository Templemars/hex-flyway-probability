from __future__ import annotations

from pathlib import Path


CASE_SPECS = (
    {
        "case_key": "svalbard_spring",
        "population": "svalbard",
        "season": "spring",
        "benchmark_file": "gdf_SS_10.csv",
        "route_prefix": "15_svalbard_spring_full_bounded_dijkstra",
        "eval_prefix": "16_svalbard_spring_full_bounded",
        "interpret_prefix": "17_svalbard_spring_top20",
        "title_label": "Svalbard spring",
        "start_rule": "first_row_of_gdf_SS_10",
        "end_rule": "last_row_of_gdf_SS_10",
    },
    {
        "case_key": "netherlands_spring",
        "population": "netherlands",
        "season": "spring",
        "benchmark_file": "gdf_NS_10.csv",
        "route_prefix": "15_netherlands_spring_full_bounded_dijkstra",
        "eval_prefix": "16_netherlands_spring_full_bounded",
        "interpret_prefix": "17_netherlands_spring_top20",
        "title_label": "Netherlands spring",
        "start_rule": "first_row_of_gdf_NS_10",
        "end_rule": "last_row_of_gdf_NS_10",
    },
    {
        "case_key": "netherlands_autumn",
        "population": "netherlands",
        "season": "autumn",
        "benchmark_file": "gdf_NA_10.csv",
        "route_prefix": "15_netherlands_autumn_full_bounded_dijkstra",
        "eval_prefix": "16_netherlands_autumn_full_bounded",
        "interpret_prefix": "17_netherlands_autumn_top20",
        "title_label": "Netherlands autumn",
        "start_rule": "last_row_of_gdf_NA_10",
        "end_rule": "first_row_of_gdf_NA_10",
        "start_override_cell": "831953fffffffff",
        "start_override_reason": "Nearest valid in-domain H3 substitute for the northern benchmark endpoint, because the direct nearest cell falls outside the ERA5-supported routing domain.",
    },
    {
        "case_key": "svalbard_autumn_afaf",
        "population": "svalbard",
        "season": "autumn",
        "benchmark_file": "gdf_SA_afaf_10.csv",
        "route_prefix": "15_svalbard_autumn_afaf_full_bounded_dijkstra",
        "eval_prefix": "16_svalbard_autumn_afaf_full_bounded",
        "interpret_prefix": "17_svalbard_autumn_afaf_top20",
        "title_label": "Svalbard autumn (afaf)",
        "start_rule": "last_row_of_gdf_SA_afaf_10",
        "end_rule": "first_row_of_gdf_SA_afaf_10",
    },
    {
        "case_key": "svalbard_autumn_amam",
        "population": "svalbard",
        "season": "autumn",
        "benchmark_file": "gdf_SA_amam_10.csv",
        "route_prefix": "15_svalbard_autumn_amam_full_bounded_dijkstra",
        "eval_prefix": "16_svalbard_autumn_amam_full_bounded",
        "interpret_prefix": "17_svalbard_autumn_amam_top20",
        "title_label": "Svalbard autumn (amam)",
        "start_rule": "last_row_of_gdf_SA_amam_10",
        "end_rule": "first_row_of_gdf_SA_amam_10",
    },
)


def build_case_map(project_root: Path) -> dict[str, dict]:
    benchmark_dir = project_root / "data" / "raw" / "benchmark_from_2025"
    case_map: dict[str, dict] = {}
    for spec in CASE_SPECS:
        cfg = dict(spec)
        cfg["benchmark_path"] = benchmark_dir / cfg.pop("benchmark_file")
        case_map[cfg["case_key"]] = cfg
    return case_map
