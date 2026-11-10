"""Static checks and a patch simulation on a trimmed copy of the vanilla traders.

They prove the files are consistent; they do not prove the game shows the goods. The patch was
also run through the mod loader's own xmltest on the full vanilla assets.xml (README).
"""
import collections
import copy
import json
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOD = ROOT / "mod"
ASSETS = MOD / "data/base/config/export/assets.xml"
FIXTURE = ROOT / "tests/fixtures/vanilla_traders.xml"
sys.path.insert(0, str(ROOT / "tools"))
import generate  # noqa: E402
import package  # noqa: E402

ADD_PATH = re.compile(r"^Trader/OfferedGoods/Item/Goods\[not\(Item/Good='(\d+)'\)\]$")
REMOVE_PATH = re.compile(r"^GenericTradeFeature/UnsellableGoodsByNonPlayerCharacters/Item\[Good='(\d+)'\]$")
GOODS = [g for g, *_ in generate.goods()]
CIO = "celtic-independence-overhaul-jtmzac"
CIO_GOODS = [g for g, _ in generate.MOD_GOODS[CIO]]


def values(doc, guid):
    return next(v for v in doc.iter("Values") if v.findtext("Standard/GUID") == guid)


def modops(root, active_mods=None):
    """ModOps in file order. active_mods=None returns all of them; a set applies #mod-id conditions."""
    for el in root:
        if el.tag == "Group":
            cond = el.get("Condition", "")
            if active_mods is not None and cond.startswith("#") and cond[1:] not in active_mods:
                continue
            yield from modops(el, active_mods)
        elif el.tag == "ModOp":
            yield el


def apply(doc, root, active_mods=frozenset()):
    """Apply the two ModOp shapes this mod uses, like the loader does: to every matching node."""
    for op in modops(root, active_mods):
        v = values(doc, op.get("GUID"))
        if "Add" in op.attrib:
            good = ADD_PATH.match(op.get("Add")).group(1)
            for goods in v.findall("Trader/OfferedGoods/Item/Goods"):
                if not any(i.findtext("Good") == good for i in goods.findall("Item")):
                    goods.extend(copy.deepcopy(list(op)))
        elif "Remove" in op.attrib:
            good = REMOVE_PATH.match(op.get("Remove")).group(1)
            parent = v.find("GenericTradeFeature/UnsellableGoodsByNonPlayerCharacters")
            for item in [i for i in parent if i.findtext("Good") == good]:
                parent.remove(item)
        else:
            raise AssertionError(f"unexpected ModOp {op.attrib}")


def tiers(doc, guid):
    return [[(i.findtext("Good"), i.findtext("ProductionPerMinute"), i.findtext("Limit")) for i in t.findall("Item")]
            for t in values(doc, guid).findall("Trader/OfferedGoods/Item/Goods")]


class StaticTests(unittest.TestCase):
    def test_assets_xml_is_generated_and_up_to_date(self):
        self.assertEqual(ASSETS.read_text(encoding="utf-8"), generate.render())

    def test_modops_are_guid_scoped_and_well_formed(self):
        root = ET.parse(ASSETS).getroot()
        ops = list(modops(root))
        self.assertEqual(len(ops), len(generate.TRADERS) * (len(GOODS) + len(CIO_GOODS)) + len(generate.UNBLOCKED))
        for op in ops:
            self.assertIn(op.get("GUID"), {*generate.TRADERS, generate.TRADE_FEATURE})
            path = op.get("Add") or op.get("Remove")
            self.assertTrue(ADD_PATH.match(path) or REMOVE_PATH.match(path), path)
            if "Add" in op.attrib:
                (item,) = list(op)
                self.assertEqual(item.findtext("Good"), ADD_PATH.match(path).group(1))
                self.assertGreater(float(item.findtext("ProductionPerMinute")), 0)
                self.assertGreater(int(item.findtext("Limit")), 0)

    def test_goods_list(self):
        self.assertEqual(len(GOODS), len(set(GOODS)))
        self.assertTrue(set(generate.UNBLOCKED) <= set(GOODS))
        self.assertNotIn("145102", GOODS)  # Obsidian stays unsellable
        # Final products only: no raw goods, intermediates or building materials.
        for raw in ("2088", "2075", "2174", "2178", "2121", "2152"):  # Sardines, Horses, Timber, Concrete, Cloth, Mosaics
            self.assertNotIn(raw, GOODS)
        self.assertFalse(set(CIO_GOODS) & set(GOODS))

    def test_cio_goods_need_cio(self):
        root = ET.parse(ASSETS).getroot()
        conditioned = {op.find("Item/Good").text for g in root.iter("Group")
                       if g.get("Condition") == f"#{CIO}" for op in g.iter("ModOp")}
        self.assertEqual(conditioned, set(CIO_GOODS))

    def test_modinfo(self):
        info = json.loads((MOD / "modinfo.json").read_text(encoding="utf-8"))
        self.assertEqual(info["Anno"], 8)
        self.assertRegex(info["Version"], r"^\d+\.\d+\.\d+$")
        self.assertIn(info["Difficulty"], ("cheat", "easier", "unchanged", "harder"))
        self.assertEqual(info["AssetsPath"], "data/base/config/export/assets.xml")
        for key in ("ModName", "Description"):
            self.assertTrue(info[key]["English"] and info[key]["French"])
        self.assertIn(str(len(GOODS)), info["Description"]["English"])
        self.assertIn(CIO, info["Dependencies"]["Optional"])
        self.assertIn(CIO, info["Dependencies"]["LoadAfter"])
        # Same purpose, from nexusmods.com/anno117paxromana/mods/30.
        self.assertEqual(set(info["Dependencies"]["Incompatible"]),
                         {"traiding-goods-all", "traiding-building-materials-all"})


class PatchSimulationTests(unittest.TestCase):
    def setUp(self):
        self.vanilla = ET.parse(FIXTURE).getroot()
        self.doc = copy.deepcopy(self.vanilla)
        apply(self.doc, ET.parse(ASSETS).getroot())

    def assert_offers(self, doc, goods):
        for guid in generate.TRADERS:
            vanilla_goods = {g for t in tiers(self.vanilla, guid) for g, *_ in t}
            for n, tier in enumerate(tiers(doc, guid)):
                counts = collections.Counter(g for g, *_ in tier)
                self.assertEqual(set(counts) - vanilla_goods, set(goods) - vanilla_goods, f"{guid} tier {n}")
                self.assertTrue(set(goods) <= set(counts), f"{guid} tier {n}")
                self.assertEqual(max(counts.values()), 1, f"{guid} tier {n}")

    def test_every_tier_offers_every_final_good_once(self):
        self.assert_offers(self.doc, GOODS)

    def test_with_cio(self):
        doc = copy.deepcopy(self.vanilla)
        apply(doc, ET.parse(ASSETS).getroot(), {CIO})
        self.assert_offers(doc, GOODS + CIO_GOODS)

    def test_vanilla_entries_unchanged(self):
        for guid in generate.TRADERS:
            before, after = tiers(self.vanilla, guid), tiers(self.doc, guid)
            self.assertEqual(len(before), len(after))
            for b, a in zip(before, after):
                self.assertEqual(a[:len(b)], b)

    def test_unsellable_list_keeps_only_obsidian(self):
        left = [g.text for g in values(self.doc, generate.TRADE_FEATURE).iter("Good")]
        self.assertEqual(left, ["145102"])

    def test_idempotent(self):
        again = copy.deepcopy(self.doc)
        apply(again, ET.parse(ASSETS).getroot())
        self.assertEqual(ET.tostring(again), ET.tostring(self.doc))


class PackageTests(unittest.TestCase):
    def test_reproducible_zip(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            za, zb = package.build(Path(a)), package.build(Path(b))
            self.assertEqual(za.read_bytes(), zb.read_bytes())
            names = zipfile.ZipFile(za).namelist()
            self.assertIn("[Gameplay] NPC Traders Sell All Finished Goods/modinfo.json", names)
            self.assertIn("[Gameplay] NPC Traders Sell All Finished Goods/data/base/config/export/assets.xml", names)


if __name__ == "__main__":
    unittest.main()
