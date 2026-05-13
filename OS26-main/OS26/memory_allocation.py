def simulate(algo, blocks_str, procs_str):
    """
    Simulate one contiguous memory allocation algorithm.
    algo: "First Fit" | "Best Fit" | "Worst Fit"
    Returns a formatted result string.
    """
    try:
        blocks     = list(map(int, blocks_str.replace(' ', '').split(',')))
        procs      = list(map(int, procs_str.replace(' ', '').split(',')))
        allocation = [-1]   * len(procs)
        frag_list  = [None] * len(procs)   # fragmentation captured at alloc time
        block_copy = blocks[:]

        for i in range(len(procs)):
            best_idx = -1
            for j in range(len(block_copy)):
                if block_copy[j] >= procs[i]:
                    if algo == "First Fit":
                        best_idx = j
                        break
                    elif algo == "Best Fit":
                        if best_idx == -1 or block_copy[j] < block_copy[best_idx]:
                            best_idx = j
                    elif algo == "Worst Fit":
                        if best_idx == -1 or block_copy[j] > block_copy[best_idx]:
                            best_idx = j

            if best_idx != -1:
                allocation[i]  = best_idx
                block_copy[best_idx] -= procs[i]
                # Fragmentation = space remaining in that block right after this alloc
                frag_list[i]   = block_copy[best_idx]

        col = 15
        res  = f"  {algo}\n"
        res += "─" * (col * 4) + "\n"
        res += (f"{'Process':<{col}}{'Size (KB)':<{col}}"
                f"{'Block No.':<{col}}{'Fragmentation':<{col}}\n")
        res += "─" * (col * 4) + "\n"

        for i in range(len(procs)):
            if allocation[i] != -1:
                b_no = str(allocation[i] + 1)
                frag = str(frag_list[i])
            else:
                b_no = "Not Allocated"
                frag = "—"
            res += (f"{'P' + str(i+1):<{col}}{procs[i]:<{col}}"
                    f"{b_no:<{col}}{frag:<{col}}\n")

        res += "─" * (col * 4) + "\n"
        allocated = sum(1 for a in allocation if a != -1)
        res += f"  Allocated : {allocated} / {len(procs)} processes\n"
        res += f"  Remaining block sizes: {block_copy}\n"
        return res

    except Exception as e:
        return f"Invalid input: {e}\n"


def simulate_all(blocks_str, procs_str):
    """Run all three allocation strategies and return combined output."""
    try:
        blocks = list(map(int, blocks_str.replace(' ', '').split(',')))
        procs  = list(map(int, procs_str.replace(' ', '').split(',')))
    except Exception as e:
        return f"Invalid input: {e}"

    output  = "═" * 62 + "\n"
    output += "  Contiguous Memory Allocation — All Strategies\n"
    output += f"  Blocks (KB) : {blocks}\n"
    output += f"  Processes   : {procs}\n"
    output += "═" * 62 + "\n\n"

    for algo in ["First Fit", "Best Fit", "Worst Fit"]:
        output += simulate(algo, blocks_str, procs_str)
        output += "\n"

    return output
