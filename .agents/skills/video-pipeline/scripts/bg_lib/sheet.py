# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def render_sheet(out: Path, items: list[dict]) -> None:
    """Contact sheet: mỗi bối cảnh 1 ô (ánh sáng mặc định) + lineup theo trạng thái ánh sáng của vài cảnh."""
    from playwright.sync_api import sync_playwright

    sheets = out / "sheets"
    sheets.mkdir(exist_ok=True)
    cells = "".join(
        f'<figure><img src="../{it["file"]}" width="440" height="248"><figcaption>{it["name"]} · {it["id"]}</figcaption></figure>'
        for it in items
    )
    html = (f'<!doctype html><meta charset="utf-8"><style>body{{margin:0;padding:16px;background:#221a14;color:#eadfce;font:13px system-ui;width:1400px}}'
            f'.g{{display:grid;grid-template-columns:repeat(3,440px);gap:14px}}figure{{margin:0}}figcaption{{margin-top:4px}}img{{display:block;border-radius:6px}}</style>'
            f'<div class="g">{cells}</div>')
    hp = sheets / "index.html"
    hp.write_text(html, encoding="utf-8")
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1432, "height": 800})
        pg.goto(hp.resolve().as_uri())
        pg.wait_for_load_state("load"); pg.wait_for_timeout(1500)
        pg.screenshot(path=str(sheets / "contact.png"), full_page=True)
        b.close()
    hp.unlink()
