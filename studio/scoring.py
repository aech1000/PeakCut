"""Evidence-based ranking for PeakCut clips.

This layer reuses PeakCut's existing AI judgement and adds inexpensive signals
already available during transcription. It makes no extra AI/API calls.
"""
import math


CATEGORY_SCORES = {
    "clutch": 95,
    "funny": 92,
    "shock": 92,
    "fail": 86,
    "rage": 84,
    "story": 80,
    "take": 76,
    "other": 60,
}


def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))


def _number(value, default=0.0):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _percentile(values, percentile):
    if not values:
        return None
    values = sorted(values)
    index = (len(values) - 1) * percentile
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)
    fraction = index - lower
    return values[lower] * (1 - fraction) + values[upper] * fraction


def score_clip(clip, words, loudness_z, min_len=15, max_len=60):
    """Return Clipverse score fields for one clip.

    Inputs are local to the source video: transcript word timestamps in seconds
    and the per-second loudness z-score array produced by brain.loud_zscore().
    Missing signals receive neutral values rather than being treated as proof
    that a clip is poor.
    """
    start = max(0.0, _number(clip.get("start")))
    end = max(start, _number(clip.get("end")))
    duration = end - start

    ai_score = _clamp(_number(clip.get("score"), 50.0))
    category = str(clip.get("category") or "other").lower()
    category_score = CATEGORY_SCORES.get(category, CATEGORY_SCORES["other"])

    # Use the 90th percentile rather than the single loudest second, which is
    # less sensitive to a click/pop or one corrupt audio sample.
    try:
        loud_values = [
            _number(loudness_z[i])
            for i in range(max(0, int(start)), min(len(loudness_z), int(math.ceil(end))))
        ]
    except (TypeError, IndexError):
        loud_values = []
    p90 = _percentile(loud_values, 0.90)
    audio_score = 50.0 if p90 is None else _clamp(50.0 + 15.0 * p90)

    spoken = 0
    for word in words or []:
        t = _number(word.get("s"), -1)
        if start <= t <= end and str(word.get("w") or "").strip():
            spoken += 1
    words_per_second = spoken / duration if duration > 0 else 0.0
    # Reward a legible amount of speech without assuming that faster speech is
    # always better. Quiet gameplay moments can still score through other signals.
    transcript_score = _clamp(100.0 - abs(words_per_second - 2.5) * 25.0)

    min_len = max(1.0, _number(min_len, 15.0))
    max_len = max(min_len, _number(max_len, 60.0))
    ideal = _clamp(30.0, min_len, max_len)
    duration_score = _clamp(100.0 - abs(duration - ideal) * (35.0 / max(1.0, max_len - min_len)))

    breakdown = {
        "ai_moment": round(ai_score),
        "audio_energy": round(audio_score),
        "transcript": round(transcript_score),
        "category": round(category_score),
        "duration": round(duration_score),
    }
    total = (
        ai_score * 0.35
        + audio_score * 0.20
        + transcript_score * 0.20
        + category_score * 0.15
        + duration_score * 0.10
    )
    score = round(_clamp(total))
    tier = "Must publish" if score >= 85 else "Strong" if score >= 70 else "Review" if score >= 50 else "Skip"
    return {
        "clipverse_score": score,
        "clipverse_tier": tier,
        "clipverse_breakdown": breakdown,
    }
