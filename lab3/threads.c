#define _GNU_SOURCE
#include <pthread.h>
#include <stdio.h>
#include <unistd.h>

/* One busy thread and two sleepy threads, to practise "top -H". */
static void *busy(void *arg) {
    pthread_setname_np(pthread_self(), "busy");
    volatile unsigned long x = 0;
    for (;;) x++;                       /* burns CPU forever */
    return arg;
}

static void *sleepy(void *arg) {
    pthread_setname_np(pthread_self(), (const char *)arg);
    for (;;) sleep(1);                  /* almost always blocked */
    return NULL;
}

int main(void) {
    pthread_t t1, t2, t3;
    printf("PID %d: 1 busy thread + 2 sleepy threads (Ctrl-C to stop)\n", getpid());
    fflush(stdout);
    pthread_create(&t1, NULL, busy, NULL);
    pthread_create(&t2, NULL, sleepy, "sleepy1");
    pthread_create(&t3, NULL, sleepy, "sleepy2");
    pthread_join(t1, NULL);
    return 0;
}
