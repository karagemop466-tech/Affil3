import json, re

# ---------------------------------------------------------------- guides
d = json.load(open('data/guides.json')); G = d['guides']; by = {g['slug']: g for g in G}

# 1. S22 (FTC page) was cited by five guides for Chefman figures: the right rows are S23 and S12.
for g in G:
    t = json.dumps(g, ensure_ascii=False)
    if 'S22' not in t or g['slug'] == 'sync-finish-and-hi-fry-what-the-buttons-do':
        continue
    t = t.replace('(S12, S22)', '(S12, S23)').replace('(S11, S22)', '(S11, S23)').replace('S22', 'S23')
    g2 = json.loads(t); g2['sources'] = list(dict.fromkeys(g2['sources']))
    g2['amended'] = ((g2.get('amended') or '') + ' Inline citation corrected 2026-11-20 by session b7320829-affil3: this page cited S22 for Chefman specifications, but S22 in this register is the FTC Endorsement Guides page; the figures come from S23, and the matte-black High-Fry unit stays S12 (FLG-044).').strip()
    G[G.index(g)] = G[G.index(g)] if False else g2
by = {g['slug']: g for g in G}
chick = by.get('air-fryer-chicken-breast-how-do-you-know-it-is-done')
if chick: chick['sources'] = list(dict.fromkeys(chick['sources'] + ['S11', 'S23']))

NEWGUIDE = {
 "slug": "sync-finish-and-hi-fry-what-the-buttons-do",
 "title": "Sync Finish and Hi-Fry: what the buttons do",
 "category": "air-fryers",
 "cluster_links": ["air-fryer-ovens"],
 "image": "/assets/img/guide-dual-basket-controls.png",
 "image_alt": "Illustration of a dual-basket air fryer control panel with two blank displays and a row of round touch controls",
 "date": "2026-11-20",
 "deck": "Dual-basket machines sell themselves on three named features. Two are about timing, one is about temperature, and none of them is about how well food cooks.",
 "description": "What Sync Finish, Hi-Fry and independent baskets mean on the Chefman dual-basket air fryer, read from the manufacturer page and the Amazon listing, including the disputed temperature ceiling on the 8 qt model.",
 "summary": "Sync Finish is a timing feature - the machine starts one basket later so two foods land together - and it does not equalise temperature or method between the sides. Independent baskets buy two temperatures and two timers, but each chamber stays 3 quarts. And the 450 °F Hi-Fry ceiling is stated for the dual-basket model only: the same brand's 8 qt page states 200-400 °F, so the higher claim is named and flagged rather than adopted.",
 "sources": ["S04", "S11", "S12", "S16", "S23"],
 "body": [
  {"type": "p", "text": "Feature names on an appliance panel are marketing sentences compressed into two words. Unpack them and you get a much better idea of whether a machine suits how you actually cook. Three names carry almost all the weight on the dual-basket unit we track, and each one means less than the button suggests."},
  {"type": "p", "text": "The Chefman page for this model describes a 6-quart air fryer that \u201ccombines two powerful air fryers in one, allowing you to cook different dishes simultaneously or easily switch between baskets\u201d. The Amazon listing title is more specific: two independent 3-quart baskets. Whether that shape suits your week at all is a separate question, answered on its own page; this one is about what the named buttons actually do."},
  {"type": "h2", "text": "Sync Finish is a timing feature, not a cooking feature"},
  {"type": "p", "text": "The manufacturer describes a Sync Finish feature \u201cto ensure both baskets finish cooking simultaneously\u201d. That is the whole promise: the machine manages when one side starts so two foods land on the table together. It does not equalise temperature between the sides, it does not make a chicken thigh and a tray of fries cook alike, and it will not rescue a dish that needed a different technique. If your Tuesday problem is two things, one plug, same table, it is aimed squarely at that. If your problem is even browning across one large batch, it is not."},
  {"type": "h2", "text": "Hi-Fry is a number, and the number is disputed"},
  {"type": "p", "text": "On the dual-basket page the manufacturer states a maximum of 450 \u00b0F (235 \u00b0C) with the Hi-Fry function, and the listing title lists Hi-Fry among the features. On the 8 qt single-basket Chefman the two documents part company: the maker's page for the model the listing names (RJ38-SQSS-8T) states 200-400 \u00b0F, while the Amazon title advertises a 450 \u00b0F Hi-Fry option - and 450 \u00b0F is what the maker states for a different 8 qt unit, the TurboFry Touch with High Fry. A headline can be a promise about a product family; a specification block is a claim about one unit. This site publishes the 400 \u00b0F figure for that model and leaves the title's 450 \u00b0F claim named but unadopted (FLG-027). When two official pages conflict, the conservative figure goes on the page and the conflict goes in the register."},
  {"type": "table", "headers": ["Feature", "Who states it", "What it changes about your cooking", "What it does not change"],
   "rows": [
    ["Sync Finish", "Manufacturer page and listing title", "Whether two foods land at the same time", "Whether both foods are cooked the same way"],
    ["Two independent 3 qt baskets", "Listing title; the maker's page states the 6 qt total", "Whether you can run two temperatures at once", "Total capacity: 3 + 3 is not one 6 qt chamber"],
    ["Hi-Fry to 450 \u00b0F", "Manufacturer page for the dual-basket model", "The upper temperature ceiling on that model", "Nothing on the 8 qt model, whose page states 200-400 \u00b0F (FLG-027)"],
    ["Easy-view windows", "Listing title", "Whether you check food by looking instead of by opening", "Crispiness, which still comes from air flow, temperature and time"],
    ["Auto shutoff", "Listing title", "What happens if you forget it is running", "The need to check doneness with a thermometer"],
   ]},
  {"type": "h2", "text": "Three questions to ask of any dual-basket listing"},
  {"type": "ol", "items": [
    "What is the capacity of one basket, not of the pair? Compare a single batch against a single chamber, not against a total.",
    "Which page states the temperature ceiling - the maker's specification or the listing title? If they differ, the difference belongs in your decision, not in a footnote.",
    "Is there a care statement about the baskets - nonstick, dishwasher-safe, top rack only? Washing is part of the daily cost of owning this shape, and it is a separate claim from the cooking one.",
  ]},
  {"type": "note", "text": "No appliance was operated to write this guide. Every feature sentence above is a statement from a manufacturer page or from the observed Amazon listing, and the two are attributed separately because they are not always the same sentence."},
  {"type": "faq", "items": [
    {"q": "Do I need Sync Finish if I can set a timer myself?", "a": "You can do the same arithmetic by hand. The feature saves you starting one side late and watching two countdowns, which on a busy evening is most of its value."},
    {"q": "Is Hi-Fry worth paying for?", "a": "That cannot be answered from these pages, because they state what the function is - a higher temperature ceiling - and not how it performs. We do not publish a performance opinion we cannot source."},
    {"q": "Can a dual-basket unit replace a single big drawer for a family?", "a": "Only if your batches fit in 3 quarts each. For one large single item, the 8 qt single-basket shape exists for exactly that reason, which is why both shapes stay on our shelf."},
  ]},
  {"type": "cta", "text": "The two Chefman rows sit side by side in the comparison table, with each figure traced to the page that states it.", "label": "Compare them in one table", "href": "/compare/"},
 ],
 "verification": "Written 2026-11-20 from the manufacturer pages fetched that day and the listing wording recorded in the dated register.",
}
if NEWGUIDE['slug'] not in by:
    G.append(NEWGUIDE)

def splice(slug, anchor_prefix, blocks, before=False):
    g = by.get(slug)
    if not g: print('guide missing, skip:', slug); return
    body = g['body']
    for i, b in enumerate(body):
        if b.get('text', '').startswith(anchor_prefix):
            j = i if before else i + 1
            body[j:j] = blocks
            return
    print('anchor missing in', slug)

splice('how-to-assess-cleanup-and-counter-space-tradeoffs', 'The counter-space questions', [
 {"type": "h2", "text": "What the pages actually say, quoted"},
 {"type": "p", "text": "The paragraph above paraphrases. Here is the same evidence in the pages' own words, because the difference between \u201cbaskets\u201d and \u201cbasket and rack, top rack\u201d is the whole point of reading carefully. Manufacturer pages re-read 2026-11-20."},
 {"type": "table", "headers": ["Product", "What the official page states", "Whose words those are"],
  "rows": [
   ["CHEFMAN 6 Qt dual basket", "The listing title itself carries \u201c2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets\u201d. The claim covers the baskets.", "Amazon listing title; the maker's page for the model states the same for its nonstick baskets"],
   ["Chefman TurboFry 8 Qt (RJ38-SQSS-8T)", "\u201cTop-rack dishwasher safe\u201d, basket and rack. The rack position is part of the claim, not a detail.", "Chefman product page for that model"],
   ["Emeril Lagasse 26 QT French Door", "No washing statement at all in the parts of the manufacturer page this site reads: capacity, presets, fan, dimensions and voltage, nothing about cleaning.", "Emeril Everyday product page"],
   ["ThermoMaven 1 Sec probe", "\u201cFeaturing a 100% waterproof design, this device easily withstands spills and scrubbing.\u201d Waterproof, yes. Dishwasher, not stated.", "ThermoMaven product page"],
   ["CHEF iQ Sense probes", "The maker states the probes are waterproof and dishwasher safe. A rating for sustained heat inside a cooker is a different claim and not the same permission.", "CHEF iQ product page"],
  ]},
 {"type": "p", "text": "Two of these rows are the same shape of sentence doing different work: \u201cwaterproof\u201d describes water reaching the device, \u201cdishwasher safe\u201d describes heat, detergent and spray. A maker that states the first has not stated the second, and the reader who conflates them is the one left with a fogged display after one cycle. Where a page is silent, this site publishes silence rather than an inference."},
 {"type": "img", "src": "/assets/img/guide-dishwasher-safe.png",
  "alt": "Illustration of two dark nonstick air fryer baskets sitting on the upper rack of an open dishwasher, with a folded towel beside it",
  "caption": "Editorial illustration, not a photograph of a tested product."},
], before=True)
by['how-to-assess-cleanup-and-counter-space-tradeoffs']['sources'] = list(dict.fromkeys(by['how-to-assess-cleanup-and-counter-space-tradeoffs']['sources'] + ['S11', 'S13', 'S14', 'S21', 'S23']))
by['how-to-assess-cleanup-and-counter-space-tradeoffs']['amended'] = ((by['how-to-assess-cleanup-and-counter-space-tradeoffs'].get('amended') or '') + ' Statement grid added 2026-11-20 by session b7320829-affil3 from that session\'s first-hand re-reads of the Chefman, Emeril and ThermoMaven pages; it replaces a standalone guide drafted on the same question, withdrawn as a duplicate (FLG-045).').strip()

splice('air-fryer-presets-how-many-do-you-need', 'Twenty-five sounds like versatility', [
 {"type": "h3", "text": "The same page, two counts"},
 {"type": "p", "text": "The table above takes the Emeril oven's figure from its specification strip: 25 cooking pre-sets. The description on that same manufacturer page calls the machine a 10-in-1 air fry convection oven, and the Amazon listing title reads \u201c24 One-Touch Preset Options\u201d, while an image on the manufacturer page records an eleven-function count. Four figures from two official pages about one machine, each published somewhere the brand controls - which is why a preset total is a number to read with its source named, and why nothing on our product page states a preset or accessory count as settled fact. The disagreement is recorded and dated as FLG-024."},
 {"type": "img", "src": "/assets/img/guide-preset-buttons.png",
  "alt": "Illustration of a countertop oven control panel with a row of blank preset buttons under a blank display",
  "caption": "Editorial illustration, not a photograph of the appliance."},
])
by['air-fryer-presets-how-many-do-you-need']['sources'] = list(dict.fromkeys(by['air-fryer-presets-how-many-do-you-need']['sources'] + ['S13']))
by['air-fryer-presets-how-many-do-you-need']['amended'] = ((by['air-fryer-presets-how-many-do-you-need'].get('amended') or '') + ' Worked example added 2026-11-20 by session b7320829-affil3 from a first-hand re-read of the Emeril manufacturer page; it replaces a standalone guide drafted on the same question, withdrawn as a duplicate (FLG-045).').strip()

splice('how-to-read-an-amazon-listing-before-you-buy-a-kitchen-appliance', 'The five-minute check, in order', [
 {"type": "h2", "text": "Sidebar: what the certification acronyms do and do not claim"},
 {"type": "table", "headers": ["Claim on the page", "Where it appears", "What it actually covers"],
  "rows": [
   ["NIST-certified, \u00b10.5 \u00b0F / \u00b10.3 \u00b0C", "ThermoMaven product page", "The instrument's certified accuracy against a reference. It says nothing about technique."],
   ["Typical accuracy 2 to 4 \u00b0F", "USDA FSIS food thermometer factsheet", "What most food thermometers deliver in a kitchen - a different kind of number from a laboratory certificate."],
   ["1 second, thermocouple", "ThermoMaven product page", "Response time and sensor type: how fast a number appears."],
   ["IP67", "An Amazon listing title; not in the maker's page text this site read", "An ingress-protection rating defined by a standard outside this site's allowed source list, so it is left untranslated here."],
   ["NSF Certified", "The same listing title; the maker's page shows certification marks as images", "Which NSF programme, unconfirmed."],
   ["Lifetime warranty", "ThermoMaven product page, with a 30-day activation window", "A service promise with a condition attached, not an unconditional one."],
  ]},
 {"type": "p", "text": "Two habits fall out of that grid. Read an accuracy figure next to USDA's expectation for the category rather than on its own: the half-degree certificate and the two-to-four-degree kitchen reality are both true, and the second is the number you cook with. And when a listing states something the maker's page does not - an IP rating, a certification scope - treat it as the retailer's claim and go looking for the document behind it. This site publishes both statements and no interpretation of its own, because an inferred number is a fabricated number with better posture."},
 {"type": "img", "src": "/assets/img/guide-thermometer-labels.png",
  "alt": "Illustration of a folding instant-read thermometer beside a magnifying glass hovering over a blank specification label",
  "caption": "Editorial illustration, not a photograph of a product."},
], before=True)
by['how-to-read-an-amazon-listing-before-you-buy-a-kitchen-appliance']['sources'] = list(dict.fromkeys(by['how-to-read-an-amazon-listing-before-you-buy-a-kitchen-appliance']['sources'] + ['S10', 'S20', 'S21']))
by['how-to-read-an-amazon-listing-before-you-buy-a-kitchen-appliance']['amended'] = ((by['how-to-read-an-amazon-listing-before-you-buy-a-kitchen-appliance'].get('amended') or '') + ' Certification sidebar added 2026-11-20 by session b7320829-affil3 from the ThermoMaven page and the two USDA FSIS pages, all re-read in that session; it replaces a standalone thermometer-label guide drafted the same day, withdrawn as a duplicate (FLG-045).').strip()

SUM = json.load(open('/dev/stdin')) if False else {
 "basket-or-oven-style-air-fryer-what-should-you-compare": "Choose from the meal, not from the box. A basket drawer is one shakeable layer that suits frozen and crisp foods for a small household; an oven-style unit buys rack positions and a door at the cost of counter depth and more pieces to wash. Four questions settle it in about a minute.",
 "no-hype-checklist-comparing-air-fryer-capacity": "Quarts are not comparable across shapes: one 6-quart figure can be two 3-quart baskets or one 6-quart drawer, and a maker's quart count says nothing about the food you can actually fit. Read the chamber shape, the maker's own serving line and the outside dimensions, and treat a capacity claim with no source as a marketing number.",
 "how-to-assess-cleanup-and-counter-space-tradeoffs": "The two daily costs of an air fryer are the pieces you wash and the counter it occupies. Count the parts that touch grease before you fall for the capacity, measure the outside box rather than the advertised volume, and read a dishwasher claim narrowly: it names the parts it covers and says nothing about the rest.",
 "questions-to-ask-before-buying-a-multi-function-kitchen-appliance": "A multi-function appliance pays for itself only if you use more than one of its functions. Ask which modes carry a stated temperature range, which ones you would have used last month, and whether the panel lets you set time and heat by hand - that decides whether it replaces two appliances or adds one more.",
 "is-your-meat-thermometer-telling-you-the-right-number": "A thermometer is only as good as where you put it. USDA's guidance is to place it in the thickest part away from bone, fat and gristle, to check a large roast in several places, and to cook to the minimum internal temperature: 165 \u00b0F for all poultry, 160 \u00b0F for ground meats, 145 \u00b0F with a three-minute rest for whole-muscle beef, pork, veal and lamb.",
 "how-much-counter-space-does-an-air-fryer-really-need": "The number that decides the purchase is not the capacity on the box but the outside footprint plus the clearance the maker asks for. Measure the space, add the room a drawer takes when it is open or a door takes when it swings, and check it against the footprints published for the three countertop appliances on this shelf.",
 "dual-basket-or-single-basket-air-fryer": "Two baskets buy you two temperatures and two timers, and cost you batch size: two 3-quart chambers are not one 6-quart chamber. If your problem is two foods landing at the same time, dual wins; if it is one large single item, a big drawer is the right shape.",
 "air-fryer-toaster-oven-or-microwave-which-one-earns-counter-space": "These three machines solve three different problems, and most kitchens need two of them at most. Start from the job you actually hate doing by hand - crisping, baking a whole tray, or reheating a plate - and let the shape follow; then count what each one costs you in counter space, cleaning and attention.",
 "instant-read-or-leave-in-probe-which-thermometer-do-you-need": "An instant-read probe is a spot check you perform; a leave-in wireless probe watches a long cook from another room. Buy the first if you check food at the end of a cook, the second if the cook is long enough that leaving it is the point - and read what each maker's specification actually promises before paying for features you will not use.",
 "how-to-read-an-amazon-listing-before-you-buy-a-kitchen-appliance": "A listing title is written to sell and the specification block is written to describe, so open the maker's page first and compare the four numbers that change the purchase: model, temperature range, power and dimensions. Where the two documents disagree, the disagreement is the finding - this site publishes both readings rather than a reconciled one.",
 "holiday-hosting-on-a-small-counter-a-plan-for-the-big-meal": "Plan the cooking before you choose the appliance: give the main heat the space it needs, run the sides and reheats through the second device, and treat the thermometer as part of the plan rather than an accessory, because the safe internal temperatures do not change with the machine you used.",
 "air-fryer-presets-how-many-do-you-need": "A preset count is a marketing number: nothing standardises what counts as a preset, and one machine on this shelf states its own count four different ways across two official pages. Compare capacity, the maker's serving line, fan behaviour, outside size and named accessories instead, then check whether you can set time and temperature by hand in two presses.",
 "air-fryer-chicken-breast-how-do-you-know-it-is-done": "Colour tells you it looks right; only a thermometer tells you it is safe. Cook chicken to 165 \u00b0F as measured with a food thermometer, in the thickest part, and read why opacity and juices mislead on this cut in particular before you trust the eye test.",
 "black-friday-kitchen-deals-a-shoppers-checklist": "A discount does not change what a machine is. Decide your number before the countdown - the capacity you actually need, the counter space you actually have, the parts you will actually wash - then check which offer the price belongs to and what the return window says. This site publishes no prices, so the checklist is the whole advice.",
 "which-air-fryer-shape-fits-your-week": "Three shapes cover almost every kitchen: a single basket for one shakeable batch, a dual basket for two foods at two temperatures landing together, and an oven-style unit for racks and a whole tray. Find the week you actually cook and the shortlist narrows itself, with no editor's-choice badge involved.",
 "smart-meat-thermometer-what-actually-matters": "Wireless range, probe count and app promises are specs that matter only if the cook is long enough to need them. The short list is whether the probe is rated for the heat it sits in, what the maker states about the ambient sensor, and whether you can read the number at all - the rest is a gadget drawer.",
 "sync-finish-and-hi-fry-what-the-buttons-do": "Sync Finish is a timing feature - the machine starts one basket later so two foods land together - and it does not equalise temperature or method between the sides. Independent baskets buy two temperatures and two timers, but each chamber stays 3 quarts. And the 450 \u00b0F Hi-Fry ceiling is stated for the dual-basket model only: the same brand's 8 qt page states 200-400 \u00b0F, so the higher claim is named and flagged rather than adopted.",
}
missing = [g['slug'] for g in G if g['slug'] not in SUM]
if missing: raise SystemExit('no summary for ' + ', '.join(missing))
for g in G:
    g['summary'] = SUM[g['slug']]
d['guides'] = G
d['note'] = ("Question-shaped guides. Working titles are editorial hypotheses, not claims about search volume or product superiority. "
 "Block types: img, h2, h3, p, note, ul, ol, table, faq, cta. 'summary' is the answer-first box rendered under the byline on every "
 "guide, and the word count in the byline is computed from the guide's own text at build time. Merge notes, 2026-11-20: session "
 "b7320829-affil3 drafted five guides against 7fac552; four duplicated pages that had landed on main, so they were withdrawn and "
 "their first-hand material was merged into the existing cleanup, preset and listing-reading pages instead - see each row's 'amended' "
 "field and FLG-045. One row is new: Sync Finish and Hi-Fry.")
json.dump(d, open('data/guides.json', 'w'), indent=2, ensure_ascii=False); open('data/guides.json', 'a').write('\n')
print('guides:', len(G))
