import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LINKS_PATH = PROJECT_ROOT / "data" / "links_list.json"
OUTPUT_PATH = PROJECT_ROOT / "TCC_latex" / "generated" / "link_count.tex"


def main() -> None:
    with LINKS_PATH.open(encoding="utf-8") as file:
        link_count = len(json.load(file))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    formatted_link_count = f"{link_count:,}".replace(",", ".")
    OUTPUT_PATH.write_text(
        "% Automatically generated. Do not edit.\n"
        f"\\newcommand{{\\LinkCount}}{{{formatted_link_count} }}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
