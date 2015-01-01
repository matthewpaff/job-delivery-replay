"""Original worker event traces; there is no live queue or job execution."""


def event(kind, key):
    return {"event": kind, "job_id": key}


def result(kind, key, outcome):
    return {"event": kind, "job_id": key, "outcome": outcome}


def job(key, status, attempts):
    return {"job_id": key, "status": status, "attempts": attempts}


def make_case(index):
    key, kind = "job-{}".format(index), index % 10
    data = {"max_attempts": 3, "events": []}
    if kind == 0:
        data["events"] = [event("deliver", key)]
        description = "reject deliveries for jobs that were not enqueued"
    elif kind == 1:
        data["max_attempts"] = 0
        description = "reject zero-attempt delivery policies"
    elif kind == 2:
        data["events"] = [event("enqueue", " ")]
        description = "reject blank job identifiers"
    elif kind == 3:
        data["events"] = [event("unknown", key)]
        description = "reject unsupported worker event kinds"
    elif kind == 4:
        data["events"] = [event("enqueue", key), event("deliver", key), event("fail", key)]
        description = "reject failure events for completed jobs"
    elif kind == 5:
        data["events"] = [event("enqueue", key), event("deliver", key), event("deliver", key)]
        expected = {"results": [result("enqueue", key, "queued"), result("deliver", key, "processed"), result("deliver", key, "duplicate")], "jobs": [job(key, "done", 1)]}
        description = "deduplicate repeated successful deliveries"
    elif kind == 6:
        data["events"] = [event("enqueue", key), event("enqueue", key), event("deliver", key)]
        expected = {"results": [result("enqueue", key, "queued"), result("enqueue", key, "duplicate"), result("deliver", key, "processed")], "jobs": [job(key, "done", 1)]}
        description = "deduplicate repeated enqueue events"
    elif kind == 7:
        data["events"] = [event("enqueue", key), event("fail", key), event("deliver", key)]
        expected = {"results": [result("enqueue", key, "queued"), result("fail", key, "retry"), result("deliver", key, "processed")], "jobs": [job(key, "done", 2)]}
        description = "complete a job after a retryable failed attempt"
    elif kind == 8:
        data.update({"max_attempts": 2, "events": [event("enqueue", key), event("fail", key), event("fail", key), event("deliver", key)]})
        expected = {"results": [result("enqueue", key, "queued"), result("fail", key, "retry"), result("fail", key, "dead"), result("deliver", key, "dead")], "jobs": [job(key, "dead", 2)]}
        description = "keep exhausted jobs in the dead-letter state"
    else:
        other = key + "-b"
        data["events"] = [event("enqueue", other), event("enqueue", key), event("deliver", key)]
        expected = {"results": [result("enqueue", other, "queued"), result("enqueue", key, "queued"), result("deliver", key, "processed")], "jobs": [job(key, "done", 1), job(other, "pending", 0)]}
        description = "isolate state and attempts across independent jobs"
    output = {"id": "jobs-{:04d}".format(index), "description": description, "input": data}
    output.update({"expected_error": True} if kind < 5 else {"expected": expected})
    return output
