import streamlit as st
import matplotlib.pyplot as plt
from scheduling import Process, simulate

st.set_page_config(page_title="CPU Scheduling Simulator", layout="wide")
st.title("CPU Scheduling Simulator")
st.caption(
    "Priority scheduling, aging and multilevel feedback queues with recurring I/O."
)
algorithm = st.selectbox("Algorithm", ["nonpreemptive", "preemptive", "mlfq"])
horizon = st.slider("Simulation horizon", 20, 1000, 300)
repeat_io = st.checkbox("Return processes after I/O", value=True)
source = st.text_area(
    "Processes: PID, arrival, CPU burst, I/O burst, priority",
    "1,0,15,5,3\n2,1,23,14,2\n3,3,14,6,3\n4,4,16,15,1\n5,6,10,13,0\n6,7,22,4,1\n7,8,28,10,2",
)
if st.button("Simulate"):
    try:
        processes = [
            Process(*map(int, line.split(",")))
            for line in source.splitlines()
            if line.strip()
        ]
        trace, waiting, turnaround = simulate(processes, algorithm, horizon, repeat_io)
    except (ValueError, TypeError) as exc:
        st.error(str(exc))
        st.stop()
    a, b, c = st.columns(3)
    a.metric("Mean waiting / completed burst", f"{waiting:.2f}")
    b.metric("Mean turnaround / completed burst", f"{turnaround:.2f}")
    c.metric("CPU utilization", f"{100*len(trace)/horizon:.1f}%")
    fig, ax = plt.subplots(figsize=(12, 4))
    identifiers = sorted({p.pid for p in processes})
    for t, pid in trace:
        row = identifiers.index(pid)
        ax.broken_barh([(t, 1)], (row - 0.35, 0.7), facecolors=f"C{row % 10}")
    ax.set(
        yticks=range(len(identifiers)),
        yticklabels=[f"P{x}" for x in identifiers],
        xlabel="Time",
        xlim=(0, horizon),
    )
    st.pyplot(fig)
    st.caption(
        "Means exclude CPU bursts unfinished at the horizon. MLFQ uses RR 8, RR 16, then FCFS; I/O completion returns to the top queue."
    )
    st.download_button(
        "Download timeline CSV",
        "time,pid\n" + "".join(f"{t},{pid}\n" for t, pid in trace),
        "timeline.csv",
    )
