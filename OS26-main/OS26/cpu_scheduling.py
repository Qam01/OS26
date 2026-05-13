from collections import deque


def run_algorithm(name, data, quantum):
    """
    Run the given scheduling algorithm.
    Returns: (output_text: str, gantt_data: list of (pid, start, end))
    """
    try:
        procs = []
        for i, p in enumerate(data.replace(' ', '').split(';')):
            p = p.strip()
            if not p:
                continue
            at, bt = map(int, p.split(','))
            procs.append({
                'id': f"P{i+1}",
                'at': at,
                'bt': bt,
                'rem': bt,
                'wt': 0,
                'tat': 0
            })

        if not procs:
            return "Error: No processes provided.", []

        gantt = []
        time = 0
        finished = []

        # ── FCFS ──────────────────────────────────────────────────────────────
        if name == "FCFS":
            procs.sort(key=lambda x: x['at'])
            for p in procs:
                if time < p['at']:
                    gantt.append(("IDLE", time, p['at']))
                    time = p['at']
                p['wt'] = time - p['at']
                gantt.append((p['id'], time, time + p['bt']))
                time += p['bt']
                p['tat'] = p['wt'] + p['bt']
            finished = procs

        # ── SJF Non-Preemptive ────────────────────────────────────────────────
        elif name == "SJF-NP":
            remaining = list(procs)
            while remaining:
                available = [p for p in remaining if p['at'] <= time]
                if not available:
                    next_at = min(p['at'] for p in remaining)
                    gantt.append(("IDLE", time, next_at))
                    time = next_at
                    continue
                # Tie-break: shortest burst then earliest arrival
                curr = min(available, key=lambda x: (x['bt'], x['at']))
                curr['wt'] = time - curr['at']
                gantt.append((curr['id'], time, time + curr['bt']))
                time += curr['bt']
                curr['tat'] = curr['wt'] + curr['bt']
                finished.append(curr)
                remaining.remove(curr)

        # ── SJF Preemptive (SRTF) ─────────────────────────────────────────────
        elif name == "SJF-P":
            remaining = [dict(p) for p in procs]
            n = len(remaining)
            done = 0
            prev_id = None
            seg_start = 0

            while done < n:
                available = [p for p in remaining if p['at'] <= time and p['rem'] > 0]
                if not available:
                    next_at = min(p['at'] for p in remaining if p['rem'] > 0)
                    if prev_id is not None:
                        gantt.append((prev_id, seg_start, time))
                        prev_id = None
                    gantt.append(("IDLE", time, next_at))
                    time = next_at
                    seg_start = time
                    continue

                # Tie-break: shortest remaining then earliest arrival
                curr = min(available, key=lambda x: (x['rem'], x['at']))

                if prev_id != curr['id']:
                    if prev_id is not None:
                        gantt.append((prev_id, seg_start, time))
                    seg_start = time
                    prev_id = curr['id']

                curr['rem'] -= 1
                time += 1

                if curr['rem'] == 0:
                    gantt.append((curr['id'], seg_start, time))
                    prev_id = None
                    curr['tat'] = time - curr['at']
                    curr['wt'] = curr['tat'] - curr['bt']
                    done += 1

            id_map = {p['id']: p for p in remaining}
            for p in procs:
                p['wt'] = id_map[p['id']]['wt']
                p['tat'] = id_map[p['id']]['tat']
            finished = procs

        # ── Round Robin ───────────────────────────────────────────────────────
        elif name == "RR":
            try:
                q = int(quantum)
                if q <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return "Error: Quantum must be a positive integer.", []

            remaining = [dict(p) for p in procs]
            remaining.sort(key=lambda x: x['at'])
            queue = deque()
            time = 0
            idx = 0
            n = len(remaining)
            done = 0

            while idx < n and remaining[idx]['at'] <= time:
                queue.append(remaining[idx])
                idx += 1

            if not queue and idx < n:
                time = remaining[0]['at']
                queue.append(remaining[0])
                idx = 1

            while done < n:
                if not queue:
                    next_at = remaining[idx]['at']
                    gantt.append(("IDLE", time, next_at))
                    time = next_at
                    while idx < n and remaining[idx]['at'] <= time:
                        queue.append(remaining[idx])
                        idx += 1

                curr = queue.popleft()
                run_time = min(q, curr['rem'])
                gantt.append((curr['id'], time, time + run_time))
                time += run_time
                curr['rem'] -= run_time

                while idx < n and remaining[idx]['at'] <= time:
                    queue.append(remaining[idx])
                    idx += 1

                if curr['rem'] == 0:
                    curr['tat'] = time - curr['at']
                    curr['wt'] = curr['tat'] - curr['bt']
                    done += 1
                else:
                    queue.append(curr)

            id_map = {p['id']: p for p in remaining}
            for p in procs:
                p['wt'] = id_map[p['id']]['wt']
                p['tat'] = id_map[p['id']]['tat']
            finished = procs

        else:
            return f"Unknown algorithm: {name}", []

        # ── Merge consecutive same-process gantt segments ─────────────────────
        merged = []
        for seg in gantt:
            if merged and merged[-1][0] == seg[0] and merged[-1][2] == seg[1]:
                merged[-1] = (merged[-1][0], merged[-1][1], seg[2])
            else:
                merged.append(seg)

        # ── Build text output ─────────────────────────────────────────────────
        algo_labels = {
            "FCFS":   "First Come First Serve (FCFS)",
            "SJF-NP": "Shortest Job First — Non-Preemptive",
            "SJF-P":  "Shortest Job First — Preemptive (SRTF)",
            "RR":     f"Round Robin  (Quantum = {quantum})",
        }
        output  = f"{'─'*52}\n"
        output += f"  {algo_labels.get(name, name)}\n"
        output += f"{'─'*52}\n\n"

        col = 11
        header = (f"{'Process':<{col}}{'Arrival':<{col}}"
                  f"{'Burst':<{col}}{'Waiting':<{col}}{'Turnaround':<{col}}\n")
        output += header
        output += "─" * (col * 5) + "\n"
        for p in finished:
            output += (f"{p['id']:<{col}}{p['at']:<{col}}"
                       f"{p['bt']:<{col}}{p['wt']:<{col}}{p['tat']:<{col}}\n")

        avg_w = sum(p['wt'] for p in finished) / len(finished)
        avg_t = sum(p['tat'] for p in finished) / len(finished)
        output += "─" * (col * 5) + "\n"
        output += f"{'Average':<{col}}{'—':<{col}}{'—':<{col}}{avg_w:<{col}.2f}{avg_t:<{col}.2f}\n"
        output += f"\n  Avg Waiting Time   : {avg_w:.2f}\n"
        output += f"  Avg Turnaround Time: {avg_t:.2f}\n"

        # Text Gantt chart (reference alongside visual)
        gantt_str = "\nGantt Chart:\n  "
        for seg in merged:
            pid, s, e = seg
            gantt_str += f"| {pid}({s}→{e}) "
        gantt_str += "|\n"
        output += gantt_str

        return output, merged

    except Exception as e:
        return f"Error in input format: {e}", []
