"""Replay explicit enqueue/success/failure events without a broker or worker process."""


def replay_jobs(data):
    if not isinstance(data, dict) or not isinstance(data.get("events"), list) or len(data["events"]) > 1000:
        raise ValueError("Supply an object with at most 1000 events")
    maximum = data.get("max_attempts", 3)
    if type(maximum) is not int or not 1 <= maximum <= 10:
        raise ValueError("max_attempts must be an integer from 1 to 10")
    jobs, results = {}, []
    for event in data["events"]:
        if not isinstance(event, dict) or set(event) != {"event", "job_id"}:
            raise ValueError("Each event requires event and job_id")
        kind, key = event["event"], event["job_id"]
        if kind not in ("enqueue", "deliver", "fail") or not isinstance(key, str) or not 1 <= len(key.strip()) <= 80:
            raise ValueError("Invalid event kind or job ID")
        if kind == "enqueue":
            outcome = "duplicate" if key in jobs else "queued"
            jobs.setdefault(key, {"job_id": key, "status": "pending", "attempts": 0})
        else:
            if key not in jobs:
                raise ValueError("Cannot process a job that was not enqueued")
            job = jobs[key]
            if job["status"] == "done":
                if kind == "fail":
                    raise ValueError("Cannot fail a completed job")
                outcome = "duplicate"
            elif job["status"] == "dead":
                outcome = "dead"
            else:
                job["attempts"] += 1
                if kind == "deliver":
                    job["status"], outcome = "done", "processed"
                elif job["attempts"] >= maximum:
                    job["status"], outcome = "dead", "dead"
                else:
                    outcome = "retry"
        results.append({"event": kind, "job_id": key, "outcome": outcome})
    return {"results": results, "jobs": [jobs[key] for key in sorted(jobs)]}
