# Custom Themes & Sensors

Twenty themes for 3.5" USB-C displays, custom sensors, and a background
generator.

## Themes

Set `THEME:` in config.yaml to the folder name under `res/themes/`.
Each theme folder contains a `preview.png` — a verified example render,
embedded below and regenerable with `python3 main.py -t 10` in SIMU mode.

**System monitors**
- `Aurora` — blue on navy, radial CPU gauge, large memory/disk cards ([Aurora](res/themes/Aurora/preview.png))
- `RedFedoraHat` — red variant, original fedora mark ([RedFedoraHat](res/themes/RedFedoraHat/preview.png))
- `Bento` — graphite/slate cards, blue accents ([Bento](res/themes/Bento/preview.png))
- `ThinkPadHUD` — near-black, red accents ([ThinkPadHUD](res/themes/ThinkPadHUD/preview.png))
- `NetPulse` — network focus: wi-fi signal, rates, ping, totals ([NetPulse](res/themes/NetPulse/preview.png))
- `AuroraLandscape`, `RedFedoraHatLandscape` — the above, in 480x320 ([AuroraLandscape](res/themes/AuroraLandscape/preview.png)) ([RedFedoraHatLandscape](res/themes/RedFedoraHatLandscape/preview.png))

**Avionics and vehicles**
- `CockpitCyan`, `CockpitGreen`, `CockpitAmber`, `CockpitIce` — instrument panels, gauge reticles, dials ([CockpitCyan](res/themes/CockpitCyan/preview.png)) ([CockpitGreen](res/themes/CockpitGreen/preview.png)) ([CockpitAmber](res/themes/CockpitAmber/preview.png)) ([CockpitIce](res/themes/CockpitIce/preview.png))
- `CarCluster` — landscape car cluster: twin dials, warning zones, activity blinkers ([CarCluster](res/themes/CarCluster/preview.png))
- `JetHUD` — fighter HUD: radar-scope sweep, heading tape, data blocks ([JetHUD](res/themes/JetHUD/preview.png))
- `JetAmber`, `JetSteel` — JetHUD in amber avionics and black/steel watch tones ([JetAmber](res/themes/JetAmber/preview.png)) ([JetSteel](res/themes/JetSteel/preview.png))
- `JetHUDLandscape` — the fighter HUD in 480x320 ([JetHUDLandscape](res/themes/JetHUDLandscape/preview.png))

**Terminal and watch**
- `TermDash` — plain terminal dump of every stat ([TermDash](res/themes/TermDash/preview.png))
- `ProcDash` — top processes, ps-style rows with summaries ([ProcDash](res/themes/ProcDash/preview.png))
- `ProcDashLandscape` — the same as a wide table: PID/USER/CPU%/MEM%/COMMAND ([ProcDashLandscape](res/themes/ProcDashLandscape/preview.png))
- `Chrono` — watch face: main dial, subdials, date aperture ([Chrono](res/themes/Chrono/preview.png))

## Custom sensors (`library/sensors/sensors_custom.py`)

- `BatteryLevel` — laptop battery charge, text and graph
- `CurrentUser` — logged-in user name
- `OsName` — OS name and version from /etc/os-release
- `WifiSignal` — wi-fi signal in dBm (text) and quality % (graph), via iw
- `FanRpm` — CPU fan speed in RPM from hwmon
- `Timezone` — local timezone abbreviation
- `CpuTempCelsius` — CPU temperature in Celsius, companion to a Fahrenheit main
- `BlinkLeft`, `BlinkRight` — network activity turn-signal indicators
- `TopProc1`-`TopProc10` — top processes by CPU, portrait rows
- `TopProcWide1`-`TopProcWide8` — top processes, wide table rows
- `ProcessCount` — total number of running processes

Themes reference them by class name under `STATS.CUSTOM`.

## Running and testing

- **No hardware**: set `REVISION: SIMU`, run `python3 main.py` — render
  goes to `screencap.png`, live view at http://localhost:5678
- **Screenshot mode**: `python3 main.py -t 10` — deterministic pass over
  all stats, same as CI
- **Verifying**: diff `screencap.png` against the theme's background per
  expected region; every region should contain changed pixels
- **Hardware**: one-time `sudo usermod -aG dialout $USER`, then
  `sg dialout -c "python3 main.py"`
- `DISPLAY_REVERSE: true` renders 180°. Known rev A quirk: reverse-portrait
  renders ~90° off; reverse-landscape works

## Making changes

- Backgrounds are generated: `python3 generate-theme-backgrounds.py`
  (palettes and layouts live there; `track()` boxes must match the theme's
  GRAPH coordinates, baked labels must match TEXT positions)
- New theme: copy an existing `theme.yaml`, recolor, add a palette,
  regenerate, verify
- Schema gotcha: `MEMORY.VIRTUAL.*` and `DISK.USED.PERCENT_TEXT` are flat
  (no `TEXT:` level); most other sections nest under `TEXT`/`GRAPH`/`RADIAL`.
  Wrong nesting fails silently — check this first when something is missing
- Shared-layout edits must be applied to all related themes
