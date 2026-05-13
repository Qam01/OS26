from collections import deque


def run_algorithm(name, data, quantum):
    try:
        procs = []
        for i, p in enumerate(data.replace(' ', '').split(';')):
            at, bt = map(int, p.split(','))
            procs.append({'id': f"P{i+1}", 'at': at, 'bt': bt, 'rem': bt, 'wt': 0, 'tat': 0})

        gantt = []
        time = 0
        finished = []

        if name == "FCFS":
            procs.sort(key=lambda x: x['at'])
            for p in procs:
                if time < p['at']:
                    time = p['at']
                p['wt'] = time - p['at']
                gantt.append((p['id'], time, time + p['bt']))
                time += p['bt']
                p['tat'] = p['wt'] + p['bt']
            finished = procs

        elif name == "SJF-NP":
            remaining = list(procs)
            while remaining:
                available = [p for p in remaining if p['at'] <= time]
                if not available:
                    time = min(p['at'] for p in remaining)
                    continue
                curr = min(available, key=lambda x: x['bt'])
                curr['wt'] = time - curr['at']
                gantt.append((curr['id'], time, time + curr['bt']))
                time += curr['bt']
                curr['tat'] = curr['wt'] + curr['bt']
                finished.append(curr)
                remaining.remove(curr)

        elif name == "SJF-P":
            # Preemptive Shortest Job First (SRTF)
            remaining = [dict(p) for p in procs]
            n = len(remaining)
            done = 0
            prev = None
            seg_start = 0

            while done < n:
                available = [p for p in remaining if p['at'] <= time and p['rem'] > 0]
                if not available:
                    time += 1
                    continue
                curr = min(available, key=lambda x: x['rem'])

                if prev != curr['id']:
                    if prev is not None:
                        gantt.append((prev, seg_start, time))
                    seg_start = time
                    prev = curr['id']

                curr['rem'] -= 1
                time += 1

                if curr['rem'] == 0:
                    gantt.append((curr['id'], seg_start, time))
                    prev = None
                    curr['tat'] = time - curr['at']
                    curr['wt'] = curr['tat'] - curr['bt']
                    done += 1

            id_map = {p['id']: p for p in remaining}
            for p in procs:
                p['wt'] = id_map[p['id']]['wt']
                p['tat'] = id_map[p['id']]['tat']
            finished = procs

        elif name == "RR":
            try:
                q = int(quantum)
            except (ValueError, TypeError):
                return "Error: Invalid quantum value."

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
                    time = remaining[idx]['at']
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

        output = f"{'Process':<10}{'Arrival':<10}{'Burst':<10}{'Waiting':<10}{'Turnaround':<10}\n"
        output += "-" * 50 + "\n"
        for p in finished:
            output += f"{p['id']:<10}{p['at']:<10}{p['bt']:<10}{p['wt']:<10}{p['tat']:<10}\n"

        avg_w = sum(p['wt'] for p in finished) / len(finished)
        avg_t = sum(p['tat'] for p in finished) / len(finished)
        output += f"\nAvg Waiting: {avg_w:.2f} | Avg Turnaround: {avg_t:.2f}\n"

        merged = []
        for seg in gantt:
            if merged and merged[-1][0] == seg[0] and merged[-1][2] == seg[1]:
                merged[-1] = [merged[-1][0], merged[-1][1], seg[2]]
            else:
                merged.append(list(seg))

        gantt_str = "|"
        for seg in merged:
            gantt_str += f" {seg[0]}({seg[1]}-{seg[2]}) |"
        output += f"\nGantt Chart:\n{gantt_str}"
        return output

    except Exception as e:
        return f"Error in input format: {e}"
