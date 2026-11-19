"""Per-video cancellation is scoped to the owner's VOD jobs and never stops live recordings."""
import os, sys, tempfile
os.environ["PEAKCUT_DATA"] = tempfile.mkdtemp(prefix="pc-cancel-")
os.environ["DATABASE_URL"] = ""
sys.path.insert(0, ".")
from studio import auth, ctx, jobs

fails = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  {detail}" if detail else ""))
    if not ok: fails.append(name)

a, _ = auth._create("cancel-a@example.com", "A", password_hash="x")
b, _ = auth._create("cancel-b@example.com", "B", password_hash="x")

def make(status="queued", kind="video"):
    j = jobs.create({"type": "url", "url": "https://example.com/video", "name": "test"},
                    {}, enqueue=False, kind=kind)
    j["status"] = status
    jobs.save(j)
    return j

with ctx.as_user(a.id):
    queued = make()
    result = jobs.cancel(queued["id"])
    check("queued job cancels immediately", result and result["status"] == "cancelled" and result["stage"] == "Cancelled")
    again = jobs.cancel(queued["id"])
    check("repeated cancellation is safe", again and again["status"] == "cancelled")

    running = make("running")
    result = jobs.cancel(running["id"])
    check("running job enters cancelling state", result and result["status"] == "cancelling")
    try:
        jobs._check_cancel(running)
        raised = False
    except jobs.JobCancelled:
        raised = True
    check("worker checkpoint observes the cancellation request", raised)

    live = make("live", "live")
    check("live recordings cannot be cancelled through the VOD action", jobs.cancel(live["id"]) is None)

    done = make("done")
    result = jobs.cancel(done["id"])
    check("finished jobs remain finished", result and result["status"] == "done")

with ctx.as_user(b.id):
    check("another user cannot cancel this job", jobs.cancel(running["id"]) is None)

print("ALL PASSED" if not fails else f"{len(fails)} failed")
import shutil
shutil.rmtree(os.environ["PEAKCUT_DATA"], ignore_errors=True)
sys.exit(1 if fails else 0)
