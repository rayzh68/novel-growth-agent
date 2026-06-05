from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


NUMERIC_COLUMNS = [
    "impressions", "clicks", "spend", "landing_views", "start_reading_click",
    "read_start", "chapter_1_finish", "chapter_3_finish", "gate_view",
    "unlock_click", "ad_watch_start", "ad_watch_complete", "subscribe_click", "revenue"
]


def read_csv_folder(folder: Path) -> pd.DataFrame:
    frames = []
    if not folder.exists():
        return pd.DataFrame()
    for path in folder.glob("*.csv"):
        try:
            frames.append(pd.read_csv(path))
        except Exception as exc:
            print(f"[WARN] Failed to read {path}: {exc}")
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def normalize_numeric(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def safe_div(num: float, den: float) -> float:
    return float(num) / float(den) if den else 0.0


def aggregate_metrics(df: pd.DataFrame, by: List[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    df = normalize_numeric(df)
    for col in by:
        if col not in df.columns:
            df[col] = "unknown"
    grouped = df.groupby(by, dropna=False)[NUMERIC_COLUMNS].sum().reset_index()
    grouped["ctr"] = grouped.apply(lambda r: safe_div(r["clicks"], r["impressions"]), axis=1)
    grouped["cpc"] = grouped.apply(lambda r: safe_div(r["spend"], r["clicks"]), axis=1)
    grouped["landing_view_rate"] = grouped.apply(lambda r: safe_div(r["landing_views"], r["clicks"]), axis=1)
    grouped["read_start_rate"] = grouped.apply(lambda r: safe_div(r["read_start"], r["landing_views"]), axis=1)
    grouped["chapter_1_finish_rate"] = grouped.apply(lambda r: safe_div(r["chapter_1_finish"], r["read_start"]), axis=1)
    grouped["chapter_3_finish_rate"] = grouped.apply(lambda r: safe_div(r["chapter_3_finish"], r["read_start"]), axis=1)
    grouped["gate_view_rate"] = grouped.apply(lambda r: safe_div(r["gate_view"], r["read_start"]), axis=1)
    grouped["unlock_click_rate"] = grouped.apply(lambda r: safe_div(r["unlock_click"], r["gate_view"]), axis=1)
    grouped["ad_watch_complete_rate"] = grouped.apply(lambda r: safe_div(r["ad_watch_complete"], r["ad_watch_start"]), axis=1)
    grouped["revenue_per_click"] = grouped.apply(lambda r: safe_div(r["revenue"], r["clicks"]), axis=1)
    grouped["revenue_per_landing_view"] = grouped.apply(lambda r: safe_div(r["revenue"], r["landing_views"]), axis=1)
    grouped["roi"] = grouped.apply(lambda r: safe_div(r["revenue"], r["spend"]), axis=1)
    grouped["net_profit"] = grouped["revenue"] - grouped["spend"]

    # Diagnostic only, not final goal.
    # Lower CPC is better. Clamp basic signals to 0-1 using practical thresholds.
    grouped["early_appeal_signal"] = grouped.apply(
        lambda r: (
            0.55 * min(r["ctr"] / 0.03, 1.0)
            + 0.25 * min(0.8 / r["cpc"], 1.0) if r["cpc"] > 0 else 0
        ) + 0.20 * min(r["landing_view_rate"] / 0.8, 1.0),
        axis=1,
    )
    grouped["appeal_signal"] = grouped.apply(
        lambda r: (
            0.20 * min(r["ctr"] / 0.03, 1.0)
            + (0.15 * min(0.8 / r["cpc"], 1.0) if r["cpc"] > 0 else 0)
            + 0.20 * min(r["read_start_rate"] / 0.5, 1.0)
            + 0.20 * min(r["chapter_1_finish_rate"] / 0.35, 1.0)
            + 0.15 * min(r["chapter_3_finish_rate"] / 0.2, 1.0)
            + 0.10 * min(r["unlock_click_rate"] / 0.05, 1.0)
        ),
        axis=1,
    )
    return grouped.sort_values(["roi", "net_profit", "appeal_signal"], ascending=False)


def merge_ad_site(ad_df: pd.DataFrame, site_df: pd.DataFrame) -> pd.DataFrame:
    if ad_df.empty and site_df.empty:
        return pd.DataFrame()

    ad_df = normalize_numeric(ad_df) if not ad_df.empty else pd.DataFrame()
    site_df = normalize_numeric(site_df) if not site_df.empty else pd.DataFrame()

    keys = ["date", "utm_source", "utm_campaign", "utm_content", "utm_term"]

    if ad_df.empty:
        return site_df
    if site_df.empty:
        return ad_df

    for key in keys:
        if key not in ad_df.columns:
            ad_df[key] = "unknown"
        if key not in site_df.columns:
            site_df[key] = "unknown"

    ad_agg = ad_df.groupby(keys, dropna=False)[["impressions", "clicks", "spend", "landing_views"]].sum().reset_index()
    site_cols = [
        "start_reading_click", "read_start", "chapter_1_finish", "chapter_3_finish",
        "gate_view", "unlock_click", "ad_watch_start", "ad_watch_complete", "subscribe_click", "revenue"
    ]
    site_agg = site_df.groupby(keys, dropna=False)[site_cols].sum().reset_index()
    return pd.merge(ad_agg, site_agg, on=keys, how="outer").fillna(0)
