def simulate(algo, blocks_str, procs_str):
    try:
        blocks = list(map(int, blocks_str.split(',')))
        procs = list(map(int, procs_str.split(',')))
        allocation = [-1] * len(procs)
        
        for i in range(len(procs)):
            best_idx = -1
            for j in range(len(blocks)):
                if blocks[j] >= procs[i]:
                    if algo == "First Fit":
                        best_idx = j
                        break
                    elif algo == "Best Fit":
                        if best_idx == -1 or blocks[j] < blocks[best_idx]:
                            best_idx = j
                    elif algo == "Worst Fit":
                        if best_idx == -1 or blocks[j] > blocks[best_idx]:
                            best_idx = j
            
            if best_idx != -1:
                allocation[i] = best_idx
                blocks[best_idx] -= procs[i]

        res = f"{algo} Results:\n{'Process':<15}{'Size':<15}{'Block':<15}\n"
        for i in range(len(procs)):
            b_txt = allocation[i] + 1 if allocation[i] != -1 else "Not Allocated"
            res += f"{i+1:<15}{procs[i]:<15}{b_txt:<15}\n"
        return res
    except:
        return "Invalid input."
