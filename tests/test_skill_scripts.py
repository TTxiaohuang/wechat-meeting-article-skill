from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "wechat-meeting-article"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def run_script(script: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SKILL / "scripts" / script), *args],
        cwd=cwd or ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


class SkillScriptTests(unittest.TestCase):
    def test_slug_replaces_quote_like_filename_characters(self) -> None:
        extract = load_module("extract_materials", SKILL / "scripts" / "extract_materials.py")

        value = extract.slug('链"岛"成“陆”：公共数据开放/研究?')

        self.assertNotIn('"', value)
        self.assertNotIn("“", value)
        self.assertNotIn("”", value)
        self.assertNotIn("：", value)
        self.assertNotIn("/", value)
        self.assertIn("链_岛_成_陆_公共数据开放_研究", value)

    def test_draft_article_from_materials_creates_editable_article_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            materials = tmp_path / "extracted_materials"
            materials.mkdir()
            (materials / "英语交流稿子.md").write_text(
                "# 英语交流稿子.docx\n\nJames\n学生\nDue to the pressure of various tasks recently, I feel a bit tired.\n\n"
                "Edward\n学生\nRecently, the main thing I've been is just being financially free.\n",
                encoding="utf-8",
            )
            (materials / "链_岛_成_陆_公共数据开放.md").write_text(
                "# 链\"岛\"成\"陆\"：公共数据开放的技术创新效应研究.pdf\n\n"
                "DOI: 10.19744/j.cnki.11-1235/f.2025.0025\n\n"
                "摘要：本文研究公共数据开放对技术创新的影响。\n",
                encoding="utf-8",
            )

            out = tmp_path / "article.scaffold.json"
            result = run_script("draft_article_from_materials.py", str(materials), "--out", str(out))

            self.assertEqual(result.returncode, 0, result.stderr)
            article = json.loads(out.read_text(encoding="utf-8"))
            self.assertTrue(article["_meta"]["scaffold_generated"])
            self.assertIn("must be expanded", article["_meta"]["warning"])
            speeches = article["sections"]["english_exchange"]["speeches"]
            papers = article["sections"]["literature_sharing"]["papers"]
            self.assertEqual(speeches[0]["speaker"], "James")
            self.assertIn("Due to the pressure", speeches[0]["text"])
            self.assertEqual(papers[0]["doi"], "10.19744/j.cnki.11-1235/f.2025.0025")
            self.assertTrue(papers[0]["title"].startswith("链"))
            self.assertFalse(papers[0]["title"].lower().endswith(".pdf"))

    def test_check_article_json_flags_source_leakage_missing_literature_and_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            article = {
                "meta": {"title": "测试", "summary": "摘要"},
                "_meta": {"scaffold_generated": True},
                "sections": {
                    "english_exchange": {
                        "speeches": [
                            {"speaker": "A", "text": "Short.", "source": "新录音_1_原文.docx"}
                        ]
                    },
                    "literature_sharing": {
                        "papers": [{"title": "Paper", "background": "", "findings": []}]
                    },
                },
            }
            article_path = tmp_path / "article.json"
            article_path.write_text(json.dumps(article, ensure_ascii=False), encoding="utf-8")
            html_path = tmp_path / "article.wechat.html"
            html_path.write_text("<p>新录音_1_原文.docx</p>", encoding="utf-8")

            result = run_script("check_article_json.py", str(article_path), "--html", str(html_path))

            self.assertEqual(result.returncode, 1)
            self.assertIn("scaffold-generated article", result.stdout)
            self.assertIn("visible source filename", result.stdout)
            self.assertIn("missing literature fields", result.stdout)

    def test_check_article_json_flags_suspiciously_short_article(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            article = {
                "meta": {"title": "测试", "summary": "短"},
                "sections": {
                    "english_exchange": {
                        "speeches": [
                            {
                                "speaker": "A",
                                "text": "This is a complete enough English paragraph for the checker to ignore.",
                            },
                            {
                                "speaker": "B",
                                "text": "This is another complete enough English paragraph for the checker to ignore.",
                            },
                        ]
                    },
                    "literature_sharing": {
                        "papers": [
                            {
                                "title": "Paper",
                                "background": "背景",
                                "research_question": "问题",
                                "methods_data": "方法",
                                "findings": ["发现"],
                                "discussion_value": "价值",
                            }
                        ]
                    },
                },
            }
            article_path = tmp_path / "article.json"
            article_path.write_text(json.dumps(article, ensure_ascii=False), encoding="utf-8")

            result = run_script("check_article_json.py", str(article_path), "--min-chars", "800")

            self.assertEqual(result.returncode, 1)
            self.assertIn("article appears too short", result.stdout)

    def test_renderer_uses_less_card_like_literature_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            article = {
                "meta": {"title": "测试", "summary": "导读"},
                "sections": {
                    "literature_sharing": {
                        "papers": [
                            {
                                "title": "Paper",
                                "background": "背景内容",
                                "research_question": "问题内容",
                                "methods_data": "方法内容",
                                "findings": ["发现一"],
                                "discussion_value": "价值内容",
                            }
                        ]
                    }
                },
            }
            article_path = tmp_path / "article.json"
            out_dir = tmp_path / "dist"
            article_path.write_text(json.dumps(article, ensure_ascii=False), encoding="utf-8")

            result = run_script("render_wechat_article.py", str(article_path), "--out", str(out_dir))

            self.assertEqual(result.returncode, 0, result.stderr)
            html = (out_dir / "article.wechat.html").read_text(encoding="utf-8")
            self.assertIn("研究背景", html)
            self.assertLessEqual(html.count("background:#eef7fa"), 1)

    def test_renderer_adds_zhengeryanzi_brand_visuals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            article = {
                "theme": "zhengeryanzi",
                "meta": {"title": "测试组会纪要", "summary": "导读", "host": "谭灵风", "editor": "张三"},
                "sections": {
                    "free_discussion": {
                        "title": "自由讨论与会议总结",
                        "items": [{"speaker": "老师", "text": "本次讨论围绕研究方法展开。"}],
                        "closing": "会议结束。",
                    }
                },
            }
            article_path = tmp_path / "article.json"
            out_dir = tmp_path / "dist"
            article_path.write_text(json.dumps(article, ensure_ascii=False), encoding="utf-8")

            result = run_script("render_wechat_article.py", str(article_path), "--out", str(out_dir))

            self.assertEqual(result.returncode, 0, result.stderr)
            html = (out_dir / "article.wechat.html").read_text(encoding="utf-8")
            self.assertIn("郑而研资", html)
            self.assertIn("data-brand=\"zhengeryanzi\"", html)
            self.assertIn("<svg", html)
            self.assertIn("本期记录由郑而研资整理", html)
            self.assertIn("主持：谭灵风", html)
            self.assertIn("推文编辑：张三", html)
            self.assertNotIn("资产评估学习与组会记录", html)
            self.assertNotIn("以阅读记录讨论，以讨论沉淀研究", html)


if __name__ == "__main__":
    unittest.main()
