"""The tests that matter for this repository are not "does the code run" but "does the gate
actually catch a wrong claim". Each test corrupts one field in a temporary copy of the register
and asserts the gate notices. If one of these starts passing while the data changes, the gate has
been weakened, which is the failure mode to watch.

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import gate  # noqa: E402
import site_common  # noqa: E402


class RegisterSandbox(unittest.TestCase):
    """Point the whole toolchain at a throwaway copy of data/, content/ and docs/."""

    def setUp(self) -> None:
        # Copy the whole surface, then point the toolchain at the copy. Auditing a half-copied tree
        # would let a rule pass against the real repo and fail against the fixture, which is worse
        # than no test at all.
        self.tmp = Path(tempfile.mkdtemp(prefix="cw-test-"))
        self.real = site_common.SITE_ROOT
        self.surface = self.tmp / "counterwise"
        shutil.copytree(self.real, self.surface, ignore=shutil.ignore_patterns("__pycache__", ".git"))
        gate.set_root(self.surface)
        self.docs = gate.OUT
        self.data = gate.DATA
        self.content = gate.CONTENT

    def tearDown(self) -> None:
        gate.set_root(self.real)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def patch_json(self, name: str, mutate) -> None:
        path = self.data / name
        doc = json.loads(path.read_text(encoding="utf-8"))
        mutate(doc)
        path.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    def patch_html(self, rel: str, replace: tuple[str, str]) -> None:
        path = self.docs / rel
        text = path.read_text(encoding="utf-8")
        old, new = replace
        self.assertIn(old, text, f"test precondition: {old!r} is not in {rel}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")


class TestRegisterRules(RegisterSandbox):
    def test_untouched_register_passes_the_data_rules(self):
        for rule in (gate.rule_sources_register, gate.rule_products, gate.rule_links, gate.rule_register_crossrefs):
            self.assertEqual(rule(), [], f"{rule.__name__} should pass on the committed register")

    def test_intended_asin_without_confirmation_is_refused(self):
        def mutate(doc):
            for p in doc["products"]:
                if p["id"] == "P-01":
                    p["intent"]["intended_asin"] = "B0CDY277D3"

        self.patch_json("products.json", mutate)
        findings = gate.rule_products()
        self.assertTrue(any("confirmation_date" in f for f in findings), findings)

    def test_copying_an_observation_into_the_intent_record_is_refused(self):
        """The specific shortcut this register exists to prevent: filling 'intended' from 'observed'."""

        def mutate(doc):
            for p in doc["products"]:
                if p["id"] == "P-01":
                    p["intent"]["intended_asin"] = p["observation"]["listing_asin_observed_in_path"]
                    p["intent"]["official_listing_url"] = p["observation"]["listing_url_observed"]
                    p["intent"]["status"] = "confirmed"

        self.patch_json("products.json", mutate)
        findings = gate.rule_products()
        self.assertTrue(any("confirmation_date" in f for f in findings), findings)

    def test_a_titled_attribute_that_is_not_in_the_listing_title_is_refused(self):
        def mutate(doc):
            for p in doc["products"]:
                if p["id"] == "P-03":
                    p["titled_features"].append("Self-cleaning steam cycle")

        self.patch_json("products.json", mutate)
        findings = gate.rule_products()
        self.assertTrue(any("Self-cleaning" in f for f in findings), findings)

    def test_a_placeholder_value_is_refused_where_a_blank_is_required(self):
        def mutate(doc):
            for p in doc["products"]:
                if p["id"] == "P-04":
                    p["intent"]["intended_asin"] = "TBD"

        self.patch_json("products.json", mutate)
        self.assertTrue(any("placeholder" in f.lower() for f in gate.rule_products()))

    def test_an_unresolved_link_may_not_carry_a_product_identifier(self):
        def mutate(doc):
            for l in doc["links"]:
                if l["id"] == "LNK-04":
                    l["observed_path_id"] = "B0CDY277D3"
                    l["observed_path_id_length"] = 10

        self.patch_json("links.json", mutate)
        self.assertTrue(any("LNK-04" in f for f in gate.rule_links()), gate.rule_links())

    def test_token_length_must_match_the_token(self):
        def mutate(doc):
            doc["links"][0]["supplied_token_length"] = 10

        self.patch_json("links.json", mutate)
        self.assertTrue(any("length" in f for f in gate.rule_links()))

    def test_claiming_a_source_was_read_with_no_method_is_refused(self):
        def mutate(doc):
            doc["sources"][0]["method"] = ""

        self.patch_json("sources.json", mutate)
        self.assertTrue(any("method" in f for f in gate.rule_sources_register()))

    def test_unknown_cross_reference_is_refused(self):
        def mutate(doc):
            doc["guides"][0]["sources"].append("SG-99")

        self.patch_json("guides.json", mutate)
        self.assertTrue(any("SG-99" in f for f in gate.rule_register_crossrefs()))

    def test_events_must_be_exactly_the_five_defined(self):
        def mutate(doc):
            doc["events"].append({"id": "EV-06", "name": "ad_impression", "properties": {}, "fires_on": "", "decision_it_serves": ""})

        self.patch_json("events.json", mutate)
        self.assertTrue(any("exactly five" in f for f in gate.rule_register_crossrefs()), gate.rule_register_crossrefs())

    def test_hardcoded_tallies_must_match_the_data(self):
        def mutate(doc):
            doc["summary_counts"]["shipped"] = 99

        self.patch_json("suggestions.json", mutate)
        self.assertTrue(any("summary_counts" in f for f in gate.rule_counts_consistent()))


class TestPageRules(RegisterSandbox):
    def test_clean_build_is_clean(self):
        self.assertEqual(gate.rule_pages(), [], "the committed docs/ should pass the page rules")

    def test_stripping_the_tag_from_one_product_link_fails_the_build(self):
        self.patch_html("index.html", ("?tag=" + site_common.load("config.json")["amazon"]["tracking_id"], "?tag=nobody-20"))
        self.assertTrue(any("tracking tag" in f for f in gate.rule_pages()))

    def test_removing_sponsored_fails(self):
        self.patch_html("gear/index.html", ('rel="sponsored nofollow noopener"', 'rel="noopener"'))
        findings = gate.rule_pages()
        self.assertTrue(any("sponsored" in f for f in findings), findings[:5])

    def test_moving_the_disclosure_out_of_the_footer_fails(self):
        self.patch_html("index.html", ('data-disclosure="footer"', 'data-nothing="footer"'))
        self.assertTrue(any("footer disclosure" in f for f in gate.rule_pages()))

    def test_paraphrasing_the_required_statement_fails(self):
        self.patch_html("about/index.html", ("As an Amazon Associate I earn from qualifying purchases.", "As an Amazon Associate I earn money from qualifying purchases."))
        findings = gate.rule_pages()
        self.assertTrue(any("required statement" in f for f in findings), findings[:5])

    def test_claiming_to_have_tested_a_product_fails(self):
        target = self.docs / "guides" / "basket-or-oven.html"
        text = target.read_text(encoding="utf-8")
        injected = text.replace('<main id="main">', "<main id=\"main\"><p>We tested all four machines for six weeks.</p>", 1)
        self.assertNotEqual(injected, text, "test precondition: the guide page has a main element")
        target.write_text(injected, encoding="utf-8")
        findings = gate.rule_pages()
        self.assertTrue(any("banned phrase" in f for f in findings), findings[:5])

    def test_a_price_on_a_product_page_fails(self):
        target = self.docs / "gear" / "index.html"
        text = target.read_text(encoding="utf-8")
        injected = text.replace('<main id="main">', '<main id="main"><p>Now only $74.99</p>', 1)
        self.assertNotEqual(injected, text)
        target.write_text(injected, encoding="utf-8")
        self.assertTrue(any("banned phrase" in f for f in gate.rule_pages()))

    def test_slop_vocabulary_fails(self):
        target = self.docs / "guides" / "capacity-checklist.html"
        text = target.read_text(encoding="utf-8")
        injected = text.replace('<main id="main">', "<main id=\"main\"><p>Look no further for a seamless experience.</p>", 1)
        self.assertNotEqual(injected, text)
        target.write_text(injected, encoding="utf-8")
        findings = gate.rule_pages()
        self.assertTrue(any("banned phrase" in f for f in findings), findings[:5])

    def test_a_broken_internal_link_fails(self):
        target = self.docs / "privacy" / "index.html"
        text = target.read_text(encoding="utf-8")
        injected = text.replace('<main id="main">', '<main id="main"><a href="/no-such-page/">x</a>', 1)
        self.assertNotEqual(injected, text, "test precondition: <main id=\"main\"> is present")
        target.write_text(injected, encoding="utf-8")
        findings = gate.rule_pages()
        self.assertTrue(any("broken internal link" in f for f in findings), findings[:5])

    def test_a_missing_asset_fails(self):
        (self.docs / "assets" / "img" / "hero-front.png").unlink()
        findings = gate.rule_pages()
        self.assertTrue(any("no file behind it" in f for f in findings), findings[:5])

    def test_an_unregistered_citation_fails(self):
        target = self.docs / "about" / "index.html"
        text = target.read_text(encoding="utf-8")
        injected = text.replace(
            '<main id="main">', '<main id="main"><p>Per <a href="https://en.wikipedia.org/wiki/Air_fryer">Wikipedia</a>.</p>', 1
        )
        self.assertNotEqual(injected, text)
        target.write_text(injected, encoding="utf-8")
        self.assertTrue(any("unregistered URL" in f for f in gate.rule_pages()))

    def test_adding_product_structured_data_without_a_feed_fails(self):
        target = self.docs / "index.html"
        text = target.read_text(encoding="utf-8")
        payload = json.dumps({"@context": "https://schema.org", "@type": "Product", "name": "x"})
        target.write_text(text.replace("</head>", f'<script type="application/ld+json">{payload}</script></head>', 1), encoding="utf-8")
        self.assertTrue(any("Product markup without" in f for f in gate.rule_jsonld()))

    def test_stale_output_fails(self):
        manifest = self.docs / "manifest.json"
        doc = json.loads(manifest.read_text(encoding="utf-8"))
        doc["inputs_hash"] = "deadbeefdeadbeef"
        manifest.write_text(json.dumps(doc), encoding="utf-8")
        self.assertTrue(any("stale" in f for f in gate.rule_no_hand_edited_output()))


class TestMeasurementRules(RegisterSandbox):
    def test_claiming_deployment_without_an_endpoint_fails(self):
        def mutate(doc):
            doc["measurement"]["status"] = "deployed"

        self.patch_json("config.json", mutate)
        # config is read from data/ by the rules; the markup attribute is what disagrees with it
        self.assertTrue(any("claims deployment" in f or "Endpoint" in f or "endpoint" in f for f in gate.rule_measurement()), gate.rule_measurement())

    def test_an_illegal_event_name_is_rejected_by_the_collector(self):
        import collector

        sink = collector.Sink(self.tmp / "sink")
        ok, why = sink.accept({"event": "ad_impression", "page": "/guides/x.html", "props": {}})
        self.assertFalse(ok)
        self.assertEqual(why, "unknown-event")

    def test_a_query_string_in_the_page_field_is_rejected(self):
        import collector

        sink = collector.Sink(self.tmp / "sink2")
        ok, why = sink.accept({"event": "page_view", "page": "/guides/x.html?token=abc", "props": {}})
        self.assertFalse(ok)
        self.assertEqual(why, "bad-page")

    def test_allowed_events_are_written_one_per_line(self):
        import collector

        sink = collector.Sink(self.tmp / "sink3")
        ok, _ = sink.accept({"event": "product_link_click", "page": "/gear/", "props": {"product_id": "P-01", "link_state": "pending-test", "placement": "rail"}})
        self.assertTrue(ok)
        files = list((self.tmp / "sink3").glob("events-*.jsonl"))
        self.assertEqual(len(files), 1)
        rec = json.loads(files[0].read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(rec["props"]["product_id"], "P-01")
        self.assertNotIn("ip", json.dumps(rec))

    def test_unprovenanced_amazon_side_numbers_are_refused(self):
        import ledger

        with self.assertRaises(ledger.Refused):
            ledger.append({"date": "2026-12-01", "channel": "search", "reported_orders": "3", "retrieved_by": "someone"})

    def test_clicks_may_be_recorded_without_an_amazon_source(self):
        import ledger

        ledger.append({"date": "2026-12-01", "channel": "search", "clicks": "12", "retrieved_by": "arena-c7a56e3d", "source": ""})
        rows = ledger.read_rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["clicks"], "12")

    def test_channel_attribution_follows_the_documented_rule(self):
        import ledger

        self.assertEqual(ledger.attribution_of("https://www.google.com/url?q=x"), "search")
        self.assertEqual(ledger.attribution_of("https://reddit.com/r/kitchen"), "social")
        self.assertEqual(ledger.attribution_of(""), "direct")
        self.assertEqual(ledger.attribution_of("newsletter:utm_source=newsletter"), "newsletter")
        self.assertEqual(ledger.attribution_of("https://example.org/elsewhere"), "other")


if __name__ == "__main__":
    unittest.main()
