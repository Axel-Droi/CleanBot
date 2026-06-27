# General Waste Handling — CleanBot Guidelines

## Bin Color System

CleanBot uses four bin types to route waste correctly. Blue bin: recyclables (clean plastic, metal, paper, cardboard). Green bin: compostable organics (food scraps, yard waste, compostable packaging). Black bin: landfill (non-recyclable, non-compostable waste). Red bin: hazardous waste (batteries, chemicals, medical waste, aerosols with contents).

## Priority Scoring

High-priority items are those with high environmental impact if left in place: plastic bags and film near storm drains, cigarette butts near waterways, batteries anywhere, and any item that poses immediate hazard to people or wildlife. Medium-priority items are standard recyclable litter with moderate persistence. Low-priority items are organic matter that will biodegrade naturally within weeks.

## Contamination Rules

Contamination occurs when the wrong items enter a recycling stream. A single pizza box can contaminate an entire recycling truckload. A plastic bag can jam an entire sorting facility. When in doubt about recyclability, landfill is safer for the recycling system. CleanBot's primary mission is to remove litter from the environment — placing a borderline item in landfill is preferable to leaving it in the environment.

## Items CleanBot Should Not Collect

Flag for human pickup without attempting mechanical collection: broken glass (physical damage risk to mechanisms), unknown syringes and medical sharps (biohazard), pressurized aerosol cans that are not empty (explosion risk), large scrap metal with sharp edges, any item that appears chemically contaminated (chemical spills, staining on soil). CleanBot action: flag_for_pickup. Use GPS coordinates and timestamp to log these for manual crew dispatch.

## Microplastics Awareness

Plastic bags, Styrofoam, and plastic straws are the highest-priority items for CleanBot because they fragment into microplastics. Microplastics enter stormwater systems, waterways, and food chains within days of outdoor exposure. One plastic bag can produce thousands of microplastic fragments.

## Storm Drain Priority

Any litter within 2 meters of a storm drain is high priority regardless of material type, because storm drains discharge directly to waterways without filtration. CleanBot's navigation system should weigh proximity to storm drains when calculating collection priority scores.

## Recycling Wishcycling Warning

Wishcycling is placing items in recycling in the hope they are recyclable, when they are not. This contaminates good recyclables. CleanBot's knowledge base is conservative — when a material's recyclability is uncertain, it defaults to landfill rather than recycling. This is the correct behavior.

## Environmental Impact Reference

Plastic bottle: 450 years to decompose. Aluminum can: 80–100 years if landfilled (but recoverable via recycling in 60 days). Cigarette butt: 10–14 years, leaches toxins the entire time. Styrofoam cup: 500 years. Paper bag: 1 month in natural environment. Glass bottle: 1 million years. Cardboard box: 2 months (dry), longer if wet.

## Edge Cases and Unknown Items

If CleanBot detects an object it cannot classify with confidence above 50%, it should log the detection with an image crop and GPS coordinate for human review rather than attempting collection. Unknown items should never be collected — they may be hazardous.
