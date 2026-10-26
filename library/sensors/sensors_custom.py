# SPDX-License-Identifier: GPL-3.0-or-later
#
# turing-smart-screen-python - a Python system monitor and library for USB-C displays like Turing Smart Screen or XuanFang
# https://github.com/mathoudebine/turing-smart-screen-python/
#
# Copyright (C) 2021 Matthieu Houdebine (mathoudebine)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# This file allows to add custom data source as sensors and display them in System Monitor themes
# There is no limitation on how much custom data source classes can be added to this file
# See CustomDataExample theme for the theme implementation part

import getpass
import math
import platform
import psutil
from abc import ABC, abstractmethod
from typing import List


# Custom data classes must be implemented in this file, inherit the CustomDataSource and implement its 2 methods
class CustomDataSource(ABC):
    @abstractmethod
    def as_numeric(self) -> float:
        # Numeric value will be used for graph and radial progress bars
        # If there is no numeric value, keep this function empty
        pass

    @abstractmethod
    def as_string(self) -> str:
        # Text value will be used for text display and radial progress bar inner text
        # Numeric value can be formatted here to be displayed as expected
        # It is also possible to return a text unrelated to the numeric value
        # If this function is empty, the numeric value will be used as string without formatting
        pass

    @abstractmethod
    def last_values(self) -> List[float]:
        # List of last numeric values will be used for plot graph
        # If you do not want to draw a line graph or if your custom data has no numeric values, keep this function empty
        pass


# Example for a custom data class that has numeric and text values
class ExampleCustomNumericData(CustomDataSource):
    # This list is used to store the last 10 values to display a line graph
    last_val = [math.nan] * 10  # By default, it is filed with math.nan values to indicate there is no data stored

    def as_numeric(self) -> float:
        # Numeric value will be used for graph and radial progress bars
        # Here a Python function from another module can be called to get data
        # Example: self.value = my_module.get_rgb_led_brightness() / audio.system_volume() ...
        self.value = 75.845

        # Store the value to the history list that will be used for line graph
        self.last_val.append(self.value)
        # Also remove the oldest value from history list
        self.last_val.pop(0)

        return self.value

    def as_string(self) -> str:
        # Text value will be used for text display and radial progress bar inner text.
        # Numeric value can be formatted here to be displayed as expected
        # It is also possible to return a text unrelated to the numeric value
        # If this function is empty, the numeric value will be used as string without formatting
        # Example here: format numeric value: add unit as a suffix, and keep 1 digit decimal precision
        return f'{self.value:>5.1f}%'
        # Important note! If your numeric value can vary in size, be sure to display it with a default size.
        # E.g. if your value can range from 0 to 9999, you need to display it with at least 4 characters every time.
        # --> return f'{self.as_numeric():>4}%'
        # Otherwise, part of the previous value can stay displayed ("ghosting") after a refresh

    def last_values(self) -> List[float]:
        # List of last numeric values will be used for plot graph
        return self.last_val


# Example for a custom data class that only has text values
class ExampleCustomTextOnlyData(CustomDataSource):
    def as_numeric(self) -> float:
        # If there is no numeric value, keep this function empty
        pass

    def as_string(self) -> str:
        # If a custom data class only has text values, it won't be possible to display graph or radial bars
        return "Python: " + platform.python_version()

    def last_values(self) -> List[float]:
        # If a custom data class only has text values, it won't be possible to display line graph
        pass


# Battery charge percentage of the internal battery (laptops), from psutil
class BatteryLevel(CustomDataSource):
    # This list is used to store the last 10 values to display a line graph
    last_val = [math.nan] * 10

    def as_numeric(self) -> float:
        battery = psutil.sensors_battery()
        self.value = battery.percent if battery is not None else math.nan

        self.last_val.append(self.value)
        self.last_val.pop(0)

        return self.value

    def as_string(self) -> str:
        battery = psutil.sensors_battery()
        if battery is None:
            # Fixed-size placeholder when there is no battery
            return ' --'
        return f'{battery.percent:>3.0f}%'

    def last_values(self) -> List[float]:
        return self.last_val


# Currently logged-in user name (text-only: no graph possible)
class CurrentUser(CustomDataSource):
    def as_numeric(self) -> float:
        # If a custom data class only has text values, it won't be possible to display line graph
        pass

    def as_string(self) -> str:
        return getpass.getuser()

    def last_values(self) -> List[float]:
        pass


# Wi-Fi signal strength of the WLO interface from config.yaml. Text: level in dBm, numeric: link quality %
class WifiSignal(CustomDataSource):
    # This list is used to store the last 10 values to display a line graph
    last_val = [math.nan] * 10

    @staticmethod
    def _read_wireless():
        # Returns (link quality 0-100, signal level in dBm) of the wireless interface
        import subprocess

        import library.config as config

        if_name = str(config.CONFIG_DATA["config"].get("WLO", ""))
        # Preferred: iw (direct dBm reading, works with cfg80211 drivers)
        try:
            out = subprocess.run(["iw", "dev", if_name, "link"], capture_output=True, text=True,
                                 timeout=2).stdout
            for line in out.splitlines():
                if "signal:" in line:
                    level = float(line.split(":")[1].split()[0])
                    # Approximate link quality from dBm: -50dBm or better = 100%, -100dBm = 0%
                    quality = max(0.0, min(100.0, 2.0 * (level + 100.0)))
                    return quality, level
        except (OSError, ValueError, IndexError, subprocess.SubprocessError):
            pass
        # Fallback: /proc/net/wireless (link quality 0-70, level in dBm)
        try:
            with open("/proc/net/wireless", "rt") as f:
                lines = [l for l in f.readlines() if ":" in l]
            if lines:
                parts = lines[0].split()
                return min(100.0, max(0.0, float(parts[2]) / 70.0 * 100.0)), float(parts[3])
        except (OSError, ValueError, IndexError):
            pass
        return None, None

    def as_numeric(self) -> float:
        link, level = self._read_wireless()
        self.value = link if link is not None else math.nan

        self.last_val.append(self.value)
        self.last_val.pop(0)

        return self.value

    def as_string(self) -> str:
        link, level = self._read_wireless()
        if level is None:
            # No associated wireless interface: nothing to measure
            return ' -----'
        return f'{level:.0f}'

    def last_values(self) -> List[float]:
        return self.last_val


# OS distribution name and version from /etc/os-release, e.g. "Fedora 44" (text-only)
class OsName(CustomDataSource):
    def as_numeric(self) -> float:
        # If a custom data class only has text values, it won't be possible to display line graph
        pass

    def as_string(self) -> str:
        try:
            with open("/etc/os-release", "rt") as f:
                info = dict(
                    line.split("=", 1) for line in f.read().splitlines() if "=" in line
                )
            name = info.get("NAME", "").strip('"')
            if name.endswith(" Linux"):
                name = name[: -len(" Linux")]
            return (name + " " + info.get("VERSION_ID", "").strip('"')).strip()
        except OSError:
            # No os-release file (e.g. Windows/macOS): fall back to the platform name
            system = platform.system()
            if system == "Darwin":
                return ' macOS'
            return f' {system} {platform.release()}'.strip()

    def last_values(self) -> List[float]:
        pass


# CPU fan speed in RPM, for the fan selected by CPU_FAN in config.yaml ("controller/fan", e.g. thinkpad/fan2)
class FanRpm(CustomDataSource):
    # This list is used to store the last 10 values to display a line graph
    last_val = [math.nan] * 10

    @staticmethod
    def _read_fan_rpm():
        import glob
        import os

        import library.config as config

        fan_sel = str(config.CONFIG_DATA["config"].get("CPU_FAN", "AUTO"))
        try:
            if fan_sel and fan_sel != "AUTO" and "/" in fan_sel:
                controller, fan = fan_sel.split("/", 1)
                for name_file in glob.glob("/sys/class/hwmon/hwmon*/name"):
                    with open(name_file, "rt") as f:
                        if f.read().strip() == controller:
                            input_file = os.path.join(os.path.dirname(name_file), fan + "_input")
                            with open(input_file, "rt") as f:
                                return int(f.read().strip())
        except (OSError, ValueError):
            pass
        return None

    def as_numeric(self) -> float:
        rpm = self._read_fan_rpm()
        self.value = float(rpm) if rpm is not None else math.nan

        self.last_val.append(self.value)
        self.last_val.pop(0)

        return self.value

    def as_string(self) -> str:
        rpm = self._read_fan_rpm()
        if rpm is None:
            # Fixed-size placeholder when the fan cannot be read
            return ' -----'
        return f'{rpm} rpm'

    def last_values(self) -> List[float]:
        return self.last_val


# Local timezone abbreviation (e.g. "EDT"), or UTC offset when the name is too long (e.g. on Windows)
class Timezone(CustomDataSource):
    def as_numeric(self) -> float:
        # If a custom data class only has text values, it won't be possible to display line graph
        pass

    def as_string(self) -> str:
        import datetime

        now = datetime.datetime.now().astimezone()
        tz = now.tzname() or ""
        if len(tz) <= 4:
            return tz
        # Long timezone name: fall back to the UTC offset (e.g. "-04:00")
        offset = now.strftime("%z")
        return f"{offset[:3]}:{offset[3:]}" if offset else "?"

    def last_values(self) -> List[float]:
        pass


# Turn-signal style network activity indicators: blink while data flows in their direction
class _NetActivityIndicator:
    _prev = None                     # (monotonic time, per-interface counters) of last measurement
    _computed = (0.0, 0.0, 0.0)      # (computed at, upload rate B/s, download rate B/s)

    @staticmethod
    def _rates():
        import time

        import psutil

        import library.config as config

        now = time.monotonic()
        computed_at, sent_rate, recv_rate = _NetActivityIndicator._computed
        if now - computed_at < 0.5:
            # Both indicators are read within one refresh cycle: reuse the same window
            return sent_rate, recv_rate
        counters = psutil.net_io_counters(pernic=True)
        prev = _NetActivityIndicator._prev
        if prev is not None:
            prev_time, prev_counters = prev
            elapsed = max(now - prev_time, 0.001)
            if_name = str(config.CONFIG_DATA["config"].get("WLO", ""))
            if if_name in counters and if_name in prev_counters:
                sent_rate = (counters[if_name].bytes_sent - prev_counters[if_name].bytes_sent) / elapsed
                recv_rate = (counters[if_name].bytes_recv - prev_counters[if_name].bytes_recv) / elapsed
        _NetActivityIndicator._prev = (now, counters)
        _NetActivityIndicator._computed = (now, sent_rate, recv_rate)
        return sent_rate, recv_rate

    @staticmethod
    def _arrow(direction: str) -> str:
        import time

        sent_rate, recv_rate = _NetActivityIndicator._rates()
        rate = sent_rate if direction == "sent" else recv_rate
        if rate >= 512.0:
            lit = int(time.time()) % 4 < 2    # active: turn-signal blink, 2s on / 2s off
        else:
            lit = int(time.time()) % 10 < 2   # idle: courtesy blink once every 10s
        if not lit:
            return " "
        # Left indicator (download) points left, right indicator (upload) points right
        return "◀" if direction == "recv" else "▶"


class BlinkLeft(_NetActivityIndicator, CustomDataSource):
    """Download activity: blinks the left indicator while data is received."""

    def as_numeric(self) -> float:
        # If a custom data class only has text values, it won't be possible to display line graph
        pass

    def as_string(self) -> str:
        return self._arrow("recv")

    def last_values(self) -> List[float]:
        pass


class BlinkRight(_NetActivityIndicator, CustomDataSource):
    """Upload activity: blinks the right indicator while data is sent."""

    def as_numeric(self) -> float:
        # If a custom data class only has text values, it won't be possible to display line graph
        pass

    def as_string(self) -> str:
        return self._arrow("sent")

    def last_values(self) -> List[float]:
        pass


# Top processes by CPU usage: one row per sensor, sharing a single cached scan per refresh cycle
class _TopProcs:
    _cache = (0.0, 0, [])  # (computed at, process count, top rows)

    @staticmethod
    def _scan(n=10):
        import time

        import psutil

        now = time.monotonic()
        computed_at, count, rows = _TopProcs._cache
        if now - computed_at < 0.5:
            return count, rows
        entries = []
        for proc in psutil.process_iter(["pid", "name", "username"]):
            try:
                # cpu_percent(None) measures since the previous call on the same cached object
                entries.append((proc.info["pid"], proc.info["name"] or "?",
                                proc.cpu_percent(interval=None), proc.memory_percent(),
                                proc.info.get("username") or "?"))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        entries.sort(key=lambda e: e[2], reverse=True)
        count, rows = len(entries), entries[:n]
        _TopProcs._cache = (now, count, rows)
        return count, rows

    @staticmethod
    def _row(index: int) -> str:
        count, rows = _TopProcs._scan()
        if index >= len(rows):
            return " "  # no sample yet (first refresh) or fewer processes than rows
        pid, name, cpu, mem = rows[index][:4]
        return f"{name[:12]:<12}{cpu:4.0f}% {mem:4.1f}%"

    @staticmethod
    def _row_wide(index: int) -> str:
        count, rows = _TopProcs._scan()
        if index >= len(rows):
            return " "
        pid, name, cpu, mem, user = rows[index]
        # Fixed-width fields so columns stay pinned (values are capped to their field width)
        return (f"{pid:>9} {user[:8]:<8} {min(cpu, 9999):4.0f}% "
                f"{min(mem, 99.9):4.1f}% {name[:16]}")


class TopProc1(_TopProcs, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row(0)

    def last_values(self) -> List[float]:
        pass


class TopProc2(_TopProcs, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row(1)

    def last_values(self) -> List[float]:
        pass


class TopProc3(_TopProcs, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row(2)

    def last_values(self) -> List[float]:
        pass


class TopProc4(_TopProcs, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row(3)

    def last_values(self) -> List[float]:
        pass


class TopProc5(_TopProcs, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row(4)

    def last_values(self) -> List[float]:
        pass


class TopProc6(_TopProcs, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row(5)

    def last_values(self) -> List[float]:
        pass


class TopProc7(_TopProcs, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row(6)

    def last_values(self) -> List[float]:
        pass


class TopProc8(_TopProcs, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row(7)

    def last_values(self) -> List[float]:
        pass


class TopProc9(_TopProcs, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row(8)

    def last_values(self) -> List[float]:
        pass


class TopProc10(_TopProcs, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row(9)

    def last_values(self) -> List[float]:
        pass


# Wide ps-style rows (PID USER CPU% MEM% COMMAND) for the landscape table
class _TopProcsWide(_TopProcs):
    pass


class TopProcWide1(_TopProcsWide, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row_wide(0)

    def last_values(self) -> List[float]:
        pass


class TopProcWide2(_TopProcsWide, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row_wide(1)

    def last_values(self) -> List[float]:
        pass


class TopProcWide3(_TopProcsWide, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row_wide(2)

    def last_values(self) -> List[float]:
        pass


class TopProcWide4(_TopProcsWide, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row_wide(3)

    def last_values(self) -> List[float]:
        pass


class TopProcWide5(_TopProcsWide, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row_wide(4)

    def last_values(self) -> List[float]:
        pass


class TopProcWide6(_TopProcsWide, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row_wide(5)

    def last_values(self) -> List[float]:
        pass


class TopProcWide7(_TopProcsWide, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row_wide(6)

    def last_values(self) -> List[float]:
        pass


class TopProcWide8(_TopProcsWide, CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        return self._row_wide(7)

    def last_values(self) -> List[float]:
        pass


# Total number of running processes
class ProcessCount(CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        count, rows = _TopProcs._scan()
        return f"{count}"

    def last_values(self) -> List[float]:
        pass


# CPU temperature in Celsius, as a small companion next to a Fahrenheit main display (text-only)
class CpuTempCelsius(CustomDataSource):
    def as_numeric(self) -> float:
        # If a custom data class only has text values, it won't be possible to display line graph
        pass

    def as_string(self) -> str:
        # Use the sensors resolved by stats.py (respects HW_SENSORS setting)
        import library.stats as stats

        temp = stats.sensors.Cpu.temperature()
        return f'{temp:.0f}°C' if temp is not None else ' --°C'

    def last_values(self) -> List[float]:
        pass
