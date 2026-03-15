from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.request import urlretrieve

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

LOG_URL = "https://max.ge/aiml_final/a_bliadze25_42198_server.log"
LOCAL_LOG = Path("a_bliadze25_42198_server.log")

LOG_PATTERN = re.compile(
    r'(?P<ip>[\d.]+) - - '
    r'\[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>\w+) (?P<url>[^\s]+) (?P<proto>HTTP/[^\"]+)" '
    r'(?P<status>\d{3}) (?P<size>\d+) '
    r'"(?P<referrer>[^\"]*)" "(?P<user_agent>[^\"]*)" (?P<response_time>\d+)'
)


def ensure_log_file(force_download: bool = False) -> Path:
    if force_download or (not LOCAL_LOG.exists()):
        print(f"Downloading dataset from: {LOG_URL}")
        urlretrieve(LOG_URL, LOCAL_LOG)
        print(f"Saved log file: {LOCAL_LOG.resolve()}")
    else:
        print(f"Using existing log file: {LOCAL_LOG.resolve()}")
    return LOCAL_LOG


def parse_log(path: Path) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            match = LOG_PATTERN.match(line.strip())
            if match:
                rows.append(match.groupdict())

    if not rows:
        raise ValueError("No rows parsed from provided log file.")

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"]).copy()
    df["status"] = df["status"].astype(int)
    return df


def build_series(df: pd.DataFrame) -> pd.DataFrame:
    ts = (
        df.set_index("timestamp")
        .resample("1min")
        .agg(
            requests=("ip", "count"),
            unique_ips=("ip", "nunique"),
            error_rate=("status", lambda s: (s >= 400).mean()),
        )
    )
    return ts.fillna(0)


def detect_intervals(ts: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, object]], float]:
    y = ts["requests"].to_numpy(dtype=float)
    x = np.arange(len(ts)).reshape(-1, 1)

    poly = PolynomialFeatures(degree=3, include_bias=True)
    x_poly = poly.fit_transform(x)

    model_initial = LinearRegression().fit(x_poly, y)
    pred_initial = model_initial.predict(x_poly)
    residual_initial = y - pred_initial

    keep_mask = ~((y > np.quantile(y, 0.95)) & (residual_initial > 0))
    model = LinearRegression().fit(x_poly[keep_mask], y[keep_mask])

    predicted = model.predict(x_poly)
    residual = y - predicted
    sigma = np.std(residual[keep_mask])

    is_attack = (residual > 3 * sigma) & (y > 1.8 * predicted)

    out = ts.copy()
    out["predicted"] = predicted
    out["residual"] = residual
    out["is_attack"] = is_attack

    intervals: list[dict[str, object]] = []
    start_idx: int | None = None

    for i, flag in enumerate(is_attack):
        if flag and start_idx is None:
            start_idx = i
        elif (not flag) and start_idx is not None:
            end_idx = i - 1
            segment = out.iloc[start_idx : end_idx + 1]
            intervals.append(
                {
                    "start_utc": segment.index[0],
                    "end_utc": segment.index[-1],
                    "duration_min": len(segment),
                    "peak_requests": int(segment["requests"].max()),
                    "total_requests": int(segment["requests"].sum()),
                    "peak_unique_ips": int(segment["unique_ips"].max()),
                }
            )
            start_idx = None

    if start_idx is not None:
        segment = out.iloc[start_idx:]
        intervals.append(
            {
                "start_utc": segment.index[0],
                "end_utc": segment.index[-1],
                "duration_min": len(segment),
                "peak_requests": int(segment["requests"].max()),
                "total_requests": int(segment["requests"].sum()),
                "peak_unique_ips": int(segment["unique_ips"].max()),
            }
        )

    return out, intervals, sigma


def save_plot(ts: pd.DataFrame, intervals: list[dict[str, object]], sigma: float) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    x = np.arange(len(ts))

    axes[0].plot(x, ts["requests"], label="Actual requests/min", linewidth=1.8)
    axes[0].plot(x, ts["predicted"], label="Regression baseline", linestyle="--", linewidth=2)
    axes[0].set_ylabel("Requests/min")
    axes[0].set_title("DDoS Detection using Regression Analysis")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    axes[1].plot(x, ts["residual"], color="tab:orange", linewidth=1.5, label="Residual")
    axes[1].axhline(3 * sigma, color="red", linestyle="--", label="+3σ threshold")
    axes[1].axhline(0, color="black", linewidth=1)
    axes[1].set_ylabel("Residual")
    axes[1].grid(alpha=0.3)
    axes[1].legend()

    axes[2].plot(x, ts["unique_ips"], color="tab:green", linewidth=1.5, label="Unique IPs/min")
    axes[2].set_ylabel("Unique IPs/min")
    axes[2].set_xlabel("Minute index")
    axes[2].grid(alpha=0.3)
    axes[2].legend()

    for interval in intervals:
        start = ts.index.get_loc(interval["start_utc"])
        end = ts.index.get_loc(interval["end_utc"])
        for ax in axes:
            ax.axvspan(start, end, color="red", alpha=0.22)

    plt.tight_layout()
    plt.savefig("ddos_analysis.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Saved visualization: ddos_analysis.png")


def main() -> None:
    parser = argparse.ArgumentParser(description="Regression-based DDoS interval detection")
    parser.add_argument("--force-download", action="store_true", help="Re-download official dataset")
    args = parser.parse_args()

    path = ensure_log_file(force_download=args.force_download)
    df = parse_log(path)
    ts = build_series(df)
    ts, intervals, sigma = detect_intervals(ts)

    print("\n===== DATA SUMMARY =====")
    print(f"Parsed rows: {len(df)}")
    print(f"Time span: {ts.index.min()} -> {ts.index.max()}")
    print(f"Mean requests/min: {ts['requests'].mean():.2f}")
    print(f"Max requests/min: {int(ts['requests'].max())}")
    print(f"Residual baseline sigma: {sigma:.2f}")

    print("\n===== DETECTED DDoS INTERVAL(S) =====")
    if not intervals:
        print("No attack interval detected with current thresholds.")
    else:
        for i, interval in enumerate(intervals, 1):
            s = interval["start_utc"]
            e = interval["end_utc"]
            print(f"Attack #{i}")
            print(f"  UTC:   {s} -> {e}")
            print(f"  +04:00 {s.tz_convert('Etc/GMT-4')} -> {e.tz_convert('Etc/GMT-4')}")
            print(f"  Duration (minutes): {interval['duration_min']}")
            print(f"  Peak requests/min:  {interval['peak_requests']}")
            print(f"  Total requests:     {interval['total_requests']}")
            print(f"  Peak unique IPs:    {interval['peak_unique_ips']}")

    save_plot(ts, intervals, sigma)
    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
