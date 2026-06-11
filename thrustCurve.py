from __future__ import annotations
import bisect


class ThrustCurve:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.name: str = ""
        self.diameter: float = 0.0
        self.length: float = 0.0
        self.delays: str = ""
        self.prop_mass: float = 0.0
        self.total_mass: float = 0.0
        self.manufacturer: str = ""
        self.data_points: list[tuple[float, float]] = []

        self._parse(filename)

    def get_thrust(self, time_ms: int) -> float:
        if not self.data_points:
            return 0.0

        time_s = time_ms / 1000.0
        times = [pt[0] for pt in self.data_points]

        if time_s <= times[0]:
            return self.data_points[0][1] if time_s == times[0] else 0.0
        if time_s >= times[-1]:
            return 0.0

        idx = bisect.bisect_right(times, time_s)
        t0, f0 = self.data_points[idx - 1]
        t1, f1 = self.data_points[idx]

        frac = (time_s - t0) / (t1 - t0)
        return f0 + frac * (f1 - f0)

    @property
    def burn_time(self) -> float:
        if not self.data_points:
            return 0.0
        return self.data_points[-1][0] - self.data_points[0][0]

    @property
    def peak_thrust(self) -> float:
        if not self.data_points:
            return 0.0
        return max(thrust for _, thrust in self.data_points)

    @property
    def average_thrust(self) -> float:
        if len(self.data_points) < 2:
            return 0.0
        total_impulse = 0.0
        for i in range(1, len(self.data_points)):
            t0, f0 = self.data_points[i - 1]
            t1, f1 = self.data_points[i]
            total_impulse += 0.5 * (f0 + f1) * (t1 - t0)
        return total_impulse / self.burn_time if self.burn_time else 0.0

    @property
    def total_impulse(self) -> float:
        if len(self.data_points) < 2:
            return 0.0
        total = 0.0
        for i in range(1, len(self.data_points)):
            t0, f0 = self.data_points[i - 1]
            t1, f1 = self.data_points[i]
            total += 0.5 * (f0 + f1) * (t1 - t0)
        return total

    def __repr__(self) -> str:
        return (
            f"EngParser(name={self.name!r}, manufacturer={self.manufacturer!r}, "
            f"diameter={self.diameter}mm, length={self.length}mm, "
            f"burn_time={self.burn_time:.3f}s, peak_thrust={self.peak_thrust:.1f}N, "
            f"total_impulse={self.total_impulse:.1f}Ns)"
        )

    def _parse(self, filename: str) -> None:
        header_parsed = False

        with open(filename, "r", encoding="utf-8", errors="replace") as fh:
            for raw_line in fh:
                line = raw_line.strip()

                if not line or line.startswith(";"):
                    continue

                if not header_parsed:
                    self._parse_header(line)
                    header_parsed = True
                else:
                    self._parse_data_point(line)

        if not header_parsed:
            raise ValueError(f"No motor header found in '{filename}'.")

        self.data_points.sort(key=lambda pt: pt[0])

    def _parse_header(self, line: str) -> None:
        parts = line.split()
        if len(parts) < 7:
            raise ValueError(
                f"Motor header must have 7 fields; got {len(parts)}: {line!r}"
            )
        self.name = parts[0]
        try:
            self.diameter = float(parts[1])
            self.length = float(parts[2])
        except ValueError as exc:
            raise ValueError(f"Non-numeric diameter/length in header: {line!r}") from exc
        self.delays = parts[3]
        try:
            self.prop_mass = float(parts[4])
            self.total_mass = float(parts[5])
        except ValueError as exc:
            raise ValueError(f"Non-numeric mass value in header: {line!r}") from exc
        self.manufacturer = " ".join(parts[6:])

    def _parse_data_point(self, line: str) -> None:
        parts = line.split()
        if len(parts) < 2:
            return

        try:
            t = float(parts[0])
            f = float(parts[1])
        except ValueError:
            return

        self.data_points.append((t, f))
