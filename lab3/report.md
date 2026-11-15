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

## Lab B: Overload your CPU

**Number of CPUs:** nproc gave N = 2. I started N + 1 = 3 CPU hogs with `yes > /dev/null &`. A screenshot of htop with the hogs running is in htop.png.

**htop:** the three yes processes got about 69.3%, 66.0% and 55.4% of a CPU, a total of about 190.7%. The total is about N x 100% (200%) and not more, because the machine has only 2 CPUs and a CPU cannot give more than 100%. The 3 hogs share the 2 x 100% between them, and htop and other small processes use the rest.

**vmstat 1 5:** the first line is an average since boot, so I ignore it. The next lines showed r = 6, 8, 3 and 5. The r column counts the processes that want the CPU (Running + Ready). Only N = 2 can be Running at the same time, so r - 2 processes are Ready but not Running: between 1 and 6, about 3 or 4 on average. The minimum expected value was N + 1 - N = 1, and r was higher because other processes of the Codespace also wanted the CPU. The CPU columns showed us 25%, sy 75% and id 0%, so the CPUs were fully busy (the hogs spend most of their time in system calls, writing to /dev/null).

**time ls -R /usr > /dev/null:**

| Situation | real | user | sys |
| --- | --- | --- | --- |
| with the hogs | 0.104 s | 0.013 s | 0.024 s |
| without the hogs (after pkill yes) | 0.029 s | 0.013 s | 0.014 s |

The real time is about 3.6 times larger with the hogs, while user is the same. user is the CPU time that ls really used, and it did the same work. real is the elapsed time on the clock, and it also includes the time ls spent in the Ready queue waiting for a CPU behind the hogs.

**Ctrl-Z, jobs, bg:** I started `yes > /dev/null` in the foreground and checked it with `ps -o pid,stat,comm`:
- running in the foreground: state R+ (the + means it belongs to the foreground process group of the terminal);
- after Ctrl-Z: state T (Stopped), and `jobs` showed it as Stopped. Ctrl-Z sends SIGTSTP;
- after `bg`: state R (running again, but in the background, so no +). bg sends SIGCONT.
After `fg` it runs in the foreground again. I cleaned up with `pkill yes`.
