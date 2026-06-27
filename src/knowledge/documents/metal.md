# Metal Waste — Disposal & Handling Guide

## Aluminum Cans

Aluminum beverage cans are among the most valuable and infinitely recyclable materials in the waste stream. Recycling aluminum requires 95% less energy than producing it from raw bauxite ore. Aluminum cans can be recycled an unlimited number of times without quality loss. CleanBot action: collect_recyclable. Bin: blue. Priority: high — high economic and environmental recovery value.

## Steel and Tin Cans

Steel food cans and tin cans are fully recyclable. They are magnetic, which allows automated sorting facilities to separate them from other recyclables easily. Rinse food residue before recycling if possible. CleanBot action: collect_recyclable. Bin: blue. Priority: high.

## Aluminum Foil

Aluminum foil and foil trays are recyclable when clean. Foil contaminated with food grease is not accepted in most recycling streams. Scrunch foil into a ball at least the size of a golf ball to prevent it from jamming sorting machinery. CleanBot action: collect_recyclable if visibly clean. Bin: blue. Priority: medium.

## Metal Bottle Caps

Metal bottle caps from glass bottles are recyclable. Do not put them loose in the recycling bin as they fall through sorting screens. Keep the cap on the bottle or collect them in a larger metal can and crimp the can closed. CleanBot action: collect_recyclable. Bin: blue. Priority: low.

## Pop Tabs / Ring Pulls

Pop tabs from cans are recyclable aluminum. They are small but collectively significant. CleanBot action: collect_recyclable. Bin: blue. Priority: low — collect when found near cans.

## Scrap Metal

General scrap metal found outdoors (wire, metal rods, broken hardware) is recyclable at scrap metal facilities, not in standard curbside bins. It may have sharp edges. CleanBot action: flag_for_pickup (sharp hazard potential). Priority: medium — do not attempt mechanical collection of unknown scrap.

## Aerosol Cans

Empty aerosol cans (deodorant, spray paint, cooking spray) are recyclable as metal once completely empty. Do not puncture. Never put pressurized or partially full aerosol cans in recycling — they are a fire and explosion hazard at sorting facilities. CleanBot action: collect_recyclable if empty (shake test), flag_for_pickup if contents unknown. Bin: blue (empty only). Hazard: high if not empty.

## Batteries

Batteries are hazardous waste. Standard alkaline batteries contain manganese, zinc, and potassium hydroxide. Lithium batteries contain lithium and cobalt which can cause fires if punctured. Button cell batteries contain mercury or silver. No battery type should go in standard recycling or landfill bins. CleanBot action: collect_hazardous. Bin: red. Priority: high — active fire and contamination risk.

## Scrap Metal Hazards

Unknown scrap metal objects may have sharp edges that could damage CleanBot's collection mechanism. If the object cannot be identified or appears to be structural metal (rebar, wiring), flag for human collection rather than attempting autonomous pickup. Contaminant risk: medium. Physical damage risk: medium.
