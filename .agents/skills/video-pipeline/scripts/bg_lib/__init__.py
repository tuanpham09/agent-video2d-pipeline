# -*- coding: utf-8 -*-
"""REGISTRY: id → {name, kind, draw(), tags, focus}. Mỗi module batch_*.py đăng ký thêm bối cảnh."""
from __future__ import annotations

REGISTRY: dict[str, dict] = {}


def register(bid: str, name: str, kind: str, tags: list[str], focus=(960, 700), **extra):
    def deco(fn):
        REGISTRY[bid] = dict(name=name, kind=kind, tags=tags, focus=list(focus), draw=fn, **extra)
        return fn
    return deco


from . import batch1  # noqa: E402,F401
