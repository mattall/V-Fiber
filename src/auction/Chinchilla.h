#ifndef __LazyCat__Chinchilla__
#define __LazyCat__Chinchilla__

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <pthread.h>

#define CMDSIZE 50

char Manual[] = "\
These commands are defined internally.  Type `/help' to see this manual.\n\
\n\
NAME\n\
Chinchilla - Client tool for the LazyCat online auction system.\n\
\n\
DESCRIPTION\n\
This is a client tool for auction managers.\n\
\n\
Using this tool is very easy. Invoke it from the prompt of your command interpreter as follows:\n\
\n\
shell> ./Chinchilla\n\
\n\
Read the document for more information about this kitten and services it provides.\n\
\n\
COMMANDS\n\
Note that all text commands must be first on line and end with \'\\n\'\n\
/?  			Another way to invoke `help'.\n\
/clear  		Clear screen.\n\
/refresh		Refresh for the latest auction state.\n\
/bid 			Bid a price.\n\
/leave          Leave.\n\
";

int client_sockfd;
int len;
struct sockaddr_in client_addr;
struct sockaddr_in server_addr;
int sin_size = sizeof(struct sockaddr_in);
char buf[BUFSIZ];
char serverIP[20] = "127.0.0.1";
char testStr[]= "aaa";  

#endif /* defined(__LazyCat__Chinchilla__) */
