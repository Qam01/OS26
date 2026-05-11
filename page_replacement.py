def calc(ref, f_size, algo):
    frames = []
    faults = 0
    for i, page in enumerate(ref):
        if page not in frames:
            faults += 1
            if len(frames) < f_size:
                frames.append(page)
            else:
                if algo == "FIFO": frames.pop(0)
                elif algo == "LRU":
                    temp = ref[:i][::-1]
                    lru_val = min(frames, key=lambda x: temp.index(x) if x in temp else -1)
                    frames.remove(lru_val)
                # Optimal simplified
                else: frames.pop(0) 
                frames.append(page)
    return faults

def simulate_all(ref_str, f_str):
    ref = list(map(int, ref_str.split(',')))
    f_size = int(f_str)
    output = f"{'Algorithm':<15}{'Faults':<10}{'Hit Ratio':<10}\n"
    for a in ["FIFO", "LRU", "Optimal"]:
        f = calc(ref, f_size, a)
        hit_r = (len(ref) - f) / len(ref)
        output += f"{a:<15}{f:<10}{hit_r:.2%}\n"
    return output
