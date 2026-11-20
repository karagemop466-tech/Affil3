#!/usr/bin/env python3
"""Session c252594d — add the question-shaped guides for the 2026-11-20 publishing round.

Every factual statement in these guides points at a source already in the register, and each
guide lists the source ids it used. Where two official pages disagree the guide says so and
names the flag; no number is smoothed over and no claim is made that was not read on the page
named in the register.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

DATE = "2026-11-20"


def img(src, alt, caption="Illustration: AI-generated for this site. It shows the idea, not the reviewed unit."):
    return {"type": "img", "src": src, "alt": alt, "caption": caption}


G = []

G.append({
    "slug": "how-much-counter-space-does-an-air-fryer-really-need",
    "title": "How much counter space does an air fryer really need?",
    "category": "air-fryers",
    "cluster_links": ["air-fryer-ovens"],
    "image": "/assets/img/guide-counter-space.png",
    "date": DATE,
    "deck": "Measure the space before you shop, and add the room the drawer takes when it is open.",
    "description": "Counter space is the constraint that decides most kitchen purchases. How to measure it properly, what to add for an open drawer and a swinging door, and the real footprints of the three countertop appliances we track.",
    "sources": ["S11", "S13", "S22"],
    "body": [
        img("/assets/img/guide-counter-space.png", "Illustration of three countertop appliances of different sizes on a kitchen counter with a measuring tape laid across it"),
        {"type": "p", "text": "Counter space is the constraint that quietly decides most kitchen purchases. You can talk about wattage and presets for an hour, and the appliance still has to live on a strip of worktop between the sink and the hob. So start with a tape measure, not a product page."},
        {"type": "h2", "text": "Three dimensions are not enough"},
        {"type": "p", "text": "A manufacturer lists a size, usually depth by width by height. That is the size of the box. What you need is the size of the box plus the space it takes up while you use it, and those are different numbers."},
        {"type": "h2", "text": "Measure these four things before you shop"},
        {"type": "table", "headers": ["What to measure", "Why it matters"], "rows": [
            ["Depth of the run you have", "The manufacturer's stated depth, plus a little slack for the plug and the cable."],
            ["Width of the run you have", "The stated width, plus enough to lift a basket out or swing a door open."],
            ["Height between the counter and the cabinet above", "The stated height, plus the clearance you need to lift the basket up and out."],
            ["The clear floor space in front", "Basket drawers pull out. A fryer with a full-width drawer needs that room every time you cook, not only on the day it arrives."],
        ]},
        {"type": "h2", "text": "What the appliances we track actually take up"},
        {"type": "p", "text": "These are the sizes the manufacturers state on their own product pages, in the order they publish them. They are the footprint of the unit, not of the unit in use."},
        {"type": "table", "headers": ["Appliance", "Stated size, depth by width by height", "Source"], "rows": [
            ["CHEFMAN 6 qt dual basket air fryer", "13.38 by 11.81 by 10.63 in", "Chefman product page (S11)"],
            ["Chefman TurboFry Touch 8 qt stainless", "15.4 by 12.6 by 13.5 in", "Chefman product page (S22)"],
            ["Emeril Lagasse 26 qt french-door oven", "16.9 by 15.8 by 14.8 in", "Emeril Everyday product page (S13)"],
        ]},
        {"type": "h2", "text": "The drawer is the part that catches people"},
        {"type": "p", "text": "A basket fryer is a drawer you pull out to shake the food. The 6 qt dual-basket unit we track is 10.63 in tall, which sounds modest until you try to lift two 3 qt baskets out of it under a wall cabinet. Measure the height of the space above the counter as well as the space in front of the unit. This is the single most common way a kitchen-appliance purchase goes wrong."},
        {"type": "h2", "text": "Doors swing, drawers pull"},
        {"type": "p", "text": "The french-door oven is a different problem: 14.8 in tall and 16.9 in deep, with doors that open outward. It is the largest thing on this list and the one that most needs a clear run of worktop in front of it. If your counter is an L-shape with the hob at the end, an appliance that needs 16 in of depth in front of it may not be the one that fits."},
        {"type": "h2", "text": "A rule of thumb you can actually use"},
        {"type": "p", "text": "If you want a straight answer: take the largest dimension of the unit you are considering and double it in your head. A 15 in appliance wants roughly 15 in of counter to sit on and roughly 15 in of room to work in. That rule is not from a manufacturer; it is a sanity check, and it is wrong in one direction only, always toward buying something smaller than you wanted."},
        {"type": "faq", "items": [
            {"q": "Does an air fryer need clearance above it?", "a": "Yes, more than a toaster does. You lift the basket out to shake it or check the food, and you need room to do that without hitting a cabinet."},
            {"q": "Is the stated size the size of the packaging?", "a": "No. The sizes published on the product pages we cite are the unit's own dimensions. Boxes are larger, but a box only matters on the day it arrives."},
            {"q": "What if I want the largest one and it does not fit?", "a": "Decide which of the two you want more: the capacity or the footprint. We would rather you buy the smaller one and use it than buy the bigger one and shelve it."},
        ]},
        {"type": "cta", "label": "See the appliances we are tracking", "href": "/categories/air-fryers/", "text": "Every row links to the observed Amazon listing, and each product page carries the size the manufacturer states."},
    ],
})

G.append({
    "slug": "dual-basket-or-single-basket-air-fryer",
    "title": "Dual basket or single basket: which one for four people?",
    "category": "air-fryers",
    "cluster_links": [],
    "image": "/assets/img/guide-dual-basket.png",
    "date": DATE,
    "deck": "Two baskets means two foods and two timers. It also means each basket is smaller than one big drawer.",
    "description": "Dual-basket and single-basket air fryers trade against each other in ways the product pages do not spell out: batch size, cooking time, cleanup and counter footprint, for a household of four.",
    "sources": ["S11", "S12", "S22", "S04"],
    "body": [
        img("/assets/img/guide-dual-basket.png", "Illustration of two air fryers side by side, one cutaway showing two separate baskets and one showing a single wide basket"),
        {"type": "p", "text": "The dual-basket format is the most confusing thing on the shelf right now, because the marketing borrows the language of two separate appliances. It is not two appliances. It is one housing, one plug and two baskets, and every advantage and every compromise comes from that arrangement."},
        {"type": "h2", "text": "What a dual basket actually gives you"},
        {"type": "p", "text": "The 6 qt unit we track is described by its manufacturer as a 6-quart (5.67 litre) air fryer with a Sync Finish function, so both baskets stop at the same moment, and a Hi-Fry setting that reaches 450 °F (S11). The marketplace listing describes the baskets themselves as two independent 3 qt nonstick baskets with viewing windows (S04). Two foods, two timers, one appliance."},
        {"type": "h2", "text": "What a single basket gives you"},
        {"type": "p", "text": "One drawer, one timer, one batch. The 8 qt stainless-steel TurboFry on the maker's site states 8 qt / 7.57 L, a 200–400 °F range and four cooking presets, with a top-rack dishwasher-safe basket (S22). The matte-black 8 qt on the same maker's site states 8 qt / 7.57 L with a 450 °F Hi-Fry finish (S12). Both are single-basket machines with roughly twice the volume of one half of the dual unit."},
        {"type": "h2", "text": "The trade-off nobody puts on the box"},
        {"type": "p", "text": "A dual basket splits one big batch into two smaller ones. Two 3 qt baskets cook less food per cycle than one 8 qt drawer, so a large batch takes two cycles instead of one, and each cycle still has its own preheat. The dual format is not faster. It is more flexible about cooking two things at once, which is a different and narrower win."},
        {"type": "table", "headers": ["", "Dual basket", "Single basket"], "rows": [
            ["Two different foods at once", "Yes, and the point of it", "No, one drawer"],
            ["One large batch", "Split across two baskets", "One drawer, one cycle"],
            ["Cooking time per batch", "Shorter per basket, more cycles for a big batch", "Longer for a full drawer, fewer cycles"],
            ["Parts to wash", "Two baskets and two racks", "One basket and one rack"],
            ["Counter footprint", "One unit, two baskets inside", "One unit, one wider basket"],
            ["Total stated capacity", "6 qt / 5.67 L (S11)", "8 qt / 7.57 L (S12, S22)"],
        ]},
        {"type": "h2", "text": "So which one for a household of four?"},
        {"type": "p", "text": "Four people is the number where the answer usually flips. If your weeknight dinner is one dish everybody eats, the single basket wins on capacity and on the number of times you have to wash things. If your household eats two different things, or you are cooking for two meals at once, the dual basket earns its keep immediately."},
        {"type": "h2", "text": "What to check before you commit"},
        {"type": "ul", "items": [
            "Whether the two baskets can run at different temperatures, or only finish at different times. Sync Finish implies the same finishing moment; independent temperature control is a separate question, and the listing is where you will find it.",
            "The size of each basket, not the total. Two 3 qt baskets is the number that decides whether a full tray of wings fits in one go.",
            "Whether the baskets are removable and dishwasher-safe. Chefman states dishwasher-safe baskets for both the 6 qt dual unit and the 8 qt stainless unit (S11, S22).",
            "Whether you will use the second basket often enough to justify the counter space.",
        ]},
        {"type": "faq", "items": [
            {"q": "Is a dual basket the same as two air fryers?", "a": "No. It is one housing and one plug with two baskets. Independent controls help when you want two foods finishing at different times, but check whether the temperatures can actually differ before assuming it."},
            {"q": "Which is better for a family of four?", "a": "For one shared meal, the single basket: more capacity per cycle and fewer parts to wash. For two different foods, the dual basket."},
            {"q": "Does a dual basket cook faster?", "a": "No. Each basket cooks its own food, and a big batch split across two baskets needs two cycles, preheats included."},
        ]},
        {"type": "cta", "label": "Compare the tracked models", "href": "/shop/", "text": "The shop table shows every tracked appliance side by side, with the listing we observed and the sources we read."},
    ],
})

G.append({
    "slug": "air-fryer-toaster-oven-or-microwave-which-one-earns-counter-space",
    "title": "Air fryer, toaster oven or microwave: which earns the space?",
    "category": "air-fryer-ovens",
    "cluster_links": ["air-fryers"],
    "image": "/assets/img/guide-appliance-choice.png",
    "date": DATE,
    "deck": "You rarely need all three. Start from the job you hate doing by hand, then let the shape follow.",
    "description": "Air fryer, toaster oven and microwave each solve a different problem. How to work out which one you actually need, what each shape costs you, and what to give up if you pick it.",
    "sources": ["S13", "S11", "S12"],
    "body": [
        img("/assets/img/guide-appliance-choice.png", "Illustration of three countertop appliances spaced apart on a long kitchen counter"),
        {"type": "p", "text": "Most kitchens do not need three countertop appliances doing similar work. They need one, chosen well. The way to choose is not to start from the appliances; start from the task you currently do badly, slowly, or not at all."},
        {"type": "h2", "text": "Start with the job, not the appliance"},
        {"type": "table", "headers": ["The job", "The tool that fits it"], "rows": [
            ["Crisp frozen or breaded food without a deep fryer", "A basket air fryer. The tracked 6 qt unit reaches 450 °F with a Hi-Fry setting and a Sync Finish function (S11)."],
            ["Cook a whole meal at once, on more than one level", "A countertop oven. The tracked 26 qt french-door unit is a 10-in-1 air fry convection oven with a 26-quart cavity (S13)."],
            ["Reheat a slice of pizza without drying it out", "The microwave, which you already own. This is the job that most often justifies buying nothing new."],
        ]},
        {"type": "h2", "text": "What each shape actually costs you"},
        {"type": "p", "text": "A basket fryer is a small chamber with a drawer. It is quick to preheat and easy to empty, because you pull the drawer out and tip the food onto a plate. Its limit is volume: one drawer, one layer of food at a time, and a tall load cooks unevenly, which is why the baskets on the units we track come with shake reminders or viewing windows."},
        {"type": "p", "text": "A countertop oven is a bigger cavity with a door, racks and usually more functions, because it is standing in for a real oven. It can run two levels at once and take food a drawer would refuse. It costs you heat and smell in the room, more pieces to wash, and real counter depth: the 26 qt unit on the maker's page measures 16.9 in deep by 15.8 in wide by 14.8 in tall (S13)."},
        {"type": "h2", "text": "The honest middle case"},
        {"type": "p", "text": "The real question for most households is whether the second appliance earns its footprint. A basket air fryer and a microwave together handle the majority of weeknight cooking. A countertop oven earns its space when you genuinely cook for a group, want a second level, or want the oven's heat instead of the fryer's."},
        {"type": "h2", "text": "Pick one and give the rest away"},
        {"type": "p", "text": "Counter space is the scarcest resource in most kitchens, and the most common regret is an appliance that gets used twice a year. Work out which single job you want to hand to a machine, buy the machine that does that job well, and let the other jobs go to what you already own."},
        {"type": "faq", "items": [
            {"q": "Is an air fryer just a small convection oven?", "a": "They overlap, but the basket is closer to a shallow drawer and the countertop oven is closer to a real oven cavity. The practical differences are volume, heat recovery and how many levels you can cook on at once."},
            {"q": "Do I need both an air fryer and a toaster oven?", "a": "Often not. If your main use is one or two foods a week for two people, a single mid-size basket machine covers it. Buy the second one when you can name the dish that needs it."},
            {"q": "Which one heats the kitchen less?", "a": "The smaller one, generally. A basket fryer has less air to heat and a shorter preheat. A countertop oven releases more heat and more smell, which matters in a small room."},
        ]},
        {"type": "cta", "label": "See the countertop ovens we track", "href": "/categories/air-fryer-ovens/", "text": "Each row links to the observed listing and carries the size the manufacturer states."},
    ],
})

G.append({
    "slug": "instant-read-or-leave-in-probe-which-thermometer-do-you-need",
    "title": "Instant-read or leave-in probe: which one do you need?",
    "category": "cooking-thermometers",
    "cluster_links": [],
    "image": "/assets/img/guide-thermometer-types.png",
    "date": DATE,
    "deck": "One is a spot check in a second. The other watches a cook from another room. Buying the wrong one is the common mistake.",
    "description": "Instant-read and leave-in wireless thermometers do completely different jobs. How to choose between them, what their published specifications actually promise, and where the numbers come from.",
    "sources": ["S21", "S14", "S10"],
    "body": [
        img("/assets/img/guide-thermometer-types.png", "Illustration of a hand holding an instant-read probe thermometer next to a wireless leave-in probe resting in its charging hub"),
        {"type": "p", "text": "Thermometers get bought for the wrong reason all the time: people buy the wireless one with the app because it looks like the serious choice, and then it sits in a drawer because the app is a hassle. Work out which of the two jobs you actually have before you choose."},
        {"type": "h2", "text": "Job one: the spot check"},
        {"type": "p", "text": "An instant-read probe is a thermometer you use at the end. You pull it out, push the tip into the thickest part of the food, read a number, and wash it. The tracked ThermoMaven is built for exactly this: the manufacturer's page states an instant read in one second on a thermocouple sensor, a stated accuracy of plus or minus 0.5 °F, a bright auto-rotating display, a 100% waterproof design, a built-in magnet, and a lifetime warranty that you activate within 30 days of purchase (S21). No hub, no app, nothing to charge."},
        {"type": "h2", "text": "Job two: the monitor"},
        {"type": "p", "text": "A leave-in probe is a thermometer you leave in the food for the whole cook and read from somewhere else. The tracked CHEF iQ Sense is built for that: the manufacturer's page states a probe 0.19 in thin and 4.75 in long, an internal temperature range of 32–212 °F, an ambient sensor range of 32–1,000 °F, heat resistance to 1,000 °F, and a USB-C-charged Wi-Fi hub that relays readings to an app (S14)."},
        {"type": "h2", "text": "The two numbers worth reading closely"},
        {"type": "p", "text": "Two specifications on that second page deserve a pause. The 1,000 °F figure is the ambient sensor's range and the probe's heat-resistance ceiling, not a range for measuring food: the internal range for the food itself is 32–212 °F. And the maker's page is not internally consistent about sensors. The features list says four internal sensors plus one ambient sensor, while the opening paragraph says five internal sensors. We publish the features list and flag the disagreement rather than picking the tidier answer (FLG-033)."},
        {"type": "h2", "text": "Which one should you buy?"},
        {"type": "table", "headers": ["", "Instant-read", "Leave-in wireless"], "rows": [
            ["Best when", "You cook a few times a week and want a number at the end", "You cook for hours, or across two zones, and want alerts"],
            ["Setup", "None. Pull it out and use it.", "Charge the probe, pair the hub, install the app"],
            ["What it tells you", "The temperature of one spot, right now", "The temperature of one spot, continuously, plus the ambient temperature around it"],
            ["Cost of a mistake", "A slightly underdone roast", "A ruined cook, because nobody was watching"],
            ["Our tracked units", "ThermoMaven F1 Ace: one-second read, plus or minus 0.5 °F claimed (S21)", "CHEF iQ Sense: 32–212 °F internal, 32–1,000 °F ambient (S14)"],
        ]},
        {"type": "h2", "text": "If you only buy one"},
        {"type": "p", "text": "Buy the instant-read. It does the job that matters with none of the friction, and the USDA's guidance on thermometers is about placement discipline, not about connectivity. Add the wireless one later, if you find yourself cooking long enough that a number at the end is no longer enough."},
        {"type": "faq", "items": [
            {"q": "Is a wireless thermometer more accurate?", "a": "Not on the makers' own pages. The wireless unit is built for monitoring, not for precision. Accuracy comes from correct placement, and the published figures deserve care: for the tracked wireless unit, 1,000 °F is an ambient and heat-resistance limit, not a food-reading range."},
            {"q": "Do I need the app?", "a": "Only for the wireless style. The tracked instant-read unit has no hub, no app and nothing to charge."},
            {"q": "What temperature am I aiming for?", "a": "The USDA's safe minimum internal temperature chart is the reference: 165 °F for all poultry, 160 °F for ground meats, and 145 °F plus a three-minute rest for beef, pork, veal and lamb steaks, chops and roasts (S10)."},
        ]},
        {"type": "cta", "label": "See the thermometers we are tracking", "href": "/categories/cooking-thermometers/", "text": "One observed listing each, linked straight to Amazon, with every specification attributed to the page it came from."},
    ],
})

G.append({
    "slug": "how-to-read-an-amazon-listing-before-you-buy-a-kitchen-appliance",
    "title": "How to read an Amazon listing before you buy a kitchen appliance",
    "category": "air-fryers",
    "cluster_links": ["air-fryer-ovens", "cooking-thermometers"],
    "image": "/assets/img/guide-reading-listings.png",
    "date": DATE,
    "deck": "The title is written to sell. The spec block is written to describe. You can tell which is which, and it takes about five minutes.",
    "description": "A practical method for checking a marketplace listing against the manufacturer's own page: model numbers, temperature ranges, wattage, dimensions and certification claims, with a worked example from our own shelf.",
    "sources": ["S16", "S12", "S22", "S04"],
    "body": [
        img("/assets/img/guide-reading-listings.png", "Illustration of a tablet showing a product listing made of placeholder bars, a magnifying glass over it, and two appliance silhouettes being compared"),
        {"type": "p", "text": "Marketplace listings are written by sellers and by software. The maker's own product page is written by the maker. When the two disagree, the maker's page is usually right about the machine and the listing is usually right about the price and availability. Here is the method we use on our own shelf, written out so you can run it on anything."},
        {"type": "h2", "text": "Step one: open the maker's page first, not the listing"},
        {"type": "p", "text": "Search the product name on the maker's own site and open that page. Do not read the listing first. The listing will tell you which machine to look for; the maker's page will tell you what the machine is. Read in the other order and the listing's framing stays in your head, and the maker's page starts to read like a correction."},
        {"type": "h2", "text": "Step two: hunt the model number, not the marketing name"},
        {"type": "p", "text": "Every appliance has a model number somewhere in its details, and it is the only field that identifies a machine reliably. Our 8 qt air fryer is a live example of why. The listing's own copy names model RJ38-SQSS-8T, and Chefman publishes that model, stating a 200–400 °F range, 1700W/120V, dimensions of 15.4 by 12.6 by 13.5 in and a weight of 12.8 lb (S22). Chefman also publishes a different 8 qt machine, RJ38-8T-BLACK, with a 450 °F Hi-Fry finish and no stated dimensions (S12). Same capacity, two machines, one shelf. We publish only what the two pages agree on, and we publish the disagreement as well (FLG-026)."},
        {"type": "h2", "text": "Step three: treat the title as advertising and the spec block as evidence"},
        {"type": "p", "text": "The title of that same listing advertises a 450 °F Hi-Fry option. The maker's page for the model the listing itself names states a 200–400 °F range, and 450 °F belongs to the maker's other 8 qt machine. A headline can be a promise about a product family; a specification block is a claim about one unit. Where they disagree, the specification block wins and the headline gets flagged (FLG-027)."},
        {"type": "h2", "text": "Step four: check the four numbers that change the purchase"},
        {"type": "table", "headers": ["What to check", "What we found on our own shelf"], "rows": [
            ["Wattage", "The listing states 1000 W. The maker's page for the same model number states 1700 W. We publish neither."],
            ["Dimensions", "The listing states 12.75 by 13.5 by 10 in. The maker's page states 15.4 by 12.6 by 13.5 in. Two machines' footprints, published as one."],
            ["Temperature range", "The listing's title says 450 °F. The maker's page for the model the listing names says 200–400 °F."],
            ["Certification claims", "The tracked thermometer's listing states NSF certification and an IP67 rating. The manufacturer's page states a plus or minus 0.5 °F accuracy and a waterproof design, and does not state an IP rating (FLG-032)."],
        ]},
        {"type": "h2", "text": "Step five: read what the maker does not say"},
        {"type": "p", "text": "Silence is data. When the maker's page gives a capacity but no dimensions, you can be certain the dimensions in the listing came from somewhere else. When a maker's page does not state a temperature range, the range on the listing is a claim rather than a specification. Our rule is that a blank cell stays blank: we would rather show a row of 'not stated' than promote a number we cannot stand behind."},
        {"type": "h2", "text": "The five-minute check, in order"},
        {"type": "ol", "items": [
            "Open the maker's page first and find the model number.",
            "Open the listing and find the model number in its details.",
            "Compare wattage, size, temperature range and any certification claim. A disagreement is a question, not a rounding error.",
            "Check whether the maker's page is newer than the listing. Appliances get revised, and listing copy often does not.",
            "If the two pages disagree about something you care about, stop and ask the maker. One email to a manufacturer's contact form is faster than returning an appliance.",
        ]},
        {"type": "faq", "items": [
            {"q": "Can the listing be wrong about the product?", "a": "Yes, and usually it is not wrong so much as describing a different variant of the same family. That is why the model number, not the product name, is the field to check."},
            {"q": "Is a page on the maker's site always more reliable?", "a": "It is more reliable about the machine. It is not more reliable about price or availability, and it does not replace the maker's own warranty terms."},
            {"q": "What if the maker has no page for it?", "a": "Then the listing's specifications are the only source, and they are unverified. We label those rows that way rather than treating a seller's copy as a specification."},
        ]},
        {"type": "cta", "label": "Read our source register", "href": "/sources/", "text": "Every fact on this site points at a dated, linked source. Where two official pages disagree, the disagreement is published rather than smoothed over."},
    ],
})

G.append({
    "slug": "holiday-hosting-on-a-small-counter-a-plan-for-the-big-meal",
    "title": "Holiday hosting on a small counter: a plan for the big meal",
    "category": "air-fryer-ovens",
    "cluster_links": ["air-fryers", "cooking-thermometers"],
    "image": "/assets/img/guide-holiday-hosting.png",
    "date": DATE,
    "deck": "November is thermometer season. Plan the cooking first, then choose the appliance, and the counter space problem solves itself.",
    "description": "A seasonal plan for cooking a big meal on limited counter space: what to cook where, the counter space each appliance needs, and the temperatures to aim for.",
    "sources": ["S13", "S10", "S20", "S11", "S21"],
    "body": [
        img("/assets/img/guide-holiday-hosting.png", "Illustration of a small kitchen counter set for a holiday meal with a countertop oven, an air fryer of roasted vegetables and a thermometer"),
        {"type": "p", "text": "November is thermometer season. Everyone wants the same roast, the same tray of sides, and the same counter, and the oven in your house is already full. The fix is not a bigger oven. It is a plan that assigns each dish a tool before the day starts."},
        {"type": "h2", "text": "The rule for a crowded counter"},
        {"type": "p", "text": "Two appliances maximum on the counter, and they must not need each other. One appliance handles the main heat, one handles the sides, and everything else is cooked ahead. That plan fits a counter most kitchens already have."},
        {"type": "h2", "text": "Give the main heat the space it needs"},
        {"type": "p", "text": "If the main event is a roast or a whole bird, the appliance that does it needs the largest uninterrupted stretch of counter. The tracked 26 qt french-door oven measures 16.9 in deep by 15.8 in wide by 14.8 in tall, and its doors open outward (S13). Leave clear worktop in front of it, not just beside it."},
        {"type": "p", "text": "If the main event is fried and crisped, the countertop oven is the wrong tool. The tracked 6 qt dual-basket unit reaches 450 °F with a Hi-Fry setting and finishes both baskets at the same moment (S11), and it is a 13.38 by 11.81 by 10.63 in box (S11). It also does two foods at once, which is what a hosting kitchen needs most."},
        {"type": "h2", "text": "The sides are the easy part"},
        {"type": "p", "text": "Roasted vegetables, potatoes and small trays are the natural output of an oven-style cavity with racks and more than one level. A basket fryer handles sides too, but only in shallow batches, and it will tie up the one appliance you need for the main."},
        {"type": "h2", "text": "The thermometer is what makes the plan work"},
        {"type": "p", "text": "A crowded kitchen is where a cooking plan goes wrong, because the cook is tempted to guess. The USDA's guidance is that all poultry, whole or ground, reaches a safe minimum internal temperature of 165 °F, ground meats reach 160 °F, and beef, pork, veal and lamb steaks, chops and roasts reach 145 °F followed by a three-minute rest (S10). For placement, USDA guidance on thermometers is specific: for whole poultry, check the thigh, the wing and the thickest part of the breast, avoiding bone (S20). A number removes the guesswork from a kitchen with two people in it."},
        {"type": "h2", "text": "A plan that works on a small counter"},
        {"type": "ol", "items": [
            "The day before: roast and chill the meat, and cut the vegetables. Nothing that needs a hot oven on the day.",
            "The morning: pull the meat out so it is not refrigerator-cold, and set the oven or fryer where it will stay for the whole cook.",
            "Cook the sides first, on the level you are not using for the main. They hold their heat better than they look like they will.",
            "Cook the main last, and put the thermometer in it early. The number, not the clock, decides when it comes out.",
            "Rest the main while everything else is on the table. The USDA's three-minute rest is not a formality; carryover heat keeps climbing.",
        ]},
        {"type": "h2", "text": "What to skip"},
        {"type": "ul", "items": [
            "The second appliance. If you already own a microwave, it is the sides' best friend for reheating and for anything that needs to be fast.",
            "The dessert gadget. A countertop oven at a low temperature does the job of a dehydrator, and the dried fruit is not the part people talk about on the way home.",
            "Any plan that needs a deep fryer. The fryer is the one appliance that needs its own counter, its own ventilation and its own storage.",
        ]},
        {"type": "faq", "items": [
            {"q": "Is it worth buying an appliance for one meal a year?", "a": "No. Buy for the other fifty-two meals. If the holiday is the only reason, borrow one, or use the microwave and the oven you already own."},
            {"q": "What temperature do I pull a turkey at?", "a": "165 °F for all poultry, checked in the thigh, the wing and the thickest part of the breast away from bone, per USDA guidance (S10, S20)."},
            {"q": "Do I need a leave-in probe for a long cook?", "a": "Not for a roast that fits through the door. An instant-read probe used at the right moment does the same job. The tracked instant-read unit states a one-second read and a plus or minus 0.5 °F claimed accuracy (S21)."},
        ]},
        {"type": "cta", "label": "See the thermometers we are tracking", "href": "/categories/cooking-thermometers/", "text": "Both styles, with the manufacturer's own wording and the ranges we could confirm."},
    ],
})

G.append({
    "slug": "air-fryer-presets-how-many-do-you-need",
    "title": "Air fryer presets: how many do you actually need?",
    "category": "air-fryers",
    "cluster_links": ["air-fryer-ovens"],
    "image": "/assets/img/guide-presets.png",
    "date": DATE,
    "deck": "Four presets and twenty-five presets are both fine. The question is how many of them are foods you already cook.",
    "description": "Preset counts are a marketing number. What matters is how many presets match the food you already cook, and how the tracked appliances differ on this.",
    "sources": ["S13", "S22", "S11"],
    "body": [
        img("/assets/img/guide-presets.png", "Illustration of two countertop appliances side by side, one with a short row of preset buttons and one with a long crowded row"),
        {"type": "p", "text": "A preset button is a saved set of time and temperature. It is convenient when it saves you a decision and mildly annoying when it does not. The number of presets tells you almost nothing about the machine; the list of presets tells you almost everything."},
        {"type": "h2", "text": "What the tracked appliances actually offer"},
        {"type": "table", "headers": ["Appliance", "Presets as the maker states them", "Source"], "rows": [
            ["Emeril Lagasse 26 qt french-door oven", "25 cooking pre-sets", "Emeril Everyday product page (S13)"],
            ["Chefman TurboFry Touch 8 qt stainless", "4 cooking presets", "Chefman product page (S22)"],
            ["CHEFMAN 6 qt dual basket", "Sync Finish plus a 450 °F Hi-Fry setting", "Chefman product page (S11)"],
        ]},
        {"type": "h2", "text": "The count is a marketing number"},
        {"type": "p", "text": "Twenty-five sounds like versatility. Four sounds like a compromise. Both readings are wrong, because a preset is only useful if it matches a food you cook on a Tuesday. Count the foods you would actually press the button for. For most households that number is somewhere between three and six: chicken wings, fries, frozen vegetables, a piece of fish, and leftovers."},
        {"type": "h2", "text": "The big oven is not competing on the same axis"},
        {"type": "p", "text": "This is the part the spec sheet hides. The 26 qt unit is described by its maker as a 10-in-1 air fry convection oven with 25 cooking pre-sets and a dual-speed fan (S13). It is standing in for a full oven: a single cavity with a door, racks and more than one level. The 8 qt stainless unit is a single drawer with four presets, a 200–400 °F range and a top-rack dishwasher-safe basket (S22). They are not competing on buttons. They are competing on what you can cook at once."},
        {"type": "h2", "text": "Dual baskets replace presets with independence"},
        {"type": "p", "text": "The 6 qt dual-basket unit takes a different route again. Instead of a long preset list, it gives you a Sync Finish function that ends both baskets at the same moment and a Hi-Fry setting that reaches 450 °F (S11). Two foods, two timers, one cycle. For a household cooking two different dinners, that is worth more than twenty-five buttons."},
        {"type": "h2", "text": "What to actually do with this"},
        {"type": "ul", "items": [
            "Count the foods you cook weekly, not the foods you could cook.",
            "Check whether the presets match those foods, or whether they are named after dishes that sound impressive.",
            "Decide whether you want help with time and temperature, or with running two things at once. Those are different features.",
            "Treat a preset as a starting point, not an instruction. Every appliance runs differently, and a preset on a 450 °F Hi-Fry machine is not the same cook as a preset on a 200–400 °F machine.",
        ]},
        {"type": "faq", "items": [
            {"q": "Are more presets better?", "a": "No. More presets is more buttons. The useful count is how many presets match food you already cook weekly."},
            {"q": "Do I need the highest temperature?", "a": "Only if you brown things. The tracked units we list span a 200–400 °F range up to a 450 °F Hi-Fry setting, and Hi-Fry on the dual-basket unit is a short, hot finish rather than the whole cook."},
            {"q": "Can I just use the manual settings?", "a": "Yes, and many people do. Presets are a convenience for repeat dishes; time and temperature on the dial give you more control, and they are what you will reach for with anything new."},
        ]},
        {"type": "cta", "label": "Compare the tracked models", "href": "/shop/", "text": "The shop table shows each appliance with the listing we observed and the sources we read for its specifications."},
    ],
})

G.append({
    "slug": "air-fryer-chicken-breast-how-do-you-know-it-is-done",
    "title": "Air fryer chicken breast: how do you know it is done?",
    "category": "cooking-thermometers",
    "cluster_links": ["air-fryers"],
    "image": "/assets/img/guide-temperature-basics.png",
    "date": DATE,
    "deck": "Colour tells you it looks right. Temperature tells you it is safe. Here is the number, and where to put the probe.",
    "description": "Cooking chicken breast in an air fryer: the safe internal temperature, where to place the probe, why colour and texture mislead, and which tracked appliance suits which job.",
    "sources": ["S10", "S20", "S21", "S14"],
    "body": [
        img("/assets/img/guide-temperature-basics.png", "Illustration of a roast on a wooden board with a digital probe thermometer inserted into the thickest part beside a simple dial gauge"),
        {"type": "p", "text": "Chicken breast is the dish where colour and temperature disagree most often. The outside goes golden long before the middle is safe, and a probe pushed into the wrong place reads high on a piece that is still raw in the thickest part. This is a short guide to the number that matters and where the probe goes."},
        {"type": "h2", "text": "The number"},
        {"type": "p", "text": "The USDA's safe minimum internal temperature for all poultry, whole or ground, is 165 °F (S10). That is the number to aim for, and it is the only one worth arguing about."},
        {"type": "h2", "text": "Where the probe goes"},
        {"type": "p", "text": "USDA guidance on thermometers is specific: for whole poultry, check the thigh, the wing and the thickest part of the breast, avoiding bone (S20). The general rule for any cut is the thickest part, away from bone, fat pockets and the pan. Bone conducts heat differently from meat, so a probe touching bone reads a temperature the meat itself does not have."},
        {"type": "h2", "text": "Why it feels wrong at 165 °F"},
        {"type": "p", "text": "Because a chicken breast cooked straight to 165 °F in a hot basket is dry, and the instinct is to pull it earlier. That instinct is reasonable; the temperature is not negotiable. The way out is to lower the cooking temperature, give the thick part time, and let carryover heat and a rest finish the job. Cook it gently, check it early, and take it out when the thickest part is close."},
        {"type": "h2", "text": "Which thermometer to use"},
        {"type": "p", "text": "For a breast this thin, an instant-read probe is the right tool, because you want the number at the moment you decide. The tracked ThermoMaven states an instant read in one second on a thermocouple sensor and a claimed accuracy of plus or minus 0.5 °F (S21). If you are cooking a whole bird rather than a breast, the tracked wireless probe does something an instant-read cannot: it stays in the food and reports continuously, with an internal range of 32–212 °F and an ambient sensor range of 32–1,000 °F (S14)."},
        {"type": "h2", "text": "The basket matters more than the mode"},
        {"type": "table", "headers": ["What changes the result", "Why"], "rows": [
            ["How full the basket is", "A full basket drops the temperature and cooks unevenly. Leave room, and cook in batches if you have to."],
            ["Which machine you use", "The tracked 6 qt dual-basket unit reaches 450 °F on Hi-Fry and stops both baskets together (S11); the 8 qt stainless unit runs a 200–400 °F range (S22). A high-heat finish browns; a moderate cook does the work."],
            ["Whether you open the drawer", "Every opening costs heat and adds time."],
            ["Whether you rest it", "Carryover heat keeps climbing after the pan. The USDA's three-minute rest for beef, pork, veal and lamb (S10) is the same physics applied to poultry."],
        ]},
        {"type": "faq", "items": [
            {"q": "Is the juice test reliable?", "a": "It is a useful smell and texture cue, but it cannot tell you the temperature in the thickest part. Use the probe to decide, and the juice to confirm."},
            {"q": "How long does it take?", "a": "We do not publish times, because they depend on the machine, the size of the breast and how full the basket is. Set the temperature, then let the thermometer decide when it is done."},
            {"q": "Can I cook frozen chicken breast?", "a": "Often, and the machine you choose matters. Follow the appliance's own guidance, and cook it in a single layer rather than stacked, so the temperature in the thickest part keeps up."},
        ]},
        {"type": "cta", "label": "See the thermometers we are tracking", "href": "/categories/cooking-thermometers/", "text": "Both styles, with every specification attributed to the page it was read from."},
    ],
})

# --------------------------------------------------------------------------- write
path = DATA / "guides.json"
doc = json.loads(path.read_text(encoding="utf-8"))
existing = {g["slug"] for g in doc["guides"]}
added = []
for g in G:
    if g["slug"] in existing:
        print(f"skip (already present): {g['slug']}")
        continue
    doc["guides"].append(g)
    added.append(g["slug"])

# The thermometer guide carried a note that is now out of date: FLG-025 said no manufacturer
# page could be located for the tracked instant-read unit. One was found on 2026-11-20.
for g in doc["guides"]:
    if g["slug"] == "is-your-meat-thermometer-telling-you-the-right-number":
        for b in g["body"]:
            if b.get("type") == "note" and "FLG-025" in b.get("text", ""):
                b["text"] = (
                    "Two things our register caught while checking the tracked units against their "
                    "makers' pages: the manufacturer's own pages disagree about the tracked wireless "
                    "thermometer's battery life (flag FLG-023), and the tracked instant-read unit's "
                    "maker page and its marketplace listing carry different model names, with the "
                    "listing adding certification and water-resistance claims the maker does not "
                    "state (flags FLG-031 and FLG-032). Conflicts like these are exactly why we link "
                    "our sources instead of summarising them."
                )

path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"added {len(added)} guides; total {len(doc['guides'])}")
for s in added:
    print("  +", s)
