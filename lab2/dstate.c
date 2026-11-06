#include <unistd.h>

int main(void) {
    pid_t pid = vfork();
    if (pid == 0) {
        sleep(20);      /* for this demo only */
        _exit(0);
    }
    return 0;
}
