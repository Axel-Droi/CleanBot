# Bio-Waste — Disposal & Handling Guide

## Food Scraps and Organic Matter

Food scraps including fruit peels, vegetable trimmings, bread, dairy, and cooked food are compostable. In a compost environment they break down into nutrient-rich humus within 2–6 months. Food waste in landfills produces methane, a greenhouse gas 80x more potent than CO2 over a 20-year period. CleanBot action: collect_compost. Bin: green. Priority: medium.

## Cigarettes and Cigarette Butts

Cigarette butts are the most collected item in beach and urban cleanups worldwide. Each butt contains a cellulose acetate filter (a form of plastic) that takes 10–14 years to decompose. Cigarette butts leach nicotine, arsenic, lead, and carcinogenic compounds into soil and water. They are not recyclable and not compostable due to toxic chemical content. CleanBot action: collect_landfill. Bin: black. Priority: high — toxic to aquatic life, extremely prevalent.

## Chewing Gum

Chewing gum base is typically made from synthetic rubber (polyisobutylene) and does not biodegrade. It should be placed in the landfill bin. CleanBot action: collect_landfill. Bin: black. Priority: low.

## Animal Waste

Animal feces is bio-waste that poses a public health risk due to pathogens including E. coli, Salmonella, Giardia, and Toxocara roundworm. It should be collected in a sealed bag and placed in the landfill bin. CleanBot should not collect loose animal waste without a containment mechanism — flag_for_pickup if no sealed bag is available. Hazard: high (biohazard). Priority: high in public spaces.

## Food Packaging with Food Residue

Empty food packaging (wrappers, containers) with significant food residue attached is a contamination risk if placed in recycling. The food component can be composted separately. For outdoor litter, CleanBot should collect the item and route by the dominant material — packaging goes to its material bin, accepting minor contamination rather than leaving it on the ground.

## Leaves, Grass Clippings, and Yard Waste

Leaves, grass clippings, and yard trimmings are fully compostable organic material. Most municipalities accept yard waste separately from food waste. CleanBot action: collect_compost if manageable volume. Bin: green. Priority: low — natural organic material, low environmental urgency.

## Biodegradable Packaging (PLA and Compostable Plastics)

Packaging labeled "compostable" or "PLA" (polylactic acid) is made from plant starch and requires industrial composting conditions (58°C+) to break down. It does not break down in home compost piles or in standard bins within a reasonable timeframe. It should not be placed in standard plastic recycling as it contaminates the stream. CleanBot action: collect_compost (industrial facility only). Bin: green with label. Priority: medium.

## Medical and Biohazardous Waste

Used syringes, blood-contaminated material, bandages, and medical waste are biohazardous and require specialized disposal. CleanBot must not collect these items directly. CleanBot action: flag_for_pickup (biohazard). Priority: critical — do not approach with mechanical collection.

## Wax and Greasy Organic Material

Wax-coated items (wax paper, milk cartons with wax coating) and heavily grease-soaked organic waste are not compostable or recyclable. CleanBot action: collect_landfill. Bin: black. Priority: medium.
