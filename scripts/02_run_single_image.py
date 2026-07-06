from __future__ import annotations

import argparse
from pprint import pprint

from src.pipeline.run_pipeline import run_single_image


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CA-APSRG pipeline on one image.")
    parser.add_argument("--image", required=True, help="Fundus image path.")
    parser.add_argument("--mask", default="", help="Ground truth vessel mask path.")
    parser.add_argument("--fov", default="", help="FoV mask path.")
    parser.add_argument("--output-dir", default="outputs/single_test", help="Output directory.")
    parser.add_argument("--dataset", default="", help="Dataset name.")
    parser.add_argument("--image-id", default="", help="Image ID.")
    parser.add_argument("--no-always-refine", action="store_true", help="Only refine if false-positive indication exists.")
    args = parser.parse_args()

    result = run_single_image(
        image_path=args.image,
        mask_path=args.mask or None,
        fov_path=args.fov or None,
        output_dir=args.output_dir,
        dataset=args.dataset,
        image_id=args.image_id or None,
        always_refine=not args.no_always_refine,
    )
    pprint(result)


if __name__ == "__main__":
    main()
