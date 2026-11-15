# OS Session 3 Lab Report

## Lab A: Schedulers on paper, then by program

Three jobs arrive at time 0: A needs 100 units, B needs 10, C needs 10.
Turnaround = finish time - arrival time. Response = first run time - arrival time.

### Timelines

    FIFO (order A, B, C)
    t=0                                         100       110       120
    |                    A                       |    B    |    C    |

    SJF (order B, C, A)
    t=0       10        20                                          120
    |    B    |    C    |                    A                       |

    RR, slice 10
    t=0       10        20        30                                120
    |    A    |    B    |    C    |   A runs alone, 9 slices of 10   |

    RR, slice 1
    t=0 1 2 3 4 5 ...  A B C A B C A B C ... (B ends at 29, C ends at 30)
    then A runs alone from t=30 to t=120

### Results (checked with sched.py)

| Policy | Job | Response | Turnaround |
| --- | --- | --- | --- |
| FIFO | A | 0 | 100 |
| FIFO | B | 100 | 110 |
| FIFO | C | 110 | 120 |
| FIFO | average | 70.00 | 110.00 |
| SJF | A | 20 | 120 |
| SJF | B | 0 | 10 |
| SJF | C | 10 | 20 |
| SJF | average | 10.00 | 50.00 |
| RR 10 | A | 0 | 120 |
| RR 10 | B | 10 | 20 |
| RR 10 | C | 20 | 30 |
| RR 10 | average | 10.00 | 56.67 |
| RR 1 | A | 0 | 120 |
| RR 1 | B | 1 | 29 |
| RR 1 | C | 2 | 30 |
| RR 1 | average | 1.00 | 59.67 |

### Questions

**Best policies:** SJF gives the best average turnaround (50.00). Round Robin with slice 1 gives the best average response (1.00). FIFO is the worst for both, because A runs first and B and C wait 100 units behind it (the convoy effect).

**RR slice 10 versus slice 1:** with slice 1 the average response improves from 10.00 to 1.00, because every job gets the CPU almost at once. The average turnaround gets worse, from 56.67 to 59.67 (for example B ends at 29 instead of 20), because every job is stretched out. Slice 1 also needs about 120 slices instead of 12. A real CPU pays for every switch: it saves and restores the registers, runs the scheduler code, and loses the warmed-up CPU caches, so a switch costs a few microseconds of work that is not useful for any job.

**Same result for FIFO and SJF:** for the lengths 10,20,30, both give an average response of 13.33 and an average turnaround of 33.33. This happens when the jobs arrive already sorted from the shortest to the longest, so the FIFO order is the same as the SJF order.

**Round Robin in sched.py:** a job whose slice ran out and still has work left (`j["left"] > 0`) is put back at the end of the queue with `queue.append(j)`.
