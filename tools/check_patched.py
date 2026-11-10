#!/usr/bin/env python3
"""Check an assets.xml patched by the mod loader's xmltest (see README, "Check against the game data").

    python3 tools/check_patched.py <vanilla assets.xml> <patched assets.xml> [--with-mod-goods]

--with-mod-goods: the patched file was made with the MOD_GOODS mods active (see README).
"""
import collections
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from generate import MOD_GOODS, TRADERS, TRADE_FEATURE, UNBLOCKED, goods  # noqa: E402


def wanted(path):
    want = set(TRADERS) | {TRADE_FEATURE}
    found = {}
    for _, el in ET.iterparse(path):
        if el.tag == "Asset":
            guid = el.findtext("Values/Standard/GUID")
            if guid in want:
                found[guid] = el.find("Values")
            else:
                el.clear()
    return found


def tiers(values):
    return [[(i.findtext("Good"), i.findtext("ProductionPerMinute"), i.findtext("Limit"))
             for i in tier.findall("Goods/Item")]
            for tier in values.findall("Trader/OfferedGoods/Item")]


def main(vanilla_path, patched_path, with_mod_goods=False):
    all_goods = [g for g, *_ in goods()]
    mod_goods = [g for items in MOD_GOODS.values() for g, _ in items]
    if with_mod_goods:
        all_goods += mod_goods
    vanilla, patched = wanted(vanilla_path), wanted(patched_path)
    errors = []
    for guid, label in TRADERS.items():
        v, p = tiers(vanilla[guid]), tiers(patched[guid])
        if len(v) != len(p):
            errors.append(f"{label}: {len(v)} tiers before, {len(p)} after")
        for n, (vt, pt) in enumerate(zip(v, p)):
            counts = collections.Counter(g for g, *_ in pt)
            missing = [g for g in all_goods if not counts[g]]
            unexpected = [g for g in mod_goods if counts[g]] if not with_mod_goods else []
            if unexpected:
                errors.append(f"{label} tier {n}: mod goods without the mod: {unexpected}")
            dupes = [g for g, c in counts.items() if c > 1]
            if missing or dupes:
                errors.append(f"{label} tier {n}: missing {missing}, duplicated {dupes}")
            if pt[:len(vt)] != vt:
                errors.append(f"{label} tier {n}: vanilla entries changed")
        print(f"{label}: {len(p)} tiers, {min(len(t) for t in p)}-{max(len(t) for t in p)} goods per tier")
    left = [i.findtext("Good") for i in
            patched[TRADE_FEATURE].findall("GenericTradeFeature/UnsellableGoodsByNonPlayerCharacters/Item")]
    if set(left) & set(UNBLOCKED):
        errors.append(f"still unsellable: {left}")
    print(f"UnsellableGoodsByNonPlayerCharacters: {left}")
    for e in errors:
        print("ERROR", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3], with_mod_goods="--with-mod-goods" in sys.argv))
