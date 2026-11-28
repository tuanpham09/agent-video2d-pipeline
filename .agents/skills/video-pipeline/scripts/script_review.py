#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gói review độc lập cho kịch bản + gộp kết quả (references/script-review-protocol.md).

  packet  --project P [--lens logic|loops|retention] [--with-drama]   → in/ghi gói để đưa cho agent review KHÔNG thấy lập luận của người viết
  merge   --project P                                                   → gộp script/review/<lens>.json thành script/review/REVIEW.md
Gói mặc định "mù": chỉ có bible (nhân vật/địa điểm/đạo cụ), setting/cast, lời thoại. Không có `visual`, `goal`, ghi chú đề xuất,
khối `drama` (để reviewer tự dò setup/payoff rồi mới đối chiếu). `--with-drama` thêm khối drama cho lượt đối chiếu.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LENSES = {
    "logic": "LOGIC & THÔNG TIN: ai biết gì khi nào (nhân vật hành động dựa trên điều chưa được biết?), động cơ có đủ để hành động không "
             "(vì sao không bỏ chạy/không báo ai/không hỏi?), mốc thời gian, đạo cụ/vị trí, luật của siêu nhiên có nhất quán không, "
             "lỗ hổng 'ai cũng ngu cùng lúc'. Ưu tiên phần giữa kịch bản (lỗi nhất quán hay dồn ở giữa).",
    "loops": "GÀI MỞ ĐÓNG: tự liệt kê mọi setup (vật, lời cảnh báo, luật, manh mối) và payoff bạn thấy, KHÔNG đoán theo dữ liệu tác giả. "
             "Tìm: setup không được trả, payoff không có setup (tiết lộ từ trên trời), tiết lộ sớm, twist không có manh mối công bằng, "
             "red herring không được giải thích, chi tiết gài quá lộ hoặc quá ẩn.",
    "retention": "GIỮ CHÂN & NHỊP: 5 câu đầu có hook thật không, đoạn nào dễ thoát (kể lể, lặp ý, giải thích thừa), cuối cảnh có kéo sang cảnh sau không, "
                 "đường căng có leo thang không, midpoint có đổi thế không, cú doạ có bị lặp kiểu, kết có đáng chờ không, câu nào đoán trước được.",
}

SCHEMA_HINT = {
    "lens": "logic|loops|retention",
    "summary": "2–4 câu nhận định chung",
    "findings": [{"severity": "must|should|nice", "scene": "S07", "line": "S07_L08a hoặc null", "category": "logic|motive|timeline|rule|setup|payoff|twist|pacing|hook|style",
                  "issue": "điều sai/yếu, trích câu", "why": "vì sao người xem sẽ thấy", "fix": "cách sửa cụ thể, ngắn"}],
    "extracted_loops": [{"plant": "line id", "payoff": "line id hoặc null", "what": "mô tả"}],
    "not_checked": ["điều bạn không kiểm được"],
}


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def packet(proj: Path, lens: str | None, with_drama: bool) -> str:
    S = load(proj / "script" / "script.json")
    B = load(proj / "script" / "bible.json")
    out = []
    out.append("# GÓI REVIEW KỊCH BẢN\n")
    lenses = [lens] if lens else list(LENSES)
    out.append("## Nhiệm vụ\nBạn là reviewer độc lập. Bạn KHÔNG phải tác giả và không biết ý đồ của tác giả. Đọc toàn bộ lời thoại rồi báo lỗi **bằng chứng cụ thể** "
               "(trích câu + line id). Không khen chung chung. Không viết lại kịch bản. Nếu không chắc là lỗi hay phong cách, đánh `nice`.\n")
    out.append("Phạm vi (lens):\n" + "\n".join(f"- **{k}**: {LENSES[k]}" for k in lenses) + "\n")
    out.append("Mức: `must` = người xem chắc chắn thấy vô lý/hở, phải sửa; `should` = nên sửa; `nice` = cải tiến.\n")
    out.append("Trả về **một file JSON** đúng dạng sau (mỗi lens một file):\n```json\n" + json.dumps(SCHEMA_HINT, ensure_ascii=False, indent=1) + "\n```\n")
    out.append("Quy ước: người kể `host` kể ngôi thứ nhất; `—` là cảnh hồi tưởng/điện thoại khi có `frame`. Tên riêng/giá trị trong ngoặc là đề xuất của tác giả khi có `[đề xuất]`.\n")
    out.append("## Bible\n")
    out.append("Nhân vật: " + "; ".join(f"{c['id']}={c.get('name', '')}" for c in B.get("characters", [])))
    out.append("\nĐịa điểm: " + "; ".join(f"{l['id']} ({l.get('kind', '?')})" for l in B.get("locations", [])))
    out.append("\nĐạo cụ: " + "; ".join(f"{p['id']} {p.get('states', '')}" for p in B.get("props", [])) + "\n")
    if with_drama and S.get("drama"):
        out.append("## Khối drama do tác giả khai (đối chiếu với lời thoại, đừng tin mù)\n```json\n" + json.dumps(S["drama"], ensure_ascii=False, indent=1) + "\n```\n")
    out.append("## Kịch bản\n")
    for s in S["scenes"]:
        st = s.get("setting", {})
        cast = ", ".join(f"{c['id']}({c.get('presence', 'physical')})" for c in s.get("cast", []))
        out.append(f"### {s['id']} {s.get('title', '')}\n[{st.get('location', '?')} {st.get('int_ext', '')} {st.get('time', '')} {st.get('story_time', '')} frame={st.get('frame', '')} link={st.get('link', '')}] cast: {cast}")
        if with_drama and s.get("drama"):
            out.append("drama: " + json.dumps(s["drama"], ensure_ascii=False))
        for ln in s["lines"]:
            out.append(f"{ln['id']} [{ln.get('speaker', '')}] {ln.get('text', '')}")
        out.append("")
    return "\n".join(out)


def merge(proj: Path) -> int:
    d = proj / "script" / "review"
    files = sorted(d.glob("*.json")) if d.exists() else []
    if not files:
        print("chưa có script/review/*.json")
        return 1
    rows, notes, sums, ploops = [], [], [], []
    for f in files:
        try:
            r = load(f)
        except Exception as e:  # noqa: BLE001
            print(f"LỖI đọc {f.name}: {e}")
            return 1
        lens = r.get("lens", f.stem)
        sums.append(f"- **{lens}**: {r.get('summary', '')}")
        for x in r.get("findings", []):
            rows.append({**x, "lens": lens})
        notes += [f"{lens}: {n}" for n in r.get("not_checked", [])]
        ploops += [{**x, "lens": lens} for x in r.get("extracted_loops", [])]
    order = {"must": 0, "should": 1, "nice": 2}
    rows.sort(key=lambda x: (order.get(x.get("severity"), 3), x.get("scene") or "", x.get("line") or ""))
    # gom lỗi trùng: cùng line + category do ≥2 lens/agent → độ tin cậy cao hơn
    key = {}
    for x in rows:
        key.setdefault((x.get("line") or x.get("scene"), x.get("category")), []).append(x["lens"])
    out = ["# REVIEW kịch bản (gộp)\n", *sums, ""]
    cnt = {k: sum(1 for x in rows if x.get("severity") == k) for k in order}
    out.append(f"Tổng: must={cnt['must']}, should={cnt['should']}, nice={cnt['nice']}\n")
    for sev in ("must", "should", "nice"):
        sub = [x for x in rows if x.get("severity") == sev]
        if not sub:
            continue
        out.append(f"## {sev.upper()} ({len(sub)})\n")
        for x in sub:
            who = key[(x.get("line") or x.get("scene"), x.get("category"))]
            dup = f" · {len(who)} reviewer cùng thấy" if len(who) > 1 else ""
            out.append(f"- **{x.get('scene', '?')}/{x.get('line') or '—'}** [{x.get('category')}, {x['lens']}{dup}] {x.get('issue')}\n  - vì sao: {x.get('why')}\n  - sửa: {x.get('fix')}")
        out.append("")
    if ploops:
        out.append("## Setup/payoff do reviewer tự dò\n")
        out += [f"- ({x['lens']}) {x.get('plant')} → {x.get('payoff')}: {x.get('what')}" for x in ploops]
        out.append("")
    if notes:
        out.append("## Reviewer báo CHƯA KIỂM\n" + "\n".join(f"- {n}" for n in notes) + "\n")
    (d / "REVIEW.md").write_text("\n".join(out), encoding="utf-8")
    print(f"đã ghi {d / 'REVIEW.md'}: must={cnt['must']} should={cnt['should']} nice={cnt['nice']}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("packet")
    p.add_argument("--project", required=True)
    p.add_argument("--lens", choices=list(LENSES))
    p.add_argument("--with-drama", action="store_true")
    p.add_argument("--out")
    m = sub.add_parser("merge")
    m.add_argument("--project", required=True)
    a = ap.parse_args()
    proj = Path(a.project)
    if a.cmd == "packet":
        t = packet(proj, a.lens, a.with_drama)
        if a.out:
            Path(a.out).parent.mkdir(parents=True, exist_ok=True)
            Path(a.out).write_text(t, encoding="utf-8")
            print(f"đã ghi {a.out} ({len(t)} ký tự)")
        else:
            print(t)
        return 0
    return merge(proj)


if __name__ == "__main__":
    sys.exit(main())
