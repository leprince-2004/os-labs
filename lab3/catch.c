#include <signal.h>
#include <stdio.h>
#include <unistd.h>

static void on_signal(int sig) {
    if (sig == SIGINT)  write(1, "Nice try! (SIGINT)\n", 19);
    if (sig == SIGTERM) write(1, "Asked politely (SIGTERM), cleaning up...\n", 41);
    if (sig == SIGTERM) _exit(0);
}

int main(void) {
    printf("PID %d: press Ctrl-C, or send me signals from another terminal\n", getpid());
    fflush(stdout);
    signal(SIGINT, on_signal);
    signal(SIGTERM, on_signal);
    if (signal(SIGKILL, on_signal) == SIG_ERR)   /* the kernel refuses this one */
        perror("cannot catch SIGKILL");
    for (;;) pause();                            /* sleep until a signal arrives */
}
