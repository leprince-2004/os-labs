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
With dstate.c, the parent is in state D (wchan: 77465   64861 D    kernel_clone         dstate) because it waits for the vfork child to finish. The child is in state S (wchan:77466   77465 S    hrtimer_nanosleep    dstate) because it is in sleep(20). When I used kill -9 on the D process:  died immediately.

### Idle (I)
In my Codespace, ps showed no I processes because it runs in a container and kernel threads are not visible. On a normal Linux machine they appear as kernel threads (names in square brackets in ps aux). The kernel needs its own threads to do background work that does not belong to any user program, such as writing cached data to disk, freeing memory and handling deferred device work. When they have nothing to do they sleep in state I.

## Lab C: Ready is not Running

**Number of CPUs:** nproc gave N = 2. I started N + 2 = 4 CPU hogs with `yes > /dev/null &`.

**vmstat r column:** before the hogs, r was about. After starting the hogs, r went up to about 30s.

**Running vs Ready:** r counts the processes that are Running plus the ones that are Ready (both show R in Linux). At any instant, at most N processes are Running, one per CPU. The remaining ones (about 2) are Ready: they could run, but they are waiting for a CPU. That is why r is bigger than the number of CPUs.

**Pinning two hogs to the same CPU:** I used `taskset -cp 0` on two hogs. With watch.sh, the involuntary counter grew fast and the voluntary counter stayed almost flat. A hog never waits for anything, so it never gives up the CPU voluntarily. The scheduler takes the CPU away at the end of each time slice so the other hog can run. This counts the arrow Running -> Ready (timeout / preemption).

**Load average:** `cat /proc/loadavg` gave 5.82 4.91 2.81. The load average is the average number of runnable (and D) processes over 1, 5 and 15 minutes. If it is above N, there are more processes wanting the CPU than there are CPUs, so some are always waiting in the Ready queue. The machine is overloaded.

**Debrief:** when a laptop freezes because one app goes crazy, the run queue (Ready) is full and every other process has to wait its turn for the CPU.

## Lab D: Birth and death

### Birth: fork + exec + wait
**State of the parent while the child runs ls:** the parent is in state S (Blocked), waiting in waitpid until the child ends. I checked it with a test copy where the child runs sleep 15: ps showed the parent in S with wchan do_wait.

**Wrong file:** when I replaced "-l" by "/nothing", the parent printed "child exited with 1". Running `ls /nothing; echo $?` gave 2. They are the same, because the parent collects the exit status of the child (ls) with waitpid.

**strace:** clone is the system call behind fork. The several execve lines ending in -1 ENOENT show execlp searching for ls in each directory of the PATH, one after the other, until it finds it (for example in /usr/bin). A failed execve returns -1 and the search continues.

### Death: a zombie
In `ps -l`, the child of zombie shows Z in the S column and `<defunct>` at the end. Defunct means that the process is dead but still has an entry in the process table, because its parent has not collected its exit status. In the five-state model it is the Exit (Terminated) state.

`kill -9` does not remove it, because it is already dead: nothing can be killed twice. Only the parent's wait, or the parent's own exit (then init adopts and collects the zombie), removes it. A screenshot is in zombie_ps.png.

### Death: an orphan
After the parent left, the parent PID of the child changed to 91205. With `cat /proc/<that number>/comm` I found that the process docker-init adopted the orphan. In a normal Linux this is PID 1 (init/systemd) or a subreaper, which collects the child when it ends.

**Why it matters:** a server that forgets to call wait fills the process table with zombies until no new process can start ("cannot fork" or "resource temporarily unavailable").
