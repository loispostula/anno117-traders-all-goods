# Anno 117: NPC Traders Sell All Finished Goods

Mod for Anno 117: Pax Romana. The NPC traders sell every finished good of Latium, Albion and Aegyptus: the 50 goods residents consume, including the Prophecies of Ash and Dawn of the Delta goods. With Celtic Independence Overhaul, also its Wicker Baskets and Ornamented Ponies.

**Status: 0.2.0 tested in game by a player (see [In-game results](#in-game-results)); 0.3.0 adds Dawn of the Delta, loads without warnings on game 3.0.** The patch has been run through the mod loader's own patch engine on the vanilla `assets.xml`, with no warnings (see [Check against the game data](#check-against-the-game-data)).

## What changes

| Trader | GUID | Vanilla stock tiers |
|---|---|---|
| Diana (Latium) | `32777` | 4 |
| Valeria (Latium) | `32778` | 4 |
| Procurator Corvinus (Albion) | `27124` | 7 |
| Manx (Albion) | `27079` | 6 |
| Caeso (Latium pirate) | `37495` | 4 |
| Voada (Albion pirate) | `37494` | 4 |
| Heron (Aegyptus, Dawn of the Delta) | `153067` | 1 |
| Valeria (Aegyptus, Dawn of the Delta) | `153068` | 1 |
| Kandis (Aegyptus pirate, Dawn of the Delta) | `153069` | 1 |

- Every stock tier of these traders (`Trader/OfferedGoods/Item`) gets every finished good from [`reference/goods.tsv`](reference/goods.tsv). Goods are offered from the start of the game, in both provinces.
- With Celtic Independence Overhaul (`celtic-independence-overhaul-jtmzac`, optional, loads before) active, they also get Wicker Baskets (`1400300500`) and Ornamented Ponies (`1400300510`). These ModOps sit in a `#celtic-independence-overhaul-jtmzac` group and do nothing without CIO. GUIDs read from CIO 0.9.2 (`includes/goods/celtic_wicker_baskets.include.xml`, `celtic_ornamented_ponies.include.xml`), same on its `main`.
- Raw goods, intermediates and building materials are not added. Those a trader already sold in vanilla (Timber, Tiles, Sardines…) stay.
- Goods a trader already sells in a tier keep their vanilla refill rate and cap. Each added good refills **0.5 per minute up to 30** (vanilla uses 0.25–0.5 and 15–75).
- Statuettes (`145220`) and Latrunculi Sets (`145221`) are removed from `UnsellableGoodsByNonPlayerCharacters` (TradeBalancing `140115`), so NPCs can sell them.
- Buying is not changed. In vanilla (game 3.0) Diana, Valeria, the Procurator, Heron and Valeria of Aegyptus buy every good (`AcceptAllGoods` 1); Manx and the three pirates buy only their `PreferredGoods`. Prices are unchanged.

Not changed:

- **Obsidian** (`145102`) stays unsellable. It is a raw material, the barter currency of Caecilia's volcano trader, and has no production building.
- **Caecilia** (`145051`, Prophecies of Ash) is a barter trader for items only, with no goods stock. **Julia** (`41986`) is a campaign trader with goods trading off. Rival AI players are not traders.
- **The Hippodrome** (DLC2) adds no new good. Chariots are in the list; Horses are a raw good.
- **Heron's sector project** (`182192`) has no goods stock.

### Which goods

Finished goods = `Product` assets with `TransportGoodsType` `Needs`, the game's own category for consumer goods: 50 goods, all residence needs, all with a production building. Raw goods residents also consume directly (Sardines, Cockles, Eels, Horses) have no transport category and are left out. Full list with English names, prices and regions: [`reference/goods.tsv`](reference/goods.tsv). 0.1.0 used every stored good with a base price (112); 0.2.0 had 35 finished goods (before Dawn of the Delta).

## DLC

Checked against game update 3.0 (Steam build 26043928, 2026-11-10), which ships Dawn of the Delta (DLC3): 15 Egyptian finished goods and the Aegyptus traders Heron, Valeria and Kandis. In vanilla, Valeria of Aegyptus already sells Latium and Albion goods (Bread, Brooches, Cloaks, Hand Mirrors, Chariots).

After a game patch or a new DLC, regenerate the goods list (see [Development](#development)). New finished goods are picked up automatically; one without a production building stops the script and asks for a decision.

## Compatibility

| Mod | ModID | Relation |
|---|---|---|
| Trading goods all (Nexus mod 30) | `traiding-goods-all` | **Incompatible**: same purpose |
| The sellers have all the building materials (Nexus mod 30, 2.0.0) | `traiding-building-materials-all` | **Incompatible**: edits the same trader lists |
| Celtic Independence Overhaul | `celtic-independence-overhaul-jtmzac` | Optional, loads before: its 2 finished goods are sold too |
| Valeria & Manx buy everything (Taludas) | `taludas-valeriaandmanxbuyeverything` | Compatible: sets `AcceptAllGoods` on Valeria and Manx (buying). Valeria already has it in vanilla; Manx then buys everything |
| Valeria approves soap (Hier0nimus) | `valeria-approves-soap-hier0nimus` | Compatible, but Soap joins Valeria's `PreferredGoods`, so Valeria of Latium stops selling Soap (a trader never offers a good it prefers) |

`traiding-building-materials-all` 2.0.0 (2025-11-19) was read and run through `xmltest` on the current vanilla data: it still applies with no warning. It adds 4–6 building goods (0.3 per minute, cap 75) to Diana, Valeria, Procurator and Manx with the same technique as this mod (one `Add` on `Trader/OfferedGoods/Item/Goods`, which hits every tier), but without a duplicate check: Armour ends up twice in the Procurator's end-game tier (`109173`). Loaded together with this mod, goods could be listed twice, so both of that author's mods are declared incompatible. Its `traiding-limit` companion was not checked.

Any other mod that edits `Trader/OfferedGoods` of these six traders may stack goods.

## Installation

1. Download `traders-sell-all-goods-postula-<version>.zip`.
2. Delete the 0.1.0 folder `mods/[Gameplay] NPC Traders Sell All Goods` if present (same ModID, the folder was renamed in 0.2.0).
3. Extract it into `<user documents>/Anno 117 - Pax Romana/mods/`, so you get `mods/[Gameplay] NPC Traders Sell All Finished Goods/modinfo.json`.
4. Start the game and enable the mod. Works with existing saves. `SafeToRemove`: disabling it restores the vanilla stock.

## In-game test checklist

- [ ] `mod-loader.log` has no warning or error for `traders-sell-all-goods-postula`.
- [ ] Diana's trade screen lists Albion finished goods (e.g. Beer, Cloaks) at game start, and Valeria's too. No new raw goods or building materials.
- [ ] Procurator and Manx list Latium goods (e.g. Garum, Togas) in Albion.
- [ ] A good bought out refills over time (0.5 per minute, cap 30).
- [ ] A good sold in vanilla (Timber at Diana) keeps its vanilla stock.
- [ ] The trade screen stays usable with about 38 goods (scrolling, passive trade routes to the trader).
- [ ] With Celtic Independence Overhaul: Wicker Baskets and Ornamented Ponies are offered. Without it: no warning in `mod-loader.log`.
- [ ] Statuettes and Latrunculi Sets are offered with Prophecies of Ash active.
- [ ] Without Prophecies of Ash active: check what Statuettes and Latrunculi Sets show (locked products).
- [ ] Pirates Caeso and Voada sell all finished goods when at peace.
- [ ] Existing save loads and traders show the new stock.

## In-game results

A player, 0.2.0, existing save, with Taludas' Increased Trader Production (×2) and Increased Trader Storage (300), which load after this mod and apply to the added goods too:

- `mod-loader.log`: no warning for this mod.
- Diana and Valeria sell the added Latium finished goods the player has unlocked (Garum, Bread, Tunics, Sandals, Olive Oil…). The trade screen stays readable.
- Bought-out goods refill; Timber at Diana keeps its vanilla stock.
- Goods not unlocked yet are not shown (answers the old "Locked products" question).
- Manx and the Procurator in Albion show only vanilla goods. Manx even hides his own Wattle & Daub and Ponies, so the filter is the player's unlocks. The few Albion finished goods unlocked (Porridge, Sausages, Trousers, Reed Shoes, Beer) are all in these traders' `PreferredGoods` (the "Demande" row), and no trader offers a good it prefers. Whether Latium unlocks count in Albion is not verified.

Own test, 0.3.0, game 3.0, new Endless game in Albion: the mod loads; Manx and the Procurator have no harbour at game start, so they could not be checked.

## Unresolved issues

- **Tier semantics.** How the game combines several unlocked `OfferedGoods` tiers is not documented. Vanilla repeats goods across tiers with different values (Diana) and has upgrade tiers with only 1–2 goods (Procurator). The mod adds every good to every tier, so the result is the same whether the game uses the highest tier or merges them. `traiding-building-materials-all` 2.0.0, a released mod, adds goods to every tier the same way.
- **Unlocks per province.** Traders hide goods the player has not unlocked. Whether a good unlocked in Latium counts in Albion is not verified.
- **Preferred goods.** A trader does not offer goods from its own `PreferredGoods` list.
- **Trade screen size.** Only unlocked goods are shown, so the list grows with progress; readable in the in-game test.

## Development

Requires Python 3.10+.

```sh
python3 -m unittest discover -s tests -v   # static checks + patch simulation on trimmed vanilla traders
python3 tools/generate.py                  # rebuild mod/.../assets.xml from reference/goods.tsv
python3 tools/package.py                   # reproducible ZIP in dist/
```

### Refresh from the game files

```sh
G="<steam>/steamapps/common/Anno 117 - Pax Romana/maindata"
python3 tools/rda.py "$G/config.rda" config/export/assets.xml out/
python3 tools/rda.py "$G/config.rda" gui/texts_english.xml out/
python3 tools/vanilla.py out/config.rda/data/base/config/export/assets.xml \
                         out/config.rda/data/base/config/gui/texts_english.xml
python3 tools/generate.py
```

`tools/rda.py` reads RDA v2.2 archives. `tools/vanilla.py` rewrites `reference/goods.tsv` and `tests/fixtures/vanilla_traders.xml`.

### Check against the game data

Build `xmltest` from [jakobharder/anno-mod-loader](https://github.com/jakobharder/anno-mod-loader) (with submodules; `g++ -std=c++17 -include algorithm -DSPDLOG_HEADER_ONLY` and the include paths of `libs/xml-operations` and `third_party` work without Bazel), then:

```sh
xmltest -m mod -o patched.xml <vanilla assets.xml> mod/data/base/config/export/assets.xml
python3 tools/check_patched.py <vanilla assets.xml> patched.xml
```

`xmltest` treats every `#mod-id` condition as false and its `-p` option only knows Anno 1800 paths. To check the CIO branch: apply CIO to vanilla with `xmltest -m <cio> -o vanilla_cio.xml <vanilla> <cio>/data/base/config/export/assets.xml`, copy `mod/`, replace `Condition="#celtic-independence-overhaul-jtmzac"` with `Condition="true()"`, patch `vanilla_cio.xml` with that copy, then run `check_patched.py <vanilla> <result> --with-mod-goods`. (CIO's own new `<Asset>` entries log 162 warnings under `xmltest`; the trader patch does not need them.)

Result for 0.3.0 on 2026-11-10 (xmltest GU17.1, vanilla `assets.xml` of game 3.0): no warning, every tier of the 9 traders has the 50 finished goods once and no CIO good, vanilla entries unchanged, a second run gives a byte-identical file, `UnsellableGoodsByNonPlayerCharacters` keeps only Obsidian. CIO branch (checked on 0.2.0 with CIO 0.9.2): no warning from this mod, the CIO goods once in all 29 tiers.

### CI and releases

Same as the olive oil mod: `.github/workflows/ci.yml` runs the tests and builds the ZIP; a `vX.Y.Z` tag equal to `Version` in `mod/modinfo.json` creates a GitHub Release and uploads to mod.io when `MODIO_GAME_ID`, `MODIO_MOD_ID`, `MODIO_TOKEN` and `MODIO_DOMAIN` are set.

mod.io page: listing image `media/modio-logo.png` (1920×1080, goods icons from the game via anno-117-calculator), description `media/modio-description.html` (paste with the editor's source code button). Neither is in the ZIP.

## Licensing

[MIT](LICENSE). The goods icons in `media/modio-logo.png` belong to their owners and are not covered by the MIT license. `tests/fixtures/vanilla_traders.xml` and `reference/goods.tsv` are excerpts of game data for testing; they belong to their owners. Anno and its names belong to their respective owners.
