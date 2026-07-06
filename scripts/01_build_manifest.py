from __future__ import annotations

import argparse

from src.data.manifest_builder import build_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build experiment manifest for DRIVE, STARE, and CHASEDB1.")
    parser.add_argument("--working-root", required=True, help="Working PNG dataset root.")
    parser.add_argument("--output", default="data/manifests/manifest.csv", help="Output manifest CSV.")
    parser.add_argument("--stare-observer", default="ah", choices=["ah", "vk"], help="Preferred STARE observer.")
    parser.add_argument("--chasedb1-observer", default="1stHO", choices=["1stHO", "2ndHO"], help="CHASEDB1 observer.")
    args = parser.parse_args()

    df = build_manifest(
        args.working_root,
        args.output,
        stare_observer=args.stare_observer,
        chasedb1_observer=args.chasedb1_observer,
    )

    print(f"Manifest saved to: {args.output}")
    print(f"Rows: {len(df)}")
    if len(df) > 0:
        print(df.groupby("dataset").size())


if __name__ == "__main__":
    main()
