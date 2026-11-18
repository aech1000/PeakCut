"""Clipverse scoring is deterministic, bounded and independent of external AI services."""
import os, sys, tempfile
os.environ["PEAKCUT_DATA"] = tempfile.mkdtemp(prefix="pc-scoring-")
sys.path.insert(0, ".")
from studio.scoring import score_clip

fails = []
def check(name, got, want=True):
    ok = want(got) if callable(want) else got == want
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"   got {got!r}"))
    if not ok:
        fails.append(name)

words = [{"w": f"word{i}", "s": i * 0.4, "e": i * 0.4 + 0.2} for i in range(75)]
clip = {"start": 0, "end": 30, "score": 90, "category": "clutch"}
quiet = score_clip(clip, words, [0.0] * 31)
loud = score_clip(clip, words, [2.0] * 31)
check("score has expected fields", set(quiet), {"clipverse_score", "clipverse_tier", "clipverse_breakdown"})
check("score stays within 0-100", 0 <= quiet["clipverse_score"] <= 100, True)
check("stronger audio increases score", loud["clipverse_score"] > quiet["clipverse_score"], True)
check("clutch category receives its category score", quiet["clipverse_breakdown"]["category"], 95)
check("breakdown includes all five signals", set(quiet["clipverse_breakdown"]),
      {"ai_moment", "audio_energy", "transcript", "category", "duration"})
check("invalid AI score is handled safely",
      0 <= score_clip({"start": 0, "end": 20, "score": float("nan")}, [], [0] * 21)["clipverse_score"] <= 100, True)
check("empty signals do not crash",
      isinstance(score_clip({"start": 0, "end": 20}, [], [] )["clipverse_tier"], str), True)
check("category is case-insensitive",
      score_clip({"start": 0, "end": 30, "score": 80, "category": "CLUTCH"}, words, [0] * 31)
      ["clipverse_breakdown"]["category"], 95)
print("ALL PASSED" if not fails else f"{len(fails)} FAILED")
sys.exit(1 if fails else 0)
