# Anno 117: NPC Traders Sell All Goods

Mod for Anno 117: Pax Romana. The NPC traders sell every good of Latium and Albion: 112 goods, including the Prophecies of Ash goods.

**Status: not tested in game yet.** The patch has been run through the mod loader's own patch engine on the vanilla `assets.xml`, with no warnings (see [Check against the game data](#check-against-the-game-data)).

## What changes

| Trader | GUID | Vanilla stock tiers |
|---|---|---|
| Diana (Latium) | `32777` | 4 |
| Valeria (Latium) | `32778` | 4 |
| Procurator Corvinus (Albion) | `27124` | 7 |
| Manx (Albion) | `27079` | 6 |
| Caeso (Latium pirate) | `37495` | 4 |
| Voada (Albion pirate) | `37494` | 4 |

- Every stock tier of these traders (`Trader/OfferedGoods/Item`) gets every good from [`reference/goods.tsv`](reference/goods.tsv). Goods are offered from the start of the game, in both provinces.
- Goods a trader already sells in a tier keep their vanilla refill rate and cap. Each added good refills **0.5 per minute up to 30** (vanilla uses 0.25–0.5 and 15–75).
- Statuettes (`145220`) and Latrunculi Sets (`145221`) are removed from `UnsellableGoodsByNonPlayerCharacters` (TradeBalancing `140115`), so NPCs can sell them.
- Traders already buy every good in vanilla (`AcceptAllGoods` 1). Prices are unchanged.

Not changed:

- **Obsidian** (`145102`) stays unsellable. It is the barter currency of Caecilia's volcano trader and has no production building.
- **Caecilia** (`145051`, Prophecies of Ash) is a barter trader for items only, with no goods stock. **Julia** (`41986`) is a campaign trader with goods trading off. Rival AI players are not traders.
- **The Hippodrome** (DLC2) adds no new good: its chariots and horses are already in the list.

### Which goods

Every `Product` asset stored in buildings with a base price, minus workforce and services: 112 goods. All have a production building. Full list with English names, prices and regions: [`reference/goods.tsv`](reference/goods.tsv).

## DLC

Checked against the game files of the 2026-10-13 install: base game, Prophecies of Ash (DLC1), The Hippodrome (DLC2) and the three cosmetic packs are installed. Dawn of the Delta (DLC3) is not installed. The game data already has an `Egyptian` region, but no Egyptian-only good.

After a game patch or a new DLC, regenerate the goods list (see [Development](#development)). New goods are picked up automatically; a new tradeable good without a production building stops the script and asks for a decision.

## Compatibility

| Mod | ModID | Relation |
|---|---|---|
| Trading goods all (Nexus mod 30) | `traiding-goods-all` | **Incompatible**: same purpose |
| The sellers have all the building materials (Nexus mod 30, 2.0.0) | `traiding-building-materials-all` | **Incompatible**: subset of this mod |

`traiding-building-materials-all` 2.0.0 (2025-11-19) was read and run through `xmltest` on the current vanilla data: it still applies with no warning. It adds 4–6 building goods (0.3 per minute, cap 75) to Diana, Valeria, Procurator and Manx with the same technique as this mod (one `Add` on `Trader/OfferedGoods/Item/Goods`, which hits every tier), but without a duplicate check: Armour ends up twice in the Procurator's end-game tier (`109173`). Loaded together with this mod, goods could be listed twice, so both of that author's mods are declared incompatible. Its `traiding-limit` companion was not checked.

Any other mod that edits `Trader/OfferedGoods` of these six traders may stack goods.

## Installation

1. Download `traders-sell-all-goods-postula-<version>.zip`.
2. Extract it into `<user documents>/Anno 117 - Pax Romana/mods/`, so you get `mods/[Gameplay] NPC Traders Sell All Goods/modinfo.json`.
3. Start the game and enable the mod. Works with existing saves. `SafeToRemove`: disabling it restores the vanilla stock.

## In-game test checklist

- [ ] `mod-loader.log` has no warning or error for `traders-sell-all-goods-postula`.
- [ ] Diana's trade screen lists Albion goods (e.g. Beer, Cloaks) at game start, and Valeria's too.
- [ ] Procurator and Manx list Latium goods (e.g. Garum, Togas) in Albion.
- [ ] A good bought out refills over time (0.5 per minute, cap 30).
- [ ] A good sold in vanilla (Timber at Diana) keeps its vanilla stock.
- [ ] The trade screen stays usable with 112 goods (scrolling, passive trade routes to the trader).
- [ ] Statuettes and Latrunculi Sets are offered with Prophecies of Ash active.
- [ ] Without Prophecies of Ash active: check what Statuettes and Latrunculi Sets show (locked products).
- [ ] Pirates Caeso and Voada sell all goods when at peace.
- [ ] Existing save loads and traders show the new stock.

## Unresolved issues

- **Tier semantics.** How the game combines several unlocked `OfferedGoods` tiers is not documented. Vanilla repeats goods across tiers with different values (Diana) and has upgrade tiers with only 1–2 goods (Procurator). The mod adds every good to every tier, so the result is the same whether the game uses the highest tier or merges them. `traiding-building-materials-all` 2.0.0, a released mod, adds goods to every tier the same way.
- **Locked products.** Goods are `<Locked />` until the game unlocks them. Whether traders show a good the player has not unlocked yet needs an in-game test.
- **Trade screen size.** No vanilla trader sells more than 7 goods. 112 goods may make the trade screen long.

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

Result on 2026-11-10 (xmltest GU17.1, vanilla `assets.xml` of 2026-10-13): no warning, every tier of the 6 traders has all 112 goods once, vanilla entries unchanged, a second run gives a byte-identical file, `UnsellableGoodsByNonPlayerCharacters` keeps only Obsidian.

### CI and releases

Same as the olive oil mod: `.github/workflows/ci.yml` runs the tests and builds the ZIP; a `vX.Y.Z` tag equal to `Version` in `mod/modinfo.json` creates a GitHub Release and uploads to mod.io when `MODIO_GAME_ID`, `MODIO_MOD_ID`, `MODIO_TOKEN` and `MODIO_DOMAIN` are set.

## Licensing

[MIT](LICENSE). `tests/fixtures/vanilla_traders.xml` and `reference/goods.tsv` are excerpts of game data for testing; they belong to their owners. Anno and its names belong to their respective owners.
