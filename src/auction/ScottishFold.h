#ifndef __LazyCat__ScottishFold__
#define __LazyCat__ScottishFold__

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <pthread.h>

#define CMDSIZE 50
#define COUNTMAX 300

char Manual[] = "\
These commands are defined internally.  Type `/help' to see this manual.\n\
\n\
NAME\n\
ScottishFold - Server tool for the LazyCat online auction system.\n\
\n\
DESCRIPTION\n\
This is a server tool for auction managers.\n\
\n\
Using this tool is very easy. Invoke it from the prompt of your command interpreter as follows:\n\
\n\
shell> ./ScottishFold\n\
\n\
Read the document for more information about this kitten and services it provides.\n\
\n\
COMMANDS\n\
Note that all text commands must be first on line and end with \'\\n\'\n\
/?  			Another way to invoke `help'.\n\
/clear  		Clear screen.\n\
/msg 			Send messages to single or multiple users (default null).\n\
/list 			List current bidders.\n\
/kickout    	Kick out single or multiple users (default null).\n\
/openauction 	Begin a new auction and notify all online users current situation.\n\
/closeauction 	Close current auction and notify all online users with the result.\n\
/exit           Quit.\n\
";
int server_sockfd, client_sockfd;
int len;
int winnerID;   
int clientN = 0;
int priceHistory[COUNTMAX]; 
struct sockaddr_in server_addr; 
struct sockaddr_in client_addr; 
struct sockaddr_in onboard_addr[100]; 
int sin_size = sizeof(struct sockaddr_in);
char buf[BUFSIZ];  
int currentAuction = 0; 
int auctionCount = 0;  
int currentPrice;   
char * bidderHoldingHighestPrice = NULL; 

#endif /* defined(__LazyCat__ScottishFold__) */
