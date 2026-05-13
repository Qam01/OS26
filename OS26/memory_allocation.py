def simulate(algo, blocks_str, procs_str):
    try:
        blocks = list(map(int, blocks_str.replace(' ', '').split(',')))
        procs = list(map(int, procs_str.replace(' ', '').split(',')))
        allocation = [-1] * len(procs)
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
                allocation[i] = best_idx
                block_copy[best_idx] -= procs[i]

        res = f"{algo} Results:\n{'Process':<15}{'Size':<15}{'Block':<15}{'Fragmentation':<15}\n"
        res += "-" * 60 + "\n"
        for i in range(len(procs)):
            if allocation[i] != -1:
                b_txt = str(allocation[i] + 1)
                frag = block_copy[allocation[i]]
                frag_txt = str(frag)
            else:
                b_txt = "Not Allocated"
                frag_txt = "-"
            res += f"{i+1:<15}{procs[i]:<15}{b_txt:<15}{frag_txt:<15}\n"

        allocated = sum(1 for a in allocation if a != -1)
        res += f"\nAllocated: {allocated}/{len(procs)} processes\n"
        return res
    except Exception as e:
        return f"Invalid input: {e}"
