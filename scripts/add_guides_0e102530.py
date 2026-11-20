#!/usr/bin/env python3
"""Append the two guides authored by session 0e102530 to data/guides.json.

Content is restricted to figures published by the manufacturer pages named in each
guide's `sources`, plus the observed listing records already in data/products.json.
Nothing is inferred, and no price, rating or review count appears.
"""
import json
from collections import OrderedDict

PATH = 'data/guides.json'

with open(PATH, encoding='utf-8') as f:
    db = json.load(f, object_pairs_hook=OrderedDict)

existing = {g['slug'] for g in db['guides']}

GUIDE_DUAL = OrderedDict([
    ("slug", "dual-basket-or-single-basket-air-fryer-which-do-you-need"),
    ("title", "Dual basket or single basket: which air fryer do you need?"),
    ("category", "air-fryers"),
    ("cluster_links", ["air-fryer-ovens"]),
    ("image", "/assets/img/guide-dual-vs-single-basket.jpg"),
    ("image_alt", "Illustration of two countertop air fryers side by side: one with two separate pull-out baskets holding fries and chicken wings, and one taller unit with a single deep drawer and a wire rack"),
    ("date", "2026-11-20"),
    ("deck", "Two drawers that finish together is a different promise from one deep basket. Here is what each shape actually commits you to."),
    ("description", "A side-by-side look at a two-basket air fryer and a single-basket air fryer: capacity each way, temperature ceiling, wattage, counter footprint and cleanup, with every figure taken from the manufacturer's own specification page."),
    ("sources", ["S11", "S23", "S04"]),
    ("body", [
        OrderedDict([
            ("type", "img"),
            ("src", "/assets/img/guide-dual-vs-single-basket.jpg"),
            ("alt", "Illustration of two countertop air fryers side by side: one with two separate pull-out baskets holding fries and chicken wings, and one taller unit with a single deep drawer and a wire rack"),
            ("caption", "Illustration: AI-generated for this site. It shows the two shapes we describe, not any specific product we track.")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "Almost every air fryer comparison starts with capacity, and capacity is exactly where the two shapes stop being comparable. A six-quart machine split into two three-quart baskets does not hold six quarts of anything at once. It holds three quarts in one drawer and three in the other, and the two finish on their own clocks. A single eight-quart basket holds eight quarts in one chamber. If your dinner is one big batch, those are different appliances. If your dinner is two dishes with different cooking times, they are different again.")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "We track two Chefman TurboFry Touch air fryers that make this comparison concrete, and we read both the manufacturer's specification pages and the Amazon listings the short links land on. Where those two disagree, we say so instead of picking a side.")
        ]),
        OrderedDict([
            ("type", "h2"),
            ("text", "What each maker publishes")
        ]),
        OrderedDict([
            ("type", "table"),
            ("headers", ["Figure", "Two-basket unit (6 qt)", "Single-basket unit (8 qt)"]),
            ("rows", [
                ["Model", "RJ38-SQPF-3TDB-2W", "RJ38-SQSS-8T"],
                ["Capacity", "6 qt / 5.67 L, in two independent 3 qt baskets", "8 qt / 7.57 L, one basket"],
                ["Temperature range", "200-450 °F, with a Hi-Fry setting at 450 °F", "200-400 °F"],
                ["Power", "1700 W / 120 V", "1700 W / 120 V"],
                ["Case size (in)", "13.38 x 11.81 x 10.63", "15.4 x 12.6 x 13.5"],
                ["Weight", "13.3 lb", "12.8 lb"],
                ["Cooking functions", "Air fry, bake, reheat, dehydrate, frozen", "Air fry, bake, dehydrate, frozen"],
                ["Presets", "Not stated on the manufacturer page", "4 cooking presets"],
                ["Viewing window", "Dual viewing windows and an interior light", "Not stated on the manufacturer page"],
                ["Dishwasher", "Nonstick, dishwasher-safe baskets", "Top-rack dishwasher-safe basket and rack"],
                ["Certification", "cETL approved", "cETL approved"],
                ["Warranty", "1-year Chefman assurance", "1-year Chefman assurance"]
            ])
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "Both figures come from Chefman's own product pages for these model numbers. Two cells are blank on purpose: the manufacturer does not publish a preset count for the two-basket unit, and neither page mentions a viewing window for the single-basket unit. We do not fill those in from the listing titles.")
        ]),
        OrderedDict([
            ("type", "note"),
            ("text", "The 8 qt listing on Amazon carries a title that advertises a 450 °F Hi-Fry burst, and its own bullet list states 200-400 °F. The manufacturer publishes 200-400 °F for model RJ38-SQSS-8T. We publish the manufacturer's figure and flag the title claim rather than repeating it as a specification.")
        ]),
        OrderedDict([
            ("type", "h2"),
            ("text", "Read the temperature ceiling as a promise about your food, not a race")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "The 450 °F on the two-basket unit is a real published figure with a named setting attached: Hi-Fry. The 400 °F ceiling on the single-basket unit is simply the top of its range. That difference matters less than it looks. Air frying at 400 °F crisps thin, breaded food perfectly well; 450 °F is where you go when you want the very darkest edges on something dense. If your weeknight food is chicken wings and fries, the gap between the two ceilings is unlikely to be the reason you pick one over the other.")
        ]),
        OrderedDict([
            ("type", "h2"),
            ("text", "Wattage, and the circuit it lives on")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "Both units publish 1700 W at 120 V. That is worth knowing for a reason that has nothing to do with cooking speed: 1700 W at 120 V draws roughly 14 amps, which is close to what a 15-amp kitchen circuit is rated for, and the same circuit usually carries the toaster. Plug either unit in alone and you are fine. Plug one in while the toaster is running and you may be looking for the reset button.")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "The 8 qt listing states 1000 W for the same model number the manufacturer names, RJ38-SQSS-8T. We publish 1700 W because that is what Chefman states on the product page, and we flag the difference rather than averaging it or quietly dropping it.")
        ]),
        OrderedDict([
            ("type", "h2"),
            ("text", "Counter space, with the drawer open")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "The two-basket unit is the shorter and deeper of the two at 13.38 x 11.81 x 10.63 in, and it is 13.3 lb. The single-basket unit is taller and wider at 15.4 x 12.6 x 13.5 in, and 12.8 lb. Neither is small. But the number that decides whether it fits is not the footprint in the manual. It is the footprint with the drawer pulled out, because you pull it out every time and you need somewhere to put the hot basket while you do.")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "Two drawers open side by side means you need clear space across a wider stretch of counter at once. One deep drawer means you need clear space in front of a single unit. Neither figure is published, so measure your own counter rather than trusting the case size.")
        ]),
        OrderedDict([
            ("type", "h2"),
            ("text", "Cleanup, in one line")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "Both baskets are nonstick and both are dishwasher-safe, so neither wins on the washing-up question. The single-basket unit's page adds that the rack is top-rack dishwasher safe. The two-basket unit has two baskets to wash instead of one, which is the part the dishwasher rating does not tell you.")
        ]),
        OrderedDict([
            ("type", "h2"),
            ("text", "So which one do you need?")
        ]),
        OrderedDict([
            ("type", "ol"),
            ("items", [
                "If you cook one big batch of one thing, you want the single deep basket. Splitting a batch across two baskets means the food in the emptier basket finishes sooner and dries out.",
                "If you cook two things that need different times, you want the two-basket unit. Separate drawers mean separate timers, and the Sync Finish function is designed to hold both to the same end time.",
                "If you are undecided, look at your counter and your outlet before the features. A unit you cannot plug in safely is the wrong unit.",
                "If you want to see the numbers side by side with the rest of the range, the shop table and the comparison page have every published figure for both of these and the other three we track."
            ])
        ]),
        OrderedDict([
            ("type", "cta"),
            ("label", "See the air fryers we are tracking"),
            ("href", "/categories/air-fryers/"),
            ("text", "Both units, with the exact Amazon listing we observed and the manufacturer pages we read.")
        ]),
        OrderedDict([
            ("type", "faq"),
            ("items", [
                OrderedDict([
                    ("q", "Is a two-basket air fryer quieter than a single-basket one?"),
                    ("a", "Neither manufacturer publishes a sound level for either model, so we have no figure to compare and we will not estimate one. If noise is the deciding factor for you, that is a question for the retailer or a review you trust, not for a specification sheet.")
                ]),
                OrderedDict([
                    ("q", "Does the Sync Finish function mean both baskets cook at the same temperature?"),
                    ("a", "The manufacturer describes Sync Finish as a function so both baskets finish cooking at the same time, with a Sync function so both baskets finish cooking simultaneously. It is described as a timing feature. The page does not describe it as forcing two different temperature settings to converge, so we do not describe it that way either.")
                ]),
                OrderedDict([
                    ("q", "Can I use parchment in either basket?"),
                    ("a", "Neither manufacturer page states a parchment rule, so there is no published answer on this site. Check the manual or the manufacturer's own support page for your model before using it.")
                ]),
                OrderedDict([
                    ("q", "Why is there no preset count for the two-basket unit?"),
                    ("a", "Because the manufacturer's specification page for model RJ38-SQPF-3TDB-2W does not publish one. The Amazon listing for that unit does not state a preset count either. A blank cell on our table means we could not confirm the figure from an official page, not that the feature is missing.")
                ])
            ])
        ])
    ])
])

GUIDE_SPECS = OrderedDict([
    ("slug", "how-to-read-air-fryer-specifications-without-being-misled"),
    ("title", "How to read air fryer specifications without being misled"),
    ("category", "air-fryers"),
    ("cluster_links", ["air-fryer-ovens", "cooking-thermometers"]),
    ("image", "/assets/img/guide-watts-and-degrees.jpg"),
    ("image_alt", "Illustration of a dial gauge, a coiled power cord with a two-prong plug, a printed temperature scale card, graph paper with a rising curve, and an empty paper food basket arranged on a wooden counter"),
    ("date", "2026-11-20"),
    ("deck", "Quarts, watts, degrees, presets: four numbers that get twisted into marketing, and what the maker actually published."),
    ("description", "A plain guide to the four numbers on an air fryer specification sheet: what capacity means when it is split across two baskets, what watts mean for your circuit, what a temperature ceiling promises, and why a preset count on a listing title is not the same as a published specification."),
    ("sources", ["S11", "S23", "S13", "S16", "S04"]),
    ("body", [
        OrderedDict([
            ("type", "img"),
            ("src", "/assets/img/guide-watts-and-degrees.jpg"),
            ("alt", "Illustration of a dial gauge, a coiled power cord with a two-prong plug, a printed temperature scale card, graph paper with a rising curve, and an empty paper food basket arranged on a wooden counter"),
            ("caption", "Illustration: AI-generated for this site. It shows the four numbers this guide is about, not any specific product we track.")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "An air fryer specification sheet is four numbers wearing a trench coat. Quarts, watts, degrees, presets. Each one is real, each one is published by the manufacturer, and each one turns into something else the moment it appears in a listing title. This guide is a short decoder: what each number is, what it is not, and where to go when the listing and the manufacturer disagree.")
        ]),
        OrderedDict([
            ("type", "h2"),
            ("text", "Quarts: capacity is a shape, not a number")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "A quart is a volume, and a chamber's volume does not tell you how much food you can cook in one go. It tells you the size of the space. The number that matters is how that space divides.")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "Our two-basket air fryer publishes 6 qt, and the same page breaks it down as two independent 3 qt baskets. Six quarts in one drawer would be one big dinner. Six quarts split across two drawers is two three-quart dinners, each with its own timer. The number on the box is the sum; the number on your counter is the part you use.")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "The same caution applies to our countertop oven, which publishes 26 qt / 24.6 L and states it is for 4-6 people, with two levels and a french door. More volume there means more levels, not one bigger batch. Compare the shape of the space, not just its size.")
        ]),
        OrderedDict([
            ("type", "note"),
            ("text", "Capacity is not even a shared unit across this category. Our range spans two air fryers, one countertop oven, a handheld instant-read probe and a wireless leave-in probe. A quart figure on the first three has no meaning at all for the last two, which is why our comparison table leaves those cells blank instead of printing a dash.")
        ]),
        OrderedDict([
            ("type", "h2"),
            ("text", "Watts: a current question before it is a speed question")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "Most people read wattage as how fast the thing cooks. The more useful reading is how much current it pulls, because that determines whether you can run it at the same time as anything else.")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "1700 W at 120 V is about 14 amps. A standard kitchen circuit in the United States is 15 amps. So an appliance at 1700 W can use nearly all of it, and the toaster, the coffee maker and the kettle are all reaching for the same budget. It is not a fault in the appliance. It is a thing to know before you plug it in.")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "Our 8 qt air fryer makes the point in one line. The manufacturer's page states 1700 W. The Amazon listing for the same model number states 1000 W. We publish 1700 W, because that is the figure from the maker's own page, and we flag the listing rather than quietly choosing one. When a maker and a listing disagree, the maker's page is the primary source and the listing is evidence that the number circulates in two forms.")
        ]),
        OrderedDict([
            ("type", "h2"),
            ("text", "Degrees: a ceiling, a burst, and a range")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "A published temperature range is the appliance's operating envelope. Our two-basket air fryer publishes 200-450 °F, with the 450 °F attached to a named Hi-Fry setting. Our single-basket air fryer publishes 200-400 °F, with no separate burst described.")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "Then there is the number in the listing title. The 8 qt listing advertises a 450 °F Hi-Fry Option, while the manufacturer's page for that model states a maximum of 400 °F, and the listing's own bullet list also states 200-400 °F. A title is marketing copy that a manufacturer approved once; a specification page is the current published statement. When they conflict, we publish the specification page and flag the title.")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "Our countertop oven publishes no temperature range at all on the manufacturer's page, so its cell on our table is blank. That is a different kind of blank from a wrong number, and it is a legitimate thing to ask a retailer about before you buy.")
        ]),
        OrderedDict([
            ("type", "h2"),
            ("text", "Presets: a convenience, rarely a difference")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "Our single-basket air fryer publishes four cooking presets. Our two-basket unit publishes none on its specification page, and its listing does not state a count either. A preset is a saved setting for one food at one temperature. Whether four presets or none is the difference between a shortcut and nothing is a matter of whether you cook the same four things every week.")
        ]),
        OrderedDict([
            ("type", "p"),
            ("text", "The oven is the interesting case. The manufacturer page shows 25 cooking pre-sets in its own specification block, while the Amazon listing title says 24 one-touch preset options, and the same page's description calls it a 10-in-1 appliance. The manufacturer's own pages disagree with each other on that count, so we publish no preset count for it at all rather than pick the number that reads best.")
        ]),
        OrderedDict([
            ("type", "h2"),
            ("text", "A five-step check you can run in two minutes")
        ]),
        OrderedDict([
            ("type", "ol"),
            ("items", [
                "Find the model number on the appliance or its listing, then open the manufacturer's page for that exact model. Model families share pages, and a nearby model's numbers are not this model's numbers.",
                "Read the specification block, not the feature bullets. The block is the list the maker stands behind; the bullets are written to be read on a phone while shopping.",
                "Write down each number next to the word that makes it honest: 6 qt, but two 3 qt baskets. 1700 W, but about 14 amps on a 15-amp circuit. 200-400 °F, but the title says 450.",
                "Leave a blank cell blank. If the maker does not publish it, the honest value is 'not stated', and that is more useful to you than a number copied from a title.",
                "Check the warranty and the certification while you are there. They are short lines and they are the two figures most often omitted from a listing title."
            ])
        ]),
        OrderedDict([
            ("type", "cta"),
            ("label", "See every specification we could confirm"),
            ("href", "/compare/"),
            ("text", "One table, five products, every cell traced to a source, and every gap marked as a gap.")
        ]),
        OrderedDict([
            ("type", "faq"),
            ("items", [
                OrderedDict([
                    ("q", "Does a higher wattage mean it cooks faster?"),
                    ("a", "It means it draws more power, and in these appliances more power generally means a hotter chamber faster. But the ceiling on how fast a piece of food cooks is usually its own thickness and moisture, not the appliance's wattage. We publish watts because they are published, not because we have measured a cooking difference. We are not a test kitchen and we do not claim to be.")
                ]),
                OrderedDict([
                    ("q", "Is a bigger chamber always better?"),
                    ("a", "No, and the shape usually matters more than the volume. A chamber you can only fill half way wastes both the heat and the counter space. A chamber split into two smaller drawers is only an advantage when you are genuinely cooking two things at once.")
                ]),
                OrderedDict([
                    ("q", "Why does your table leave so many cells blank?"),
                    ("a", "Because a blank cell on this site means 'not confirmed from an official page', and an unfilled cell is the honest answer when the maker does not publish a figure. Every blank has a line of explanation on the product page telling you exactly which figure is missing and why, and each one is listed on our Flagged for review page with the source that was checked.")
                ]),
                OrderedDict([
                    ("q", "Can I trust a listing title's numbers?"),
                    ("a", "Treat a title as a claim someone made, not a specification. It is a perfectly good place to start a question. It is a bad place to end one. This site publishes figures from the manufacturer's specification pages and flags title claims that conflict with them.")
                ])
            ])
        ])
    ])
])

for g in (GUIDE_DUAL, GUIDE_SPECS):
    if g['slug'] in existing:
        raise SystemExit('slug already present: ' + g['slug'])
    db['guides'].append(g)

with open(PATH, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
    f.write('\n')

print('guides now:', len(db['guides']))
for g in db['guides']:
    print(' -', g['slug'])
