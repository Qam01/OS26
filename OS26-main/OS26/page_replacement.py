def _calc(ref, f_size, algo):
    """Simulate one page replacement algorithm; returns fault count."""
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
                    frames.append(page)

                elif algo == "LRU":
                    # Find the frame whose last use was earliest
                    lru_page = None
                    lru_time = float('inf')
                    for f in frames:
                        last_use = -1
                        for t in range(i - 1, -1, -1):
                            if ref[t] == f:
                                last_use = t
                                break
                        if last_use < lru_time:
                            lru_time = last_use
                            lru_page = f
                    frames.remove(lru_page)
                    frames.append(page)

                elif algo == "Optimal":
                    future = ref[i + 1:]
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
    """
    Run FIFO, LRU, and Optimal for the given reference string and frame size.
    Returns a formatted table with faults, hits, hit ratio, and miss ratio.
    """
    try:
        ref = list(map(int, ref_str.replace(' ', '').split(',')))
        f_size = int(f_str)
        if f_size <= 0:
            raise ValueError("Frame size must be positive.")
        if not ref:
            raise ValueError("Reference string is empty.")

        total = len(ref)

        col1, col2 = 12, 13
        output  = f"{'─'*62}\n"
        output += f"  Page Replacement Results  "
        output += f"(Frames: {f_size}  |  References: {total})\n"
        output += f"{'─'*62}\n"
        output += (f"{'Algorithm':<{col1}}{'Page Faults':<{col2}}"
                   f"{'Page Hits':<{col2}}{'Hit Ratio':<{col2}}{'Miss Ratio':<{col2}}\n")
        output += "─" * 62 + "\n"

        for algo in ["FIFO", "LRU", "Optimal"]:
            faults = _calc(ref, f_size, algo)
            hits   = total - faults
            hit_r  = hits   / total
            miss_r = faults / total
            output += (f"{algo:<{col1}}{faults:<{col2}}{hits:<{col2}}"
                       f"{hit_r:<{col2}.2%}{miss_r:<{col2}.2%}\n")

        output += "─" * 62 + "\n"
        output += f"\n  Reference String : {', '.join(map(str, ref))}\n"
        return output

    except Exception as e:
        return f"Invalid input: {e}"
