import json

# ============================================================== flags
fd = json.load(open('data/flags.json')); F = fd['flags']; fb = {x['id']: x for x in F}
fb['FLG-032']['detail'] = fb['FLG-032']['detail'].replace(
 "Only the root publication is listed in sitemap.xml; the others are excluded from the index through robots.txt and noindex metadata, and they are all reachable from the single archive page.",
 "Only the root publication is listed in sitemap.xml. What protects the others is thinner than that sentence used to claim, and is now stated exactly: "
 "every non-root page is reachable, the root robots.txt disallows /editorial/, /legacy/, /crisp-index/, /counter/ and /counterwise/ (widened 2026-11-20), "
 "only /editorial/ ships a noindex tag of its own, and robots.txt is not an indexing control at all - Google reads it from the host root, not from a project "
 "path, and says it 'is not a mechanism for keeping a web page out of Google' (S24, S25, S26, FLG-038, FLG-043). They are all reachable from the single archive page.")
fb['FLG-006']['sources'] = ["S19", "S02"]
fb['FLG-006']['detail'] = fb['FLG-006']['detail'].replace(
 "Associates help states that tags must be embedded in links on the sites declared in the application (S11). The declared site URL and account approval status are unknown to this build. The qualifying-sales requirement (three within 180 days) is also stated (S11).",
 "Associates help states that tags must be embedded in links on the sites declared in the application, and the qualifying-sales requirement is three sales within "
 "180 days (S19, read from an excerpt: re-check in a signed-in session). Program Policies 2(b) is the clause tying the tag to every link on a declared site (S02). "
 "The declared site URL and account approval status are unknown to this build. Citation corrected 2026-11-20 by session b7320829-affil3, which had credited S11 for "
 "both statements: in this register S11 is the Chefman dual-basket product page (FLG-044).")
fb['FLG-007']['sources'] = ["S19"]
fb['FLG-007']['detail'] += " Citation corrected 2026-11-20: the rule of thumb was credited to S11, a Chefman product page; the row that holds it is S19 (FLG-044)."
fb['FLG-012']['sources'] = ["S04", "S23"]
fb['FLG-012']['detail'] += (" Corrected 2026-11-20: this row also credited S12, which is the Chefman High-Fry product page and says nothing about what an ASIN is; "
 "the sell.amazon.com candidate page is listed as text in the manual step because that host is not on the gate's source allowlist (FLG-044).")
fb['FLG-012']['manual_step'] = ("Either cite https://sell.amazon.com/learn/prepare-to-sell after adding sell.amazon.com to ALLOWED_SOURCE_HOSTS in tools/verify.mjs, "
 "or accept the observed-identifier basis and close this flag as 'not needed'.")
fb['FLG-014']['detail'] = ("No named author, credential or biography is supplied, so every byline reads with the team name held in data/config.json "
 "('ShopNow Kitchen editorial team'). Inventing a person would be a fabrication, and a fabricated credential would also cut against the truthfulness the "
 "Program Policies ask of an Associates site. If a named editor is wanted, the name, the role and any claimed experience have to come from the owner "
 "(Q-06, suggestion S-08). Corrected 2026-11-20: this row quoted a byline string ('Affil3 editorial team') that the config has not held since the rename (FLG-044).")

NEWF = [
 {"id":"FLG-043","severity":"medium","status":"open","area":"findability",
  "title":"The root robots.txt the site leans on is not read where the site is served, and the board said the editions were de-indexed",
  "detail":("Wording: FLG-032 stated the non-root editions 'are excluded from the index through robots.txt and noindex metadata'. Google's pages say a robots.txt "
   "file 'is not a mechanism for keeping a web page out of Google', that a disallowed URL 'can still appear in search results' without a description, that "
   "'Specifying the noindex rule in the robots.txt file is not supported by Google', and that a page blocked in robots.txt cannot have its noindex tag seen "
   "(S24, S26). Against the shipped files: /editorial/ carries noindex; /counter/, /counterwise/, /counter-desk/ and /crisp-index/ do not, and /counter/ and "
   "/counterwise/ advertise sitemaps of their own. That sentence is now replaced with what the files actually do. Mechanism: main's FLG-038 established that "
   "Google reads robots.txt from the host root, so /Affil3/robots.txt is not consulted for these URLs at all - which means the Disallow lines for the secondary "
   "editions, and the index,follow meta tag now on every root page, buy crawl-budget management and explicit intent for crawlers that read path-scoped files, "
   "and nothing for Google today. The only per-page control available without host access is a noindex meta tag in each edition's own generator, with those paths "
   "left crawlable so the tag can be read: S-20 option B. Moving an edition under /legacy/ is option C."),
  "impact":"Either the site says plainly that four near-duplicate editions of the same five products are indexable and competing, or it does not get to claim it de-indexed them. The first is honest and fixable; the second is a promise the repository cannot keep from the root.",
  "manual_step":"Pick S-20 option B (noindex,follow in each secondary edition's generator, no Disallow line on those paths) or option C (archive them off this Pages site). Each edition is built by its own session's tooling, so the request is logged in COORDINATION.md rather than executed here.",
  "sources":["S24","S25","S26","S09"]},
 {"id":"FLG-044","severity":"medium","status":"resolved","area":"citation",
  "title":"Eleven cross-references pointed at rows that exist and say something else",
  "detail":("Found while merging with main and by reading the registers against the documents they cite. Five guides - counter-space, dual-versus-single basket, "
   "how to read a listing, the preset guide and the chicken-breast guide - cite S22 for Chefman specification figures, but S22 in this register is the FTC "
   "Endorsement Guides page; those figures come from S23 (the maker's page for RJ38-SQSS-8T) and, for the matte-black High-Fry unit, S12. FLG-006 and FLG-007 "
   "credited S11, a Chefman product page, with the declared-site rule and the 'at least 10 posts' rule of thumb, which both live in S19, and the workflow page "
   "carried the same wrong id. FLG-012 credited S12 with support for the ASIN definition. FLG-014 quoted a byline string the config has not held since the rename. "
   "DESIGN-BRIEF PB-4 blocks on the house-style row but cites S-20, which is crawl control; the house-style row is S-19. And the chicken-breast guide cited S11 and "
   "S23 inline without declaring either in its own source list. All eleven corrected on 2026-11-20, and the last one was caught by the gate rule written for this "
   "class the moment it ran. Recorded together for one reason: every one of these ids resolves to a row that exists, so a check limited to existence passes all of "
   "them. The rules that do catch it now live in tools/verify.mjs - an inline citation must be declared by the guide that uses it, and a sentence carrying a "
   "measurement may not cite a policy or consumer-advice page (S-35)."),
  "impact":"A source id is the whole evidentiary claim of a row. Pointing a reader from a wattage figure to an FTC disclosure page is worse than no citation, because it looks like one.",
  "resolution":"Corrections and both gate rules by session b7320829-affil3 on 2026-11-20, in the merge commit that resolves the branch.",
  "manual_step":"If those guide figures are re-checked, compare against S23 and S12 - never S22.",
  "sources":["S22","S23","S12","S19","S11"]},
 {"id":"FLG-045","severity":"low","status":"resolved","area":"editorial",
  "title":"This session's five new guides would have duplicated pages that landed on main first",
  "detail":("Cut from 7fac552, where the shelf held five guides, this session drafted five more: dishwasher-safe parts, reading thermometer certification labels, "
   "what Sync Finish and Hi-Fry do, how to read a preset list, and holiday capacity planning. main published eleven more in the meantime, and four of the five "
   "drafts covered ground its pages already own - the cleanup guide already reads dishwasher claims, the preset guide already runs the 24-versus-25 comparison, "
   "the holiday guide already plans a big meal on a small counter, and the listing guide already teaches listing-versus-maker checking. Publishing both sets would "
   "have produced near-duplicate pages on one domain, the pattern Google's spam policies call scaled content abuse (S09) and the pattern FLG-032 already reproaches "
   "this repository for. Resolution: one guide ships (Sync Finish and Hi-Fry, whose subject - what the named buttons do, and the disputed 450 °F ceiling - no other "
   "page answers), and even that page had its basket-shape paragraph cut to a cross-reference because the dual-basket guide owns that argument. The first-hand "
   "material from the other four was merged into the existing pages as new sections carrying their own sources and dated 'amended' notes. Convergence recorded in the "
   "same pass rather than re-filed: the stray degree sign in P01's function list, the stale 'fifth link resolves to nothing' executive summary and the /docs/ row in "
   "the README had all been fixed on main first, and the unreproducible short-link fetches are main's FLG-036 and FLG-037."),
  "impact":"Had the merge been a concatenation, the site would have published twins about the same appliances while arguing in its own flag board that the editions' twins are a problem.",
  "resolution":"Resolved in the merge commit by session b7320829-affil3 on 2026-11-20: five drafts became one page plus three enriched pages; one unused illustration was deleted.",
  "manual_step":"None. If the withdrawn topics are revisited, check the shelf first: presets, holiday planning, cleanup and listing-reading all have an owner page already.",
  "sources":["S09"]},
]
F.extend([x for x in NEWF if x['id'] not in fb])
fd['note'] = (fd.get('note','') + " FLG-043 to FLG-045 were added by session b7320829-affil3 on 2026-11-20, renumbered as main took the earlier ids "
 "while this branch was open; FLG-006, FLG-007, FLG-012, FLG-014 and FLG-032 carry corrections from the same pass.")
json.dump(fd, open('data/flags.json','w'), indent=2, ensure_ascii=False); open('data/flags.json','a').write('\n')

# ============================================================== questions
qd = json.load(open('data/questions.json'))
K = [
 {"id":"K-23","statement":"Four dated rounds have read the five observed listings. Each round that reached the pages matched the register's titles; the most recent (2026-11-20, session b7320829-affil3) could not reach amazon.com at all and re-derived nothing, and is recorded as a failed round rather than as agreement.","sources":["S04","S05"]},
 {"id":"K-24","statement":"robots.txt is not an exclusion mechanism, and noindex cannot live in robots.txt: both sentences are read verbatim from Google's documentation, held here as S24 and S26; and Google reads robots.txt from the host root, which FLG-038 established for this project path.","sources":["S24","S25","S26"]},
 {"id":"K-25","statement":"The shelf publishes 17 guides, 7 Journal articles and 5 product rows across 3 clusters, so the 'at least 10 posts' rule of thumb is met on page count alone. Whether a reviewer calls the content robust is not something a count can answer.","sources":["S19"]},
 {"id":"K-26","statement":"The submitted short links are not usable as the site's outbound route: in the latest round four of four that resolved at all landed on the Amazon home page. The site publishes its own tagged /dp/ links for that reason, and not because the short links were declared invalid.","sources":["S05","S04"]},
]
Q = [
 {"id":"Q-23","question":"What counts as a page for the 10-post threshold, and who decides the site is ready to submit?",
  "have":"17 guides, 7 Journal articles and 5 product rows; S19's wording, read from an excerpt; FLG-007 open since the first pass.",
  "lack":"Amazon's answer, and a decision to submit.","who":"The owner, in a signed-in Associates session.",
  "why_it_matters":"A count is not a pass and page count is not content quality; submitting early with thin pages risks the account review for no gain.",
  "how_to_close":"Read S19 signed-in, decide, submit, and record the outcome with its date. That closes FLG-007.","blocking":True,"sources":["S19"]},
 {"id":"Q-24","question":"Will each buy link be replaced by a Special Link generated in Associates Central, and when?",
  "have":"Five constructed tagged links (observed ASIN + tag), the Program Policies clause they satisfy (S02), and gate G-02 saying none has been tested.",
  "lack":"A link issued by Amazon for each product, and one confirmation that the click lands in the tracking report.",
  "who":"The owner, in Associates Central. No agent can do this from the repository.",
  "why_it_matters":"This is the difference between a site built to earn and a site that looks ready to. Everything else is presentation.",
  "how_to_close":"S-02 option D: generate one link per product, paste it into the row's special_link field with its date, re-run the gate.","blocking":True,"sources":["S01","S02"]},
 {"id":"Q-25","question":"Who re-checks listing copy, and where is that record kept?",
  "have":"A per-product observed date, four dated rounds, and one round that failed to reach the source at all.",
  "lack":"An owner and a cadence for a ten-minute check, and a field on the product row for its result.",
  "who":"The owner, or the editorial team once one exists (Q-06).",
  "why_it_matters":"Titles, included accessories and prices change without notice on the retailer's side; the site publishes the wording it saw with a date on it, so the date has to stay near the truth.",
  "how_to_close":"S-34 option B: one short monthly pass into data/observations/ with its date, rendered as a last-seen line on the product page.","blocking":False,"sources":["S04","S03"]},
]
D = [
 {"id":"D-19","suggestion":"Fetch each published edition's index.html once and write down whether it carries a noindex meta tag, then compare what you find with what FLG-032 claims. Two minutes, and it turns a findability argument into a checked fact.","closes":["Q-17"]},
 {"id":"D-20","suggestion":"In Associates Central, generate one Special Link per product, paste it into the product row with its generation date, then click it once and confirm the click in the tracking report. That sequence closes Q-01, Q-02 and Q-24 together.","closes":["Q-01","Q-02","Q-24"]},
 {"id":"D-21","suggestion":"Run a ten-minute monthly listing re-check: open each tagged link in a signed-in browser, compare the title and the included-accessory wording with the row, and write the outcome into data/observations/ with its date.","closes":["Q-25"]},
 {"id":"D-22","suggestion":"Write to manufacturer support for the disputed figures (P03 wattage and case size, P02 preset and accessory counts, P05 battery hours and probe working temperature). A one-line reply from the brand is an official source; a forum post is not and will not be used.","closes":["Q-11","Q-12","Q-20"]},
]
for key, rows in (('known',K),('unknown',Q),('discovery',D)):
    ids = {x['id'] for x in rows}
    qd[key] = [x for x in qd[key] if x['id'] not in ids] + rows
qd['note'] = (qd.get('note','') + " Q-23 to Q-25, K-23 to K-26 and D-19 to D-22 were added by session b7320829-affil3 on 2026-11-20, after a round that read "
 "seven official pages first-hand and merged this branch with main; two of the three new questions close in one sitting in Associates Central.")
json.dump(qd, open('data/questions.json','w'), indent=2, ensure_ascii=False); open('data/questions.json','a').write('\n')

# ============================================================== suggestions
sd = json.load(open('data/suggestions.json')); SG = sd['suggestions']
for x in SG:
    if x['id'] == 'S-02':
        ids = {o['id'] for o in x['options']}
        if 'D' not in ids:
            x['options'].append({"id":"D","label":"Keep A, and give every product row a special_link field: the moment a link is generated in Associates Central it is pasted there with its date, and the build prefers it over the constructed URL.","tradeoff":"Recommended by session b7320829-affil3. One test per product, no downtime, and the link a reader clicks becomes the link Amazon issued rather than the link we assembled. The register then holds both, dated, and the difference between them stays visible.","effort":"20 minutes per product","risk":"low"})
        if 'b7320829' not in (x.get('recommendation') or ''):
            x['recommendation'] = ((x.get('recommendation') or '') + " Session b7320829-affil3 adds option D: it changes no copy on the site and makes the tested link the one that renders.").strip()
NEW = [
 {"id":"S-32","track":"trust","topic":"Answer-first summaries on every guide",
  "problem":"A guide that buries its answer under four headings is a guide a reader leaves, and a page a reader leaves is a page a search engine discounts. The brief's 'not AI slop' instruction is answered by giving the answer plainly, with its sources, before the argument - not by decoration.",
  "current":"B",
  "options":[{"id":"A","label":"Leave the deck as the only above-the-fold summary.","tradeoff":"The deck is a teaser by design, so the answer arrives later. Nothing to maintain.","effort":"none","risk":"medium"},
   {"id":"B","label":"Add a 'summary' field per guide, rendered as a boxed short answer under the byline, and compute the word and minute count from the guide's own text at build time.","tradeoff":"Implemented 2026-11-20 for all seventeen guides. Each guide needs a short honest answer written for it, which also catches a guide that has no answer to give. The reading figure is the page's word count over 225 words a minute - a property of the text, not a measurement of the reader.","effort":"done","risk":"low"}],
  "recommendation":"B, shipped. If a guide cannot be summarised in four sentences, that is a finding about the guide, not about the format.",
  "depends_on":["S-19"]},
 {"id":"S-33","track":"findability","topic":"How much structured data to publish",
  "problem":"The shelf emits Article on guides and Product on product pages. Question-shaped guides with questions and answers on the page, and a hierarchy under one root, are both describable in machine-readable form - the cheapest findability lever available that needs no owner action and no host access, unlike the robots.txt problem in S-20.",
  "current":"B",
  "options":[{"id":"A","label":"Article only (as shipped before 2026-11-20).","tradeoff":"Minimal and valid; nothing about site structure or the Q&A content is declared.","effort":"none","risk":"low"},
   {"id":"B","label":"An @graph per guide: Article (with wordCount, articleSection, inLanguage) + BreadcrumbList, plus FAQPage where the guide carries questions and answers on the page.","tradeoff":"Implemented 2026-11-20. It buys machine-readable structure, not a rich result: Google shows FAQ rich results mainly for well-known authoritative sites, so this is stated as structure rather than as a SERP promise.","effort":"done","risk":"low"},
   {"id":"C","label":"Add Product offers and price data.","tradeoff":"Not available while the site publishes no prices: the price clause (S03) and the no-republished-prices rule both stand until the Creators API decision at S-04.","effort":"blocked","risk":"high"}],
  "recommendation":"B, shipped, and not sold as a rich-result win. C waits for an API enrolment decision.",
  "depends_on":["S-04","S-20"]},
 {"id":"S-34","track":"trust","topic":"A dated re-check ritual for listing copy",
  "problem":"Four rounds have read the five listings; three matched, and the fourth could not reach the site at all. Listing titles, accessories and prices change without notice, and this site publishes the wording it saw with a date on it. That is honest, but it quietly ages - and an automated check cannot do the job, because unauthenticated fetches of Amazon fail or land on the home page (FLG-036, FLG-037).",
  "current":"B",
  "options":[{"id":"A","label":"Leave the dated reads as they are and let the dates speak.","tradeoff":"Zero work. A reader sees 'observed November 20, 2026' and can judge staleness themselves.","effort":"none","risk":"low"},
   {"id":"B","label":"A monthly ten-minute manual re-check, written into data/observations/ with its date and rendered on the product page as a last-seen line.","tradeoff":"Recommended. It is the only check that sees the page a shopper sees, and it needs a person - which is why it is a suggestion and not an automation claim.","effort":"10 minutes a month","risk":"low"},
   {"id":"C","label":"Automate the fetch in CI.","tradeoff":"Rejected on this repository's own evidence: a scheduled job would raise a flag every week for reasons unrelated to the fact it claims to verify. Do not build an alarm nobody can trust.","effort":"hours","risk":"high"}],
  "recommendation":"B, and explicitly not C. The same logic that keeps gate G-02 manual keeps this manual: a check that fails for the wrong reason is worse than no check.",
  "depends_on":["FLG-037","S-21"]},
 {"id":"S-35","track":"platform","topic":"A citation check that catches wrong meaning, not just a dangling id",
  "problem":"Eleven cross-reference defects shipped in this repository before anyone noticed, because every id involved resolved: five guides cited the FTC endorsement page for Chefman wattage figures, two flags credited a Chefman product page with Amazon's application-review text, a byline sentence named a team the config had already renamed, a design-brief row blocked on the wrong suggestion, and one guide used source ids it never declared. None of that is catchable by an existence check, and traceability is the whole claim this site makes about itself.",
  "current":"C",
  "options":[{"id":"A","label":"Rely on reviewers noticing.","tradeoff":"Eleven were missed across several sessions and found only by reading text against the documents it cites.","effort":"none","risk":"medium"},
   {"id":"B","label":"Gate rule: every S-id, FLG-id, S-nn, Q-id, K-id and D-id inside a register string or a rendered page must resolve to a real row.","tradeoff":"Implemented 2026-11-20. It catches the dangling-reference class and nothing else, because a mis-numbered but existing id still passes it.","effort":"done","risk":"low"},
   {"id":"C","label":"Two further rules, implemented with B: an inline citation in a guide must be declared in that guide's own source list, and a sentence carrying a measurement (W, °F, qt, lb, in, litres, presets) may cite only a maker, an observed retailer page or USDA - never a policy, disclosure or developer page.","tradeoff":"Implemented 2026-11-20 in tools/verify.mjs; this is the pair that catches 'Chefman states 1700 W (S22)'. It can flag a legitimate comparison that quotes a regulator, and the answer then is to cite the regulator properly rather than to loosen the rule.","effort":"done","risk":"low"},
   {"id":"D","label":"Also require every guide sentence to carry an inline source id.","tradeoff":"Maximum auditability, and every guide reads like a filing. The source list plus the product-page grid already do this job where the facts live.","effort":"hours","risk":"medium"}],
  "recommendation":"B and C, shipped. Prose stays readable; the wiring gets tested. D stays rejected for the reason above. Recorded as FLG-044.",
  "depends_on":["FLG-044","S-19"]},
]
ids = {x['id'] for x in SG}
sd['suggestions'] = SG + [x for x in NEW if x['id'] not in ids]
seq = sd['sequence']; have = {x['id'] for x in seq}
sd['sequence'] = seq + [{"order": len(seq)+1+i, "id": s, "why": w} for i,(s,w) in enumerate([
 ("S-32","Shipped with this merge: answer-first summaries and computed reading stats on all seventeen guides."),
 ("S-33","Shipped: Article + BreadcrumbList + FAQPage graph. Do not expect rich results from it."),
 ("S-34","The only check that sees what a shopper sees, and deliberately manual (FLG-036, FLG-037)."),
 ("S-35","Shipped: eleven mis-citations was the evidence; the gate now tests meaning, not just existence."),
]) if s not in have]
sd['note'] = (sd.get('note','') + " S-32 to S-35 continue main's board after the 2026-11-20 merge, renumbered because main took this session's draft ids "
 "while the branch was open. Three were implemented by session b7320829-affil3 in that merge and are listed here for reversal as well as approval. This session's "
 "de-indexing proposal was folded into main's S-20 and its Special-Link field became option D of main's S-02, for the same reason the board exists: one row per decision.")
json.dump(sd, open('data/suggestions.json','w'), indent=2, ensure_ascii=False); open('data/suggestions.json','a').write('\n')

# ============================================================== products + design brief
pd = json.load(open('data/products.json'))
pd['checked'] = "2026-11-20 (fourth dated round; see data/observations/)"
VN = {
 "P01":("Re-read 2026-11-20 (session b7320829-affil3) against the manufacturer page: model RJ38-SQPF-3TDB-2W, 'Max temp: 450ºF/ 235ºC with Hi-Fry function' "
   "and the Sync Finish wording all match this row. The listing itself could not be fetched in that round, so its observed fields are carried from the dated "
   "rounds that read them (FLG-036, FLG-037)."),
 "P02":("Re-read 2026-11-20 (session b7320829-affil3): the manufacturer page's specification strip and description were fetched and every figure on this row - "
   "26 qt / 24.6 L, food for 4-6 people, 16.9 x 15.8 x 14.8 in, 120 V, model 4-00675-02A-VN - matched. The page states no washing claim, and the preset "
   "disagreement in FLG-024 was confirmed again first-hand (FLG-042)."),
 "P04":("Re-read 2026-11-20 (session b7320829-affil3): the ThermoMaven F1 Ace page states NIST-certified ±0.5 °F / ±0.3 °C, a one-second thermocouple read, "
   "a 100% waterproof design, a built-in magnet and a lifetime warranty that must be activated within 30 days. It names no model correspondence with the listing "
   "title and no IP rating, so FLG-025 stays open and the listing's IP67 wording is left unattributed to the maker."),
}
for p in pd['products']:
    if p['id'] in VN: p['verification_note'] = VN[p['id']]
json.dump(pd, open('data/products.json','w'), indent=2, ensure_ascii=False); open('data/products.json','a').write('\n')

dp='data/design-brief.json'; dd=json.load(open(dp))
dd['amended']=("Amended 2026-11-20 by session b7320829-affil3 during the merge with main: PB-4 blocked on 'S-20' for the house style file, but on main's board "
 "S-20 is crawl control and the house-style row is S-19. Both ids resolve, so an existence check would never have caught it (FLG-044). The reference is corrected to "
 "S-19; the PB-4 guide-count wording is stale in the useful direction, since the shelf now publishes seventeen guides. Nothing else here was rewritten - this is a "
 "plan written on a date, and it reads as one.")
json.dump(dd, open(dp,'w'), indent=2, ensure_ascii=False); open(dp,'a').write('\n')
print('registers applied; flags/suggestions/questions renumbered past main')
