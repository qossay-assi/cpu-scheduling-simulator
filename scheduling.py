"""CPU scheduling with recurring I/O, priority aging and multilevel queues."""

from dataclasses import dataclass
from copy import deepcopy
from collections import deque


@dataclass
class Process:
    pid: int
    arrival_time: int
    cpu_burst_time: int
    io_burst_time: int
    priority: int


def _prepare(processes):
    items = deepcopy(processes)
    if len({p.pid for p in items}) != len(items):
        raise ValueError("Process IDs must be unique")
    for p in items:
        if (
            not isinstance(p.arrival_time, int)
            or p.arrival_time < 0
            or not isinstance(p.cpu_burst_time, int)
            or p.cpu_burst_time <= 0
        ):
            raise ValueError(
                "Arrival must be a nonnegative integer and CPU burst a positive integer"
            )
        p.remaining_time = p.cpu_burst_time
        p.age = 0
    return sorted(items, key=lambda p: p.arrival_time)


def simulate(
    processes,
    algorithm="nonpreemptive",
    horizon=300,
    repeat_io=True,
    quanta=(8, 16, float("inf")),
):
    """Return per-tick Gantt trace and means over completed CPU bursts.

    Turnaround is measured from initial arrival or I/O completion to CPU completion.
    Bursts unfinished at the horizon are excluded from mean waiting/turnaround.
    Equal-priority processes use round robin with a two-tick quantum.
    MLFQ processes return from I/O to queue zero; a higher queue preempts immediately.
    """
    if algorithm not in {"nonpreemptive", "preemptive", "mlfq"}:
        raise ValueError("Unknown algorithm")
    if not isinstance(horizon, int) or horizon <= 0 or any(q <= 0 for q in quanta):
        raise ValueError("Horizon and quanta must be positive")
    items = _prepare(processes)
    for p in items:
        if not isinstance(p.io_burst_time, int) or p.io_burst_time < 0:
            raise ValueError("I/O bursts must be nonnegative integers")
        p.next_ready = p.arrival_time
        p.burst_ready = p.arrival_time
        p.base_priority = p.priority
        p.level = 0
        p.slice_used = 0
        p.waited = 0
    blocked = items[:]
    ready = []
    current = None
    chart, waits, turns = [], [], []
    for clock in range(horizon):
        for p in blocked[:]:
            if p.next_ready <= clock:
                blocked.remove(p)
                p.burst_ready = clock
                p.remaining_time = p.cpu_burst_time
                p.priority = p.base_priority
                p.age = p.waited = p.slice_used = p.level = 0
                ready.append(p)
        key = (lambda p: p.level) if algorithm == "mlfq" else (lambda p: p.priority)
        if current is not None and ready and algorithm != "nonpreemptive":
            if min(key(p) for p in ready) < key(current):
                ready.insert(0, current)
                current = None
        if current is None and ready:
            current = min(ready, key=key)
            ready.remove(current)
            current.age = 0
        if current is None:
            continue
        chart.append((clock, current.pid))
        current.remaining_time -= 1
        current.slice_used += 1
        for p in ready:
            p.waited += 1
            if algorithm == "preemptive":
                p.age += 1
                if p.age >= 5:
                    p.priority = max(0, p.priority - 1)
                    p.age = 0
        if current.remaining_time == 0:
            waits.append(current.waited)
            turns.append(clock + 1 - current.burst_ready)
            if repeat_io:
                current.next_ready = clock + 1 + current.io_burst_time
                blocked.append(current)
            current = None
        elif algorithm == "mlfq" and current.slice_used >= quanta[current.level]:
            current.level = min(current.level + 1, len(quanta) - 1)
            current.slice_used = 0
            ready.append(current)
            current = None
        elif algorithm != "mlfq" and current.slice_used >= 2:
            current.slice_used = 0
            if any(p.priority == current.priority for p in ready):
                # Non-preemptive priority: rotate only within the active priority.
                same = next(p for p in ready if p.priority == current.priority)
                ready.remove(same)
                ready.append(current)
                current = same
                current.age = 0
    return (
        chart,
        (sum(waits) / len(waits) if waits else 0.0),
        (sum(turns) / len(turns) if turns else 0.0),
    )


def simulate_non_preemptive_priority(processes, **kwargs):
    return simulate(processes, "nonpreemptive", **kwargs)


def simulate_preemptive_priority(processes, **kwargs):
    return simulate(processes, "preemptive", **kwargs)


def simulate_multilevel_feedback_queue(processes, **kwargs):
    return simulate(processes, "mlfq", **kwargs)
