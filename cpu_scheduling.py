def run_algorithm(name, data, quantum):
    try:
        procs = []
        for i, p in enumerate(data.split(';')):
            at, bt = map(int, p.split(','))
            procs.append({'id': f"P{i+1}", 'at': at, 'bt': bt, 'rem': bt, 'wt': 0, 'tat': 0})
        
        gantt = "|"
        time = 0
        finished = []
        
        if name == "FCFS":
            procs.sort(key=lambda x: x['at'])
            for p in procs:
                if time < p['at']: time = p['at']
                p['wt'] = time - p['at']
                time += p['bt']
                p['tat'] = p['wt'] + p['bt']
                gantt += f" {p['id']} |"
            finished = procs

        elif name == "SJF-NP":
            while len(finished) < len(procs):
                available = [p for p in procs if p['at'] <= time and p not in finished]
                if not available:
                    time += 1
                    continue
                curr = min(available, key=lambda x: x['bt'])
                curr['wt'] = time - curr['at']
                time += curr['bt']
                curr['tat'] = curr['wt'] + curr['bt']
                gantt += f" {curr['id']} |"
                finished.append(curr)

        # (Logic for SJF-P and RR can be added here similarly)
        
        output = f"{'Process':<10}{'Arrival':<10}{'Burst':<10}{'Waiting':<10}{'Turnaround':<10}\n"
        output += "-"*50 + "\n"
        for p in finished:
            output += f"{p['id']:<10}{p['at']:<10}{p['bt']:<10}{p['wt']:<10}{p['tat']:<10}\n"
        
        avg_w = sum(p['wt'] for p in finished) / len(procs)
        avg_t = sum(p['tat'] for p in finished) / len(procs)
        output += f"\nAvg Waiting: {avg_w:.2f} | Avg Turnaround: {avg_t:.2f}\n"
        output += f"\nGantt Chart:\n{gantt}"
        return output
    except:
        return "Error in input format."
