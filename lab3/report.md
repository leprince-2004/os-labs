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

## Lab C: Measure fairness with nice

spin.c counts how many units of work a process gets done each second. I pinned it to CPU 0 with `taskset -c 0` so that the tests compete for the same CPU. The first second of every run is incomplete, so I ignore it and use the average of the other seconds (the script ratio.sh does this).

**Alone:** spin alone on CPU 0 did about 4550 units of work per second (4723, 4488, 4509 and 4480 in seconds 2 to 5).

**Two equal processes on one CPU:** both at nice 0, they did about 2322 and 2287 units per second, so each got about half of the work of the alone run (4550 / 2 = 2275), and the ratio was 1.02. The scheduler shares the CPU fairly between equal processes.

**Unequal processes (nice):**

| Nice values | Work ratio I measured | Predicted (1.25 per step) |
| --- | --- | --- |
| 0 vs 0 | 1.02 | 1 |
| 0 vs 5 | 3.12 | about 3 |
| 0 vs 10 | 9.71 | about 9 to 10 |
| 0 vs 19 | 72.22 | about 70 (CPU-time weights 1024 vs 15) |

The measured ratios are very close to the predictions. The kernel gives each nice value a weight (nice 0 = 1024, nice 5 = 335, nice 10 = 110, nice 19 = 15) and shares the CPU in proportion to the weights. For example 1024 / 110 is about 9.3, and I measured 9.71. At nice 19 the process got only about 64 units per second, against about 4600 for the other one.

**The referee again:** `nice -n -5 ./spin 3` printed "nice: cannot set niceness: Permission denied". The program still ran, but with the normal priority, because nice could not lower the value. With `sudo nice -n -5 ./spin 3` it worked, because root is allowed to do it. A normal user must not be allowed to give a process a better priority: on a shared computer anybody could give their programs the best priority and starve everyone else's. Only root can lower nice values, and normal users can only make their own processes nicer.

**Fair is not equal:** I pinned two spin processes at nice 0 on CPU 0 and watched one of them with watch.sh. The state was R in every line, the voluntary counter stayed at 0, and the involuntary counter grew by about 260 per second (265, 532, 783, ..., 4052 after 14 seconds).
- involuntary stands for the arrow Running -> Ready: the scheduler takes the CPU away from the process when its time slice is over, to give it to the other process. This happens all the time here because two processes want the same CPU.
- voluntary stands for the arrow Running -> Blocked: the process gives up the CPU by itself to wait for something. It never happens here, because spin never waits, it only computes.
The scheduler is fair (each process gets about half of the CPU), but it is not equal in the sense that every process gets the same number of turns without being interrupted: it constantly interrupts both.

## Lab D: Signals

catch.c installs a handler for SIGINT and SIGTERM, and tries to install one for SIGKILL.

**Ctrl-C three times:** each time the program printed "Nice try! (SIGINT)" and did not stop. The handler replaces the default action of SIGINT (end the process), so the process caught the signal and kept running. The perror line printed at the start says "cannot catch SIGKILL: Invalid argument". It means that signal(SIGKILL, ...) returned SIG_ERR: the kernel refuses to let a program install a handler for SIGKILL.

**kill -INT and kill -TERM from another terminal:**
- `kill -INT <pid>` printed "Nice try! (SIGINT)" again, and the program kept running, exactly like Ctrl-C.
- `kill -TERM <pid>` printed "Asked politely (SIGTERM), cleaning up..." and the program ended. `echo $?` showed 0, because the SIGTERM handler calls _exit(0): the program chose its own exit code.

**kill -KILL:** the handler did not run (no message), the shell only printed "Killed". `echo $?` showed 137. The shell computes the exit code of a process killed by a signal as 128 + the signal number: SIGKILL is signal 9, so 128 + 9 = 137 (and Ctrl-C on a program without a handler would give 128 + 2 = 130).

**kill -STOP and kill -CONT:** after `kill -STOP <pid>`, `ps -o pid,stat,comm -p <pid>` showed state T (Stopped), and the shell printed "[1]+ Stopped ./catch". After `kill -CONT <pid>` the state was S again (sleeping in pause(), waiting for a signal), so the process continued. I ended it with `kill -TERM`.

**Why the kernel keeps SIGKILL and SIGSTOP for itself:** if a program could catch or ignore them, a buggy or malicious program could make itself impossible to stop or kill (like deaf.c does with SIGINT and SIGTERM). These two signals are the kernel's guarantee that the administrator and the system can always stop a process or end it, whatever the program does.

**kill -l:** `kill -l SEGV CHLD PIPE` gave 11, 17 and 13.
- SIGSEGV (11) is sent by the kernel to a process that accesses memory it is not allowed to use or that does not exist (a segmentation fault). The default action ends the process and makes a core dump.
- SIGCHLD (17) is sent to a parent when one of its children ends (or stops). It is ignored by default. A parent can catch it to call wait and collect its children, so that they do not stay zombies.
- SIGPIPE (13) is sent to a process that writes into a pipe or a socket that nobody reads any more. The default action ends the process. For example in `yes | head -1`, yes receives SIGPIPE when head ends.

**write and not printf in the handler:** printf is not async-signal-safe (see man 7 signal-safety). It uses internal buffers and locks. If a signal arrives while the main program is in the middle of a printf, and the handler also calls printf, the second call can wait forever for the lock held by the first one (deadlock) or corrupt the buffer. write is a simple system call, and it is on the list of functions that are safe inside a signal handler.

**Debrief:** when Windows shows "Not responding", the CPU is not frozen. The program stopped answering the messages the system sends to it, usually because it is busy or blocked. The OS then offers "End task", which is the equivalent of SIGKILL.
