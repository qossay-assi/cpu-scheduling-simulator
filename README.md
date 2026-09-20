# CPU Scheduling Simulator

Simulate a single CPU using priority scheduling, aging and multilevel feedback queues, with processes returning after I/O.

## Run
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
Enter one process per line: `PID, arrival, CPU burst, I/O burst, priority`. Lower numbers mean higher priority. The GUI exports a per-tick CSV timeline.

## Scheduling semantics
- Non-preemptive priority: higher-priority arrivals do not interrupt the running burst. Equal-priority processes rotate every two ticks.
- Preemptive priority: a higher-priority ready process preempts on the next tick; five waiting ticks improve priority by one, bounded at zero. Equal priorities use a two-tick quantum.
- MLFQ: RR with quantum 8, then RR 16, then FCFS, following the recovered assignment diagram. Higher queues preempt lower ones. I/O completion returns to the top queue; priority/aging state resets for a new burst.

The horizon defaults to 300 ticks. Waiting and turnaround means are computed over **completed CPU bursts**; partially completed bursts are excluded. Turnaround begins at initial arrival or I/O completion. CPU utilization includes all executed ticks. These conventions resolve details not fully specified by the original report.

## Recovery and fixes
Recovered the original program from its ZIP archive. Replaced the erroneous one-burst scheduling core with a tick-based model that implements I/O recurrence. Corrected preemption, aging, equal-priority RR, queue quanta, input ordering, idle periods and timeline widths. Replaced fixed Tk charts with a configurable Streamlit interface. This is a substantial later reconstruction, not an unchanged historical submission.

## Validation
```bash
python -m unittest -v
```
Six regression tests passed: preemption, equal-priority rotation, repeated I/O and metrics, MLFQ quantum, idle/horizon handling and aging. Streamlit's Simulate action also passed AppTest.

## Attribution
The recovered submission archive is named for Qusai Assi. No additional author was identified in that archive.

## License
MIT for this repository's project code; dependencies retain their own licenses. See `LICENSE`.
