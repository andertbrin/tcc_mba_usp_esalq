import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LINKS_PATH = PROJECT_ROOT / "data" / "links_list.json"
PERIOD_SCORES_PATH = PROJECT_ROOT / "data" / "period_sentiment_scores.csv"
OUTPUT_PATH = PROJECT_ROOT / "TCC_latex" / "generated" / "link_count.tex"


def main() -> None:
    with LINKS_PATH.open(encoding="utf-8") as file:
        link_count = len(json.load(file))

    saved_period_scores = pd.read_csv(PERIOD_SCORES_PATH)
    constant_similarity_cutoff = saved_period_scores["similarity_cutoff"].median()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    formatted_link_count = f"{link_count:,}".replace(",", ".")
    formatted_similarity_cutoff = f"{constant_similarity_cutoff:.2f}".replace(".", ",")
    OUTPUT_PATH.write_text(
        "% Automatically generated. Do not edit.\n"
        f"\\newcommand{{\\LinkCount}}{{{formatted_link_count} }}\n"
        f"\\newcommand{{\\ConstantSimilarityCutoff}}{{{formatted_similarity_cutoff}}}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
