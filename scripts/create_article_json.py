#!/usr/bin/env python3
"""Create a valid starter article.json for the WeChat meeting article skill."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def configure_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def starter_article() -> dict:
    return {
        "theme": "zhengeryanzi",
        "template": "classic",
        "palette": "classic",
        "meta": {
            "title": "第 X 周组会纪要",
            "date": "",
            "group": "",
            "host": "",
            "editor": "",
            "cover_image": "",
            "cover_caption": "",
            "summary": "本次组会围绕英语交流、文献分享、时政交流和自由讨论展开。",
        },
        "sections": {
            "english_exchange": {
                "title": "英语交流",
                "topic": "",
                "intro": "",
                "images": [],
                "speeches": [
                    {
                        "speaker": "",
                        "role": "",
                        "mode": "full_text",
                        "text": "",
                        "source": "",
                    }
                ],
            },
            "literature_sharing": {
                "title": "文献分享",
                "intro": "",
                "images": [],
                "papers": [
                    {
                        "title": "",
                        "authors": "",
                        "venue": "",
                        "doi": "",
                        "presenter": "",
                        "images": [],
                        "background": "",
                        "research_question": "",
                        "methods_data": "",
                        "findings": [],
                        "discussion_value": "",
                        "summary": "",
                        "comments": [
                            {
                                "speaker": "",
                                "text": "",
                                "source": "",
                            }
                        ],
                    }
                ],
            },
            "policy_discussion": {
                "title": "时政交流",
                "topic": "",
                "summary": "",
                "images": [],
                "viewpoints": [
                    {
                        "speaker": "",
                        "text": "",
                        "source": "",
                    }
                ],
            },
            "free_discussion": {
                "title": "自由讨论与会议总结",
                "images": [],
                "items": [
                    {
                        "speaker": "",
                        "text": "",
                        "source": "",
                    }
                ],
                "closing": "",
            },
        },
        "custom_sections": [],
        "assets": {"images": []},
    }


def main() -> None:
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("article.json"))
    args = parser.parse_args()

    args.out.write_text(
        json.dumps(starter_article(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
