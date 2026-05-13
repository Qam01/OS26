def calc(ref, f_size, algo):
    frames = []
    faults = 0

    for i, page in enumerate(ref):
        if page not in frames:
            faults += 1
            if len(frames) < f_size:
                frames.append(page)
            else:
                if algo == "FIFO":
                    frames.pop(0)

                elif algo == "LRU":
                    # Find which frame was used least recently
                    lru_page = None
                    lru_time = float('inf')
                    for f in frames:
                        # Search backwards in ref[:i] for last use
                        last_use = -1
                        for t in range(i - 1, -1, -1):
                            if ref[t] == f:
                                last_use = t
                                break
                        if last_use < lru_time:
                            lru_time = last_use
                            lru_page = f
                    frames.remove(lru_page)

                elif algo == "Optimal":
                    future = ref[i + 1:]
                    # Replace the page that won't be used for the longest time
                    farthest = -1
                    victim = frames[0]
                    for f in frames:
                        if f not in future:
                            victim = f
                            break
                        next_use = future.index(f)
                        if next_use > farthest:
                            farthest = next_use
                            victim = f
                    frames.remove(victim)

                frames.append(page)
    return faults


def simulate_all(ref_str, f_str):
    try:
        ref = list(map(int, ref_str.replace(' ', '').split(',')))
        f_size = int(f_str)
        total = len(ref)

        output = f"{'Algorithm':<15}{'Page Faults':<15}{'Page Hits':<15}{'Hit Ratio':<12}\n"
        output += "-" * 57 + "\n"
        for a in ["FIFO", "LRU", "Optimal"]:
            faults = calc(ref, f_size, a)
            hits = total - faults
            hit_r = hits / total
            output += f"{a:<15}{faults:<15}{hits:<15}{hit_r:.2%}\n"
        return output
    except Exception as e:
        return f"Invalid input: {e}"
