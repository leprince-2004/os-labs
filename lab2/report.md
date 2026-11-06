# OS Session 2 Lab Report

## Lab A: Meet the family

I ran this lab in a GitHub Codespace (a Linux container), not on a physical laptop.

**Shell PID and parent PID:** my shell (bash) has PID 3313 and its parent has PID 2220.

**Process tree of my shell:**

    bash(3313)---pstree(6831)

My bash process has one child, the pstree command I just ran.

**PID 1:** it is called docker-init. Because Codespaces runs inside a Docker container, PID 1 is docker-init instead of systemd. Under it I can see containerd, dockerd, sh and sshd.

**State counts (whole system):**
- R: 1
- S: 25
- I: 0
- Other letters: 0

In the first 30 lines of `ps -eo pid,stat,comm`, 24 processes were visible: 1 was R (the ps command itself) and 23 were S (sleeping).

The most common state is S (interruptible sleep), because most processes are waiting for an event such as a key press, a timer or network data. They are Blocked, not using the CPU.

**Fraction Running:** 1 out of 26 processes, about 3.8%. The only running process was ps itself, which was running while it took the snapshot.

**What this tells me:** processes spend almost all of their life waiting (Blocked), not running. Only a few processes use the CPU at any given instant, which is why a few CPUs can serve hundreds of processes. My Codespace has only 26 processes because it is a small container, while a normal laptop has hundreds.

## Lab B: Catch every state

I ran states.c and watched it with watch.sh from a second terminal (output saved in lab_b_watch.txt).

| Phase | What the code does | Linux state | Textbook state | Which counter went up? |
| --- | --- | --- | --- | --- |
| 1 | sleep(5) | S | Blocked | voluntary |
| 2 | burn(8) | R | Running (Ready when preempted) | involuntary |
| 3 | sleep(8) | S | Blocked | voluntary |
| 4 | fgets waiting for me | S | Blocked | voluntary |
| 5 | burn(5) | R | Running | involuntary |
| after | program ended | gone | Exit | none |

**Counters:** voluntary goes up when the process gives up the CPU itself to wait (Running -> Blocked). involuntary goes up when the scheduler takes the CPU away at the end of the time slice (Running -> Ready).

### Stopped (T)
With Ctrl-Z in phase 2, watch.sh showed state T and the involuntary counter stopped growing, because a stopped process is not on the CPU. After fg the state went back to R and the program continued. With kill -STOP and kill -CONT from another terminal I saw the same: T, then back to R.

### Uninterruptible sleep (D)
With dstate.c, the parent is in state D (wchan: <WRITE the wchan of the D process>) because it waits for the vfork child to finish. The child is in state S (wchan: <WRITE the wchan of the S process>) because it is in sleep(20). When I used kill -9 on the D process: <WRITE what you saw: died immediately, or died after about 20 seconds>.

### Idle (I)
In my Codespace, ps showed no I processes because it runs in a container and kernel threads are not visible. On a normal Linux machine they appear as kernel threads (names in square brackets in ps aux). The kernel needs its own threads to do background work that does not belong to any user program, such as writing cached data to disk, freeing memory and handling deferred device work. When they have nothing to do they sleep in state I.
