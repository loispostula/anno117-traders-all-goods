#!/usr/bin/env python3
"""Refresh reference/goods.tsv and tests/fixtures/vanilla_traders.xml from the game files.

Run after a game patch or a new DLC, then run tools/generate.py and the tests.

    python3 tools/rda.py "<game>/maindata/config.rda" config/export/assets.xml <out>
    python3 tools/rda.py "<game>/maindata/config.rda" gui/texts_english.xml <out>
    python3 tools/vanilla.py <out>/config.rda/data/base/config/export/assets.xml \
                             <out>/config.rda/data/base/config/gui/texts_english.xml
"""
import collections
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from generate import TRADERS, TRADE_FEATURE  # noqa: E402

# Goods the game keeps out of NPC hands on purpose and that this mod leaves alone.
EXCLUDED = {
    "145102": "Obsidian: Prophecies of Ash barter currency, no production building",
}


def main(assets_path, texts_path):
    root = ET.parse(assets_path).getroot()
    texts = {t.findtext("LineId"): t.findtext("Text") for t in ET.parse(texts_path).getroot().iter("Text")}

    producers = collections.defaultdict(list)
    products, keep = [], {}
    for asset in root.iter("Asset"):
        values = asset.find("Values")
        if values is None:
            continue
        guid = values.findtext("Standard/GUID")
        for out in values.findall(".//FactoryOutputs/Item/Product"):
            producers[out.text].append(guid)
        if asset.findtext("Template") == "Product":
            products.append((guid, values))
        if guid in TRADERS or guid == TRADE_FEATURE:
            keep[guid] = values

    rows = []
    for guid, values in products:
        p = values.find("Product")
        if (p.findtext("StorageLevel") != "Building" or p.findtext("BasePrice") is None
                or p.find("IsAbstract") is not None or p.find("IsWorkforce") is not None):
            continue
        if guid in EXCLUDED:
            continue
        if not producers[guid]:
            raise SystemExit(f"{guid} {values.findtext('Standard/Name')}: tradeable good without producer, "
                             "decide whether to include it (EXCLUDED)")
        rows.append((int(guid), guid, values.findtext("Standard/Name"),
                     texts.get(values.findtext("Text/OasisId"), ""), p.findtext("BasePrice"),
                     p.findtext("AssociatedRegion") or ""))
    rows.sort()
    with open(ROOT / "reference/goods.tsv", "w", encoding="utf-8") as f:
        f.write("guid\tname\tenglish\tbase_price\tregions\n")
        for _, *cols in rows:
            f.write("\t".join(cols) + "\n")

    missing = (set(TRADERS) | {TRADE_FEATURE}) - set(keep)
    if missing:
        raise SystemExit(f"assets not found in vanilla: {sorted(missing)}")
    out = ET.Element("AssetList")
    for guid in [*TRADERS, TRADE_FEATURE]:
        values = keep[guid]
        a = ET.SubElement(ET.SubElement(out, "Asset"), "Values")
        std = ET.SubElement(a, "Standard")
        ET.SubElement(std, "GUID").text = guid
        ET.SubElement(std, "Name").text = values.findtext("Standard/Name")
        if guid == TRADE_FEATURE:
            a.append(values.find("GenericTradeFeature"))
        else:
            ET.SubElement(a, "Trader").append(values.find("Trader/OfferedGoods"))
    ET.indent(out)
    (ROOT / "tests/fixtures/vanilla_traders.xml").write_text(
        "<!-- Trimmed from vanilla assets.xml (config.rda) by tools/vanilla.py. -->\n"
        + ET.tostring(out, encoding="unicode") + "\n", encoding="utf-8")
    print(f"{len(rows)} goods, {len(TRADERS)} traders")


if __name__ == "__main__":
    main(*sys.argv[1:3])
