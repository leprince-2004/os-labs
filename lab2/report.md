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
