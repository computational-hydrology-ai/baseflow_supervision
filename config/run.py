#!/usr/bin/env python3

from __future__ import annotations

import argparse
import multiprocessing
import subprocess
from pathlib import Path
from typing import List


# =============================================================================
# PATHS
# =============================================================================

DPL_ROOT = Path(
    "/home/s0shar47/scratch/salil/DPL/CASES"
)

ENTRY_SCRIPT = "main_hydro_temp.py"


# =============================================================================
# WORKER FUNCTION
# =============================================================================

def run_case(case_path: Path) -> tuple[str, bool, str]:
    """
    Changes directory to the case folder and runs the entry point script.
    """
    case_name = str(case_path.relative_to(DPL_ROOT))
    script_path = case_path / ENTRY_SCRIPT

    if not script_path.is_file():
        return case_name, False, f"Missing entry script: {script_path}"

    try:
        # Run the model script inside the target case directory
        result = subprocess.run(
            ["python3", ENTRY_SCRIPT],
            cwd=case_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return case_name, True, result.stdout
    except subprocess.CalledProcessError as e:
        error_msg = f"Exit code {e.returncode}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        return case_name, False, error_msg
    except Exception as e:
        return case_name, False, str(e)


# =============================================================================
# DISCOVERY & SELECTION
# =============================================================================

def discover_cases(
    methods: List[str] | None,
    hydros: List[str] | None,
    losses: List[str] | None,
    weights: List[str] | None,
) -> List[Path]:
    """
    Traverse DPL_ROOT to find cases matching the optional selection filters.
    Structure: method/hydro/loss/weight
    """
    matched_cases = []

    if not DPL_ROOT.is_dir():
        print(f"ERROR: Cases root directory not found: {DPL_ROOT}")
        return matched_cases

    for method_dir in DPL_ROOT.iterdir():
        if not method_dir.is_dir():
            continue
        if methods and method_dir.name not in methods:
            continue

        for hydro_dir in method_dir.iterdir():
            if not hydro_dir.is_dir():
                continue
            if hydros and hydro_dir.name not in hydros:
                continue

            for loss_dir in hydro_dir.iterdir():
                if not loss_dir.is_dir():
                    continue
                if losses and loss_dir.name not in losses:
                    continue

                for weight_dir in loss_dir.iterdir():
                    if not weight_dir.is_dir():
                        continue
                    if weights and weight_dir.name not in weights:
                        continue

                    # Verify if entry script exists here
                    if (weight_dir / ENTRY_SCRIPT).is_file():
                        matched_cases.append(weight_dir)

    return sorted(matched_cases)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run selected DPL experiment cases in parallel."
    )

    parser.add_argument(
        "--methods",
        nargs="+",
        help="Filter by baseflow methods (e.g., Eckhardt Furey)",
    )
    parser.add_argument(
        "--hydros",
        nargs="+",
        help="Filter by hydro models (e.g., HBV marrmot_PRMS)",
    )
    parser.add_argument(
        "--losses",
        nargs="+",
        help="Filter by loss functions",
    )
    parser.add_argument(
        "--weights",
        nargs="+",
        help="Filter by weight tags (e.g., 5050 7525)",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=4,
        help="Number of parallel processes to run simultaneously (default: 4)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List matching cases that would be executed without running them.",
    )

    args = parser.parse_args()

    # Discover cases based on filters
    cases = discover_cases(
        methods=args.methods,
        hydros=args.hydros,
        losses=args.losses,
        weights=args.weights,
    )

    print("=" * 90)
    print("DPL PARALLEL CASE RUNNER")
    print("=" * 90)
    print(f"Found {len(cases)} matching cases to run.")

    if not cases:
        print("No cases matched your criteria. Exiting.")
        return 0

    if args.dry_run:
        print("\n[DRY RUN] Matched cases:")
        for c in cases:
            print(f"  - {c.relative_to(DPL_ROOT)}")
        print("=" * 90)
        return 0

    print(f"Executing with max parallel jobs = {args.jobs}\n")
    print("=" * 90)

    success_count = 0
    fail_count = 0

    # Run in parallel using multiprocessing Pool
    with multiprocessing.Pool(processes=args.jobs) as pool:
        results = pool.imap_unordered(run_case, cases)

        for i, (case_name, success, message) in enumerate(results, 1): # type: ignore
            status = "SUCCESS" if success else "FAILED"
            print(f"[{i:03d}/{len(cases):03d}] {case_name} -> {status}")

            if success:
                success_count += 1
            else:
                fail_count += 1
                print(f"\n--- Error Output for {case_name} ---\n{message}\n-----------------------------------\n")

    print("=" * 90)
    print(f"EXECUTION COMPLETE: {success_count} succeeded, {fail_count} failed.")
    print("=" * 90)

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())