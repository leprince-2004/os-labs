# Rapport Lab 1 - Operating Systems Session 1

## Définition d'un système d'exploitation

Avant le cours : Un système d'exploitation est un logiciel qui permet à l'ordinateur de fonctionner et de lancer des programmes, comme Windows ou Linux.

Après le cours : Un système d'exploitation est le logiciel qui partage le matériel d'une machine (CPU, mémoire, disques) entre plusieurs programmes, de façon sûre et simple. Son coeur, le kernel, joue trois rôles : arbitre (il protège les programmes les uns des autres), illusionniste (chaque programme croit avoir le CPU et la mémoire pour lui seul) et colle (une même interface pour tout le matériel). Un programme en user mode ne peut accéder au matériel que par un system call, comme write, que le kernel vérifie avant d'agir.

## Lab B - Interroger la machine

| Commande | Réponse |
| --- | --- |
| uname -a | Kernel 6.8.0-1064-azure, architecture x86_64 |
| lscpu | 2 CPU vus par Linux, modèle Intel(R) Xeon(R) Platinum 8370C @ 2.80GHz |
| nproc | 2, ce qui correspond à lscpu |
| free -h | 5.8 Gi de RAM "available". "available" est plus grand que "free" (368 Mi) car le kernel utilise la RAM libre comme cache de fichiers (buff/cache, 5.8 Gi), et il peut rendre ce cache tout de suite si un programme a besoin de mémoire |
| df -h | Le système de fichiers monté sur / est "overlay" (32 Go au total), il reste 19 Go libres |
| ps aux \| head | Le programme de PID 1 est /sbin/docker-init (on est dans un conteneur) |
| ps aux \| wc -l | 27 lignes, donc 26 processus plus la ligne d'en-tête. C'est beaucoup plus que les 2 CPU de nproc |
| htop | Le processus en tête du tri par CPU est dockerd (PID 439), à 0.0 % de CPU : la machine est presque inactive, tous les processus sont à 0.0 %. |

Discussion : il y a beaucoup plus de processus que de CPU, et ils avancent tous quand même. Le kernel donne le CPU à chaque processus pendant un très court instant, puis passe au suivant, et recommence plusieurs fois par seconde. Chaque programme a l'impression d'avoir le CPU pour lui seul : c'est le rôle d'illusionniste du kernel.


## Lab C - Chaque processus est un dossier

Mon shell : PID 2958 (echo $$).

| Champ | Valeur pour mon shell |
| --- | --- |
| Name | bash |
| State | S (sleeping) |
| Pid / PPid | 2958 / 2157 |
| Uid | 1000 |
| VmRSS | 9532 kB |
| Threads | 1 |
| voluntary_ctxt_switches | 288 |

- readlink /proc/$$/exe : /usr/bin/bash
- ls -l /proc/$$/fd : les descripteurs 0, 1 et 2 pointent vers /dev/pts/1, mon terminal (il y a aussi le 255).
- Processus sleep : State = S (sleeping), PPid = 2958, le PID de mon shell. Après kill, le dossier /proc/10296 a disparu (No such file or directory).
- /proc/meminfo a une taille de 0 mais on peut le lire : ce fichier n'est pas sur le disque, le kernel génère son contenu au moment où on le lit.

Conclusion : ps, top et htop sont des programmes qui lisent /proc et affichent le résultat.

## Lab D - Observer le kernel au travail

Programme hello.c compilé avec gcc -Wall -g. La trace strace montre que printf devient l'appel système write(1, "Hello, OS!\n", 11) = 11 : écriture de 11 octets sur le descripteur 1 (le terminal).

Expérience 1 : strace-hello.txt contient 36 lignes (35 appels système plus la ligne finale "+++ exited with 0 +++").

Expérience 2 : avec strace -c, l'appel le plus fréquent est mmap (8 appels).

Expérience 3 : avec trois printf, strace -e trace=write ./hello3 montre 3 appels write (8 octets chacun) quand la sortie va au terminal. Avec > out.txt, il n'y a plus qu'un seul write de 24 octets.

Hypothèse : quand la sortie va vers un terminal, la bibliothèque C envoie le texte à chaque retour à la ligne, donc un write par ligne. Quand elle va vers un fichier, elle garde le texte en mémoire et l'envoie en une seule fois à la fin du programme, pour appeler le kernel moins souvent.

Expérience 4 : ltrace ./hello affiche puts("Hello, OS!") au lieu de printf : le compilateur a remplacé printf par la fonction plus simple puts, car il n'y a rien à formater. ltrace montre les appels à la bibliothèque C, strace montre les appels au kernel.

Expérience 5 : strace -c ls fait 147 appels système, contre 34 pour mon programme hello, soit 113 de plus. ls doit ouvrir et lire des dossiers (openat, getdents64), ce que hello ne fait pas.

## Le referee dit non

Commande : cat /etc/shadow, qui affiche "Permission denied". Avec strace -e trace=openat cat /etc/shadow, la ligne importante est :

openat(AT_FDCWD, "/etc/shadow", O_RDONLY) = -1 EACCES (Permission denied)

cat a demandé au kernel d'ouvrir le fichier des mots de passe chiffrés. Le kernel a vérifié mon Uid (1000, comme vu au Lab C), a vu que je n'ai pas le droit de lire ce fichier, et a refusé avec l'erreur EACCES. C'est le kernel qui a décidé, pas le programme cat : c'est la protection du système d'exploitation en action.
