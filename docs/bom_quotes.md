# BOM + local quotes — planning list, NOT a quotation (Phase 1)

**Rule:** every price below is a planning estimate until 3 signed local quotes + photo receipts are filed here. Never present BOM as market truth — in the report, video, or judging Q&A.

| # | Item | Phase 1 spec | Est. DT | Quote 1 (seller/date/photo) | Quote 2 | Quote 3 |
|---|---|---|---|---|---|---|
| 1 | Mini conveyor / frame / belt / DC motor | 60–100 cm, 12 V, 10–30 RPM PWM | 250–400 | _pending 24–27 Oct_ | _pending_ | _pending_ |
| 2 | ESP32 / Arduino + motor driver | ESP32 + L298N/MX1508 | 35–80 | _pending_ | | |
| 3 | USB camera + fixed mount | UVC 720p+, locked exposure | 70–150 | _pending_ | | |
| 4 | LED + inspection tunnel | 5500 K strip, diffused, matte-black 30 cm | 30–70 | _pending_ | | |
| 5 | Servo flap + linkage + chutes | MG996R 25 kg·cm, 2 food-contact chutes | 25–60 | _pending_ | | |
| 6 | Optical sensor + wiring | IR break-beam + cables | 15–40 | _pending_ | | |
| 7 | Dust hood + fan + duct + filter | 120 mm 12 V + replaceable G4/F7 | 80–180 | _pending_ | | |
| 8 | Boxes + guards | 2 wipeable boxes, belt sides, servo pinch cover | 30–70 | _pending_ | | |
| 9 | Scale | digital, 1 g resolution | 30–80 | _pending_ | | |
| 10 | Power + switches + LEDs + e-stop | mushroom NC + relay cutting motor PSU | 50–100 | _pending_ | | |
| 11 | Cables + mounts + misc | contrasting belt cover, fasteners | 60–120 | _pending_ | | |
| | **Total** | excl. laptop + fabrication | **675–1,350** (~1,500 w/ laptop) | | | |

Safety: e-stop mushroom NC in series with motor PSU coil + sense line to MCU; software stop is NOT safety; restart = deliberate local button + UI resume. Dust filter reduces *some* visible dust, NOT respiratory protection — test fan empty first (herbs must not lift), 10-pour before/after + white-wipe photos, sealed electronics, cleaning SOP.
