#!/usr/bin/env python3
"""Session c252594d — apply the primary-source corrections verified on 2026-11-20.

Every change below was made against a dated fetch of the page named in `sources`.
No value is inferred: where two official pages disagree the cell stays blank and a
flag explains it, which is the rule the register already states in its own "rule" field.

Run:  python3 tools/apply-verification-c252594d.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def save(name, obj):
    (DATA / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote data/{name}")


# ---------------------------------------------------------------- sources
sources = load("sources.json")
by_id = {s["id"]: s for s in sources["sources"]}

# Re-verified in full by this session; keep the original finding, add the dated re-check.
by_id["S12"]["method"] = (
    "fetched 2026-11-20; re-fetched in full 2026-11-20 by session c252594d-affil3 "
    "(specifications block re-read: capacity 8 qt / 7.57 L, Hi-Fry 450 °F, 1700W/120V, "
    "model RJ38-8T-BLACK, cETL approved with a 1-year Chefman assurance)"
)
by_id["S12"]["used_for"] = (
    "P03 comparison column: the manufacturer's own page for the matte-black RJ38-8T-BLACK, "
    "kept separate from the listing's copy. The page does not state overall dimensions, so none are shown."
)
by_id["S13"]["method"] = (
    "fetched 2026-11-20; re-fetched in full 2026-11-20 by session c252594d-affil3 "
    "(specification panel re-read: 26-quart capacity, 24.6 litres, 16.9\"D x 15.8\"W x 14.8\"H, "
    "120 volts, 25 cooking pre-sets, model 4-00675-02A-VN)"
)
by_id["S14"]["method"] = (
    "fetched 2026-11-20; re-fetched in full 2026-11-20 by session c252594d-affil3 "
    "(specifications block re-read: probe 0.19 in thin x 4.75 in long, internal temperature range "
    "32-212 F, ambient temperature range 32-1,000 F, probe materials stainless steel and zirconia)"
)
by_id["S14"]["used_for"] = (
    "P05 internal temperature range 32-212 F, ambient sensor range 32-1,000 F, heat resistance to "
    "1,000 F, probe dimensions, Wi-Fi hub and USB-C charging, waterproof and dishwasher-safe probe."
)

new_sources = [
    {
        "id": "S21",
        "title": "ThermoMaven F1 Ace Instant Read Thermometer - product page",
        "publisher": "ThermoMaven",
        "url": "https://www.thermomaven.com/products/f1-ace",
        "method": "fetched in full 2026-11-20 by session c252594d-affil3",
        "used_for": (
            "P04: the manufacturer's own page for its 1-second instant-read thermometer: "
            "one-second instant read, thermocouple sensor, stated accuracy of +/-0.5 F, bright "
            "auto-rotating LCD, 100% waterproof design, built-in magnet, lifetime warranty "
            "activated within 30 days. The page does not state a temperature range, a power source, "
            "dimensions or a weight, so those cells stay blank."
        ),
        "status": "verified",
    },
    {
        "id": "S22",
        "title": "Chefman TurboFry Touch Stainless-Steel Air Fryer, 8 qt (RJ38-SQSS-8T) - product page",
        "publisher": "Chefman",
        "url": "https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1",
        "method": "fetched in full 2026-11-20 by session c252594d-affil3",
        "used_for": (
            "P03: the manufacturer's own page for the 8 qt stainless-steel model whose model number "
            "(RJ38-SQSS-8T) is the one the Amazon listing itself names. States a 200-400 F range, "
            "8 qt / 7.57 L, 1700W/120V, dimensions 15.4 x 12.6 x 13.5 in, weight 12.8 lb, "
            "4 cooking presets, top-rack dishwasher-safe basket, cETL approved, 1-year assurance."
        ),
        "status": "verified",
    },
    {
        "id": "S23",
        "title": "Understanding ASINs to create successful advertising campaigns",
        "publisher": "Amazon Ads (Amazon.com, Inc.)",
        "url": "https://advertising.amazon.com/library/guides/asins-introduction",
        "method": "fetched in full 2026-11-20 by session c252594d-affil3",
        "used_for": (
            "The Amazon-owned definition of the ASIN, closing FLG-012: an ASIN is 'a unique "
            "combination of 10 letters and numbers that Amazon assigns to a product'."
        ),
        "status": "verified",
        "quote": (
            "Short for \"Amazon Standard Identification Number,\" an ASIN is a unique combination "
            "of 10 letters and numbers that Amazon assigns to a product—including product variations "
            "and product versions—in the Amazon store."
        ),
    },
]
existing = {s["id"] for s in sources["sources"]}
for s in new_sources:
    if s["id"] not in existing:
        sources["sources"].append(s)
save("sources.json", sources)

# ---------------------------------------------------------------- products
products = load("products.json")
prod = {p["id"]: p for p in products["products"]}

# ---- P03: the maker publishes the exact model the listing names -------------------
p3 = prod["P03"]
p3["model"] = "RJ38-SQSS-8T"
p3["capacity_note"] = (
    "8 qt / 7.57 L per the manufacturer's page for the 8 qt model; the Amazon listing also states 8 quarts."
)
p3["temp_min_f"] = "200"
p3["temp_max_f"] = "400"
p3["weight_lb"] = "12.8"
p3["functions"] = (
    "Air fry, bake, dehydrate and frozen - four cooking presets, per the manufacturer's "
    "RJ38-SQSS-8T page. The Amazon listing's own title adds a 450 F Hi-Fry option that the "
    "manufacturer's page for this model does not list (FLG-027)."
)
p3["sources"] = ["S05", "S04", "S22", "S12", "S16"]
p3["spec_sources"] = ["S22"]
p3["blank_reason"] = {
    "power_w": (
        "The manufacturer's page for RJ38-SQSS-8T states 1700 W; the Amazon listing for B08DKYBTPH "
        "states 1000 W for what it calls the same model. The two official pages disagree, so no "
        "wattage is published (FLG-026)."
    ),
    "dimensions_in": (
        "The manufacturer's page for RJ38-SQSS-8T states 15.4 x 12.6 x 13.5 in; the Amazon listing "
        "states 12.75 x 13.5 x 10 in. The two official pages disagree, so no size is published (FLG-026)."
    ),
    "temp_max_f_note": (
        "The 200-400 F range published above is the manufacturer's range for RJ38-SQSS-8T. The listing's "
        "title advertises a 450 F Hi-Fry option; that figure belongs to the manufacturer's other 8 qt "
        "model, RJ38-8T-BLACK (S12), so it is not published for this row."
    ),
}
p3["model_note"] = (
    "The Amazon listing's own copy names model RJ38-SQSS-8T, and Chefman publishes that model "
    "(S22). Chefman also publishes a different 8 qt machine, RJ38-8T-BLACK (S12), so '8 qt' on its "
    "own does not identify a unit. See FLG-026."
)
p3["reverification"]["2026-11-20"] = (
    "Re-verified by session c252594d-affil3: Chefman's own catalogue carries two 8 qt air fryers. "
    "The page for RJ38-SQSS-8T (S22) matches the model number the Amazon listing names and states a "
    "200-400 F range, 1700W/120V, 15.4 x 12.6 x 13.5 in and 12.8 lb. The page for RJ38-8T-BLACK (S12) "
    "states 450 F Hi-Fry, 1700W/120V and no dimensions. Wattage and size still disagree between the "
    "maker's page and the listing, so both stay blank (FLG-026)."
)

# ---- P04: the manufacturer does publish a page; the submitted link resolves here ----
p4 = prod["P04"]
p4["confirmation_status"] = "Unverified; observation only"
p4["model"] = "F1 Ace (manufacturer's page; the observed listing is titled 1 Sec Professional - FLG-031)"
p4["functions"] = (
    "Instant read in one second on a thermocouple sensor; bright auto-rotating LCD; "
    "motion-sensing wake and sleep; built-in magnet (manufacturer)"
)
p4["dishwasher_safe"] = (
    "Waterproof design: yes (manufacturer states a 100% waterproof design). Dishwasher use is not stated."
)
p4["certification"] = (
    "Stated accuracy +/-0.5 F, described by the manufacturer as NIST-certified precision; the "
    "manufacturer's page also displays an NSF mark. The marketplace listing additionally states "
    "NSF certification and an IP67 rating, neither of which the manufacturer's page states (FLG-032)."
)
p4["warranty"] = "Lifetime warranty, to be activated within 30 days of purchase (manufacturer)"
p4["sources"] = ["S05", "S04", "S21"]
p4["spec_sources"] = ["S21"]
p4["tagged_outbound_url"] = "https://www.amazon.com/dp/B0DHZTCNR5?tag=shopnow047c-20"
p4["no_buy_link"] = None
p4.pop("no_buy_link", None)
p4.pop("no_buy_link_reason", None)
p4["blank_reason"] = {
    "temp_min_f": "The manufacturer's page does not state a temperature range for the probe.",
    "temp_max_f": "The manufacturer's page does not state a temperature range for the probe.",
    "power_w": "The manufacturer's page does not state a power source or a battery type.",
    "voltage": "Not applicable to the manufacturer's page, which does not state a power source.",
    "dimensions_in": "The manufacturer's page does not state dimensions.",
    "weight_lb": "The manufacturer's page does not state a weight.",
    "capacity_qt": "Not applicable; this is a hand-held probe, not a vessel with a capacity.",
    "model_note": (
        "The manufacturer's page is titled F1 Ace. The observed marketplace listing is titled "
        "1 Sec Professional. The maker's F1 Ace page describes the same one-second instant read, "
        "auto-rotating display and waterproof design, but the maker does not publish the marketplace "
        "identifier on that page, so the two are consistent rather than confirmed identical (FLG-031)."
    ),
}
p4["reverification"]["2026-11-20"] = (
    "Re-verified by session c252594d-affil3. Two things changed. First, a manufacturer page for this "
    "line exists: thermomaven.com/products/f1-ace (S21), fetched in full, states a one-second instant "
    "read on a thermocouple sensor, a stated accuracy of +/-0.5 F, a bright auto-rotating LCD, a 100% "
    "waterproof design, a built-in magnet and a lifetime warranty activated within 30 days. Second, the "
    "submitted short link for this row, https://link.amazon/B0c8moW59, resolves to this listing "
    "(B0DHZTCNR5, a live ThermoMaven 1 Sec Professional Digital Meat Thermometer page fetched "
    "2026-11-20), so the row no longer needs to withhold its buy link. A third dated fetch of the short "
    "link on 2026-11-20 landed on the Amazon home page instead of the listing, which is the same "
    "intermittent checkpoint behaviour already recorded in FLG-003 and FLG-024; the destination varies "
    "by attempt and must be re-checked in a signed-in session."
)

# ---- P05: 1,000 F is the ambient ceiling, not the probe's reading range -------------
p5 = prod["P05"]
p5["temp_min_f"] = "32"
p5["temp_max_f"] = "212"
p5["functions"] = (
    "Four internal sensors plus one ambient sensor (per the manufacturer's features list); Wi-Fi hub "
    "with speaker; USB-C charging; waterproof, dishwasher-safe probe"
)
p5["blank_reason"] = {
    "battery": (
        "The manufacturer's product page says '70+ hours' while the same brand's FAQ says 'up to 60 "
        "hours' for Gen 3, so no battery figure is published (FLG-023)."
    ),
    "model": (
        "The manufacturer's page shows one variant of a family (CQ60-1C-Z1-E, one probe). The observed "
        "listing is titled with three probes and 'Gen3', so no single model number is published."
    ),
    "temp_max_f_note": (
        "32-212 F is the manufacturer's internal temperature range for the probe. The manufacturer's "
        "ambient sensor range is 32-1,000 F, and it states the probe is heat resistant to 1,000 F; "
        "that ceiling is not a reading range for the food."
    ),
}
p5["spec_notes"] = [
    ["Ambient sensor", "32-1,000 °F (manufacturer)"],
    ["Heat resistance", "Up to 1,000 °F / 537 °C (manufacturer)"],
    ["Sensor count", "The features list says four internal sensors plus one ambient sensor; the same page's opening paragraph says five internal sensors (FLG-033)"],
]
p5["reverification"] = {
    "date": "2026-11-20",
    "correction": (
        "The register published the probe's temperature range as 32-1,000 F. Re-fetching the "
        "manufacturer's page in full shows that 1,000 F is the ambient sensor range and the heat-"
        "resistance ceiling; the internal range for the probe is 32-212 F. The published range was "
        "corrected, and the ambient figure is now shown as its own row."
    ),
    "method": "Read https://chefiq.com/products/iq-sense in full, including the Specifications block.",
    "session": "c252594d-affil3",
}

save("products.json", products)

# ---------------------------------------------------------------- flags
flags = load("flags.json")
flg = {f["id"]: f for f in flags["flags"]}

flg["FLG-012"]["status"] = "resolved"
flg["FLG-012"]["severity"] = "low"
flg["FLG-012"]["title"] = "Amazon's own definition of the ASIN has now been retrieved (resolved)"
flg["FLG-012"]["detail"] = (
    "Amazon Ads publishes the definition on its own site: an ASIN is 'a unique combination of 10 "
    "letters and numbers that Amazon assigns to a product'. This is an Amazon-owned page, so the "
    "10-character rule that FLG-001 depends on no longer rests on third-party descriptions or on "
    "inference from observed identifiers."
)
flg["FLG-012"]["manual_step"] = (
    "Closed by session c252594d-affil3 on 2026-11-20 with source S23. No further action needed; "
    "re-check only if Amazon moves the page."
)
flg["FLG-012"]["sources"] = ["S23", "S04"]

flg["FLG-025"]["status"] = "resolved"
flg["FLG-025"]["severity"] = "low"
flg["FLG-025"]["title"] = "ThermoMaven: a manufacturer page exists (resolved)"
flg["FLG-025"]["detail"] = (
    "A ThermoMaven product page for this line does exist: thermomaven.com/products/f1-ace, fetched in "
    "full on 2026-11-20 (S21). It states a one-second instant read on a thermocouple sensor, a stated "
    "accuracy of +/-0.5 F, a bright auto-rotating LCD, a 100% waterproof design, a built-in magnet and a "
    "lifetime warranty activated within 30 days. Those values are now published on the product page, "
    "attributed to the manufacturer. Values the page does not state - temperature range, power source, "
    "dimensions, weight - remain blank and render as 'not stated'. Two new flags record what is still "
    "open: FLG-031 (the maker's page is titled F1 Ace, the observed listing is titled 1 Sec Professional) "
    "and FLG-032 (the listing states NSF certification and an IP67 rating that the manufacturer's page "
    "does not state)."
)
flg["FLG-025"]["impact"] = (
    "The product page now carries a specification grid and a tagged outbound link instead of being an "
    "empty context card. The intended-product question is unchanged and still flagged (FLG-001)."
)
flg["FLG-025"]["manual_step"] = (
    "Closed by session c252594d-affil3 on 2026-11-20 with source S21. To close FLG-031 as well, "
    "confirm in a signed-in Amazon session that listing B0DHZTCNR5 is the F1 Ace."
)
flg["FLG-025"]["sources"] = ["S21", "S04"]

flg["FLG-026"]["status"] = "open"
flg["FLG-026"]["severity"] = "high"
flg["FLG-026"]["title"] = "The 8 qt air fryer listing and the manufacturer's catalogue describe two different machines"
flg["FLG-026"]["detail"] = (
    "Chefman publishes at least two 8 qt air fryers. The page for RJ38-8T-BLACK (S12) states a 450 F "
    "Hi-Fry finish, 1700W/120V and no dimensions. The page for RJ38-SQSS-8T (S22) states a 200-400 F "
    "range, 1700W/120V, 15.4 x 12.6 x 13.5 in and 12.8 lb. The Amazon listing for B08DKYBTPH names "
    "RJ38-SQSS-8T in its own copy and states 1000 W / 120 V, a 200-400 F range and 12.75 x 13.5 x 10 in. "
    "So the temperature range and the model number now agree across the listing and the maker's own "
    "page for RJ38-SQSS-8T, and the row publishes that range. Wattage and size still disagree between "
    "two official pages, so both stay blank. The listing's title also advertises a 450 F Hi-Fry option "
    "that the manufacturer's page for the model the listing names does not list, which is FLG-027."
)
flg["FLG-026"]["manual_step"] = (
    "Open the B08DKYBTPH listing in a signed-in session and read the model number in the 'About this "
    "item' block and the size chart. If the listing sells the matte-black RJ38-8T-BLACK, the published "
    "200-400 F range should move to the listing column instead."
)
flg["FLG-026"]["sources"] = ["S12", "S22", "S16"]

new_flags = [
    {
        "id": "FLG-031",
        "severity": "medium",
        "status": "open",
        "area": "product data",
        "title": "ThermoMaven: the maker's page and the observed listing carry different model names",
        "detail": (
            "The manufacturer's page used for P04's specifications is titled ThermoMaven F1 Ace Instant "
            "Read Thermometer. The observed marketplace listing for that row is titled ThermoMaven 1 Sec "
            "Professional Digital Meat Thermometer. The maker's own line-up includes a 1-second model "
            "and a 0.5-second model, and the F1 Ace page describes a one-second instant read, a bright "
            "auto-rotating display and a waterproof design - the same defining features the listing "
            "states. That makes the two consistent, but the maker does not publish the marketplace "
            "identifier on its page, so identity is consistent rather than confirmed. The P04 row says "
            "so on the page itself."
        ),
        "impact": (
            "The published P04 specifications rest on a manufacturer page that is probably, but not "
            "provably, the same unit as the observed listing."
        ),
        "manual_step": (
            "In a signed-in Amazon session, open the listing for the ThermoMaven 1 Sec Professional "
            "thermometer and look for a model number on the product page or in the manufacturer's own "
            "storefront listing. If it reads F1 Ace, close this flag; if it reads HT04 or another code, "
            "the P04 specification row must be re-sourced."
        ),
        "sources": ["S21", "S04"],
    },
    {
        "id": "FLG-032",
        "severity": "medium",
        "status": "open",
        "area": "product data",
        "title": "ThermoMaven: the marketplace listing states NSF certification and an IP67 rating that the manufacturer's page does not",
        "detail": (
            "The observed listing title for P04 reads 'NIST&NSF Certified ... IP67 Waterproof'. The "
            "manufacturer's own page states a +/-0.5 F accuracy and describes the unit as NIST-certified, "
            "and it displays an NSF mark, but it does not state NSF certification in words and it does not "
            "state an IP rating - it says 100% waterproof design. The site therefore publishes the "
            "manufacturer's wording and records the extra listing claims as claims of the listing."
        ),
        "impact": (
            "A buyer comparing the product page with the listing will see two different certification "
            "claims and two different water-resistance descriptions."
        ),
        "manual_step": (
            "Ask ThermoMaven, through the contact form on its product page, whether the F1 Ace carries "
            "NSF certification and an IP67 rating, and whether the 1 Sec Professional listing is the "
            "same product. One email closes FLG-031 and FLG-032 together."
        ),
        "sources": ["S21", "S04"],
    },
    {
        "id": "FLG-033",
        "severity": "low",
        "status": "open",
        "area": "product data",
        "title": "CHEF iQ Sense: the manufacturer's own page disagrees with itself on the sensor count",
        "detail": (
            "On https://chefiq.com/products/iq-sense the opening paragraph says 'Five internal sensors' "
            "and a section heading reads 'Five Temperature Sensors', while the features list on the same "
            "page says '4 internal temperature sensors for accuracy within 1 F' plus '1 ambient temperature "
            "sensor' - four internal and one ambient, which is five in total. The published P05 row "
            "follows the features list and says so on the page."
        ),
        "impact": (
            "A reader counting sensors on the manufacturer's own page gets two different answers, so the "
            "specification could be quoted back at the site."
        ),
        "manual_step": (
            "Ask CHEF iQ which reading is current for the generation being sold, or read the user guide "
            "PDF linked on the product page, which is the manufacturer's own document."
        ),
        "sources": ["S14"],
    },
]
existing = {f["id"] for f in flags["flags"]}
for f in new_flags:
    if f["id"] not in existing:
        flags["flags"].append(f)
save("flags.json", flags)
print("done")
