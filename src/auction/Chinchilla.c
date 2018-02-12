#include "Chinchilla.h"

void makeBuf (int type, char content[])
{
    memset(buf, '\0', sizeof(buf));
    sprintf(buf, "%d%s", type, content);
}

void startClient()
{
    printf("Client starting ... ...\n");
    printf("Server IP: %s\n", serverIP);
    printf("Setting up client ...");
    memset(& server_addr, 0, sizeof(server_addr)); 
    server_addr.sin_family = AF_INET;  
    server_addr.sin_addr.s_addr = inet_addr(serverIP); 
    server_addr.sin_port = htons(8000); 
    
    if((client_sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) < 0)
    {
        perror("Error: Can not create socket.");
        exit(EXIT_FAILURE);
    }
    printf(" ... ... [Done]\n");
}

void exitChinchilla()
{
    exit(0);
}

void * listening (void * args)
{
    while (1)
    {
        memset(buf, 0, sizeof(buf));
        if((len = recvfrom(client_sockfd, buf, BUFSIZ, 0, (struct sockaddr *) & server_addr, &sin_size)) < 0)
        {
            perror("recvfrom");
        }
        if (strcmp(buf, "Uoyj9gJcuDBfEpcFKq9htFGW") == 0)
        {
            printf("\nleaving..."); 
            exit(0);
        }
        if (strcmp(buf, "PaVk49AavrrxmuMxxADUjcr") ==0)
        {
            printf("\nServer down. Force quit."); 
            exit(0);
        }
        printf("\n------------------------\n%s", buf);
    }
    return NULL;
}

void clientLoggin()
{
    char userName[20];
    printf("Enter your name\n(Note: Other bidders won't see this):");
    scanf("%s", userName);
    makeBuf (0, userName);  
    printf("Loggin as %s ...", userName);
    if(sendto(client_sockfd, buf, BUFSIZ, 0, (struct sockaddr *) & server_addr, sizeof(struct sockaddr)) < 0)
    {
        perror("Loggin failed");
        close(client_sockfd);
        exit(EXIT_FAILURE);
    }
    memset(buf, 0, sizeof(buf));
    if((len = recvfrom(client_sockfd, buf, BUFSIZ, 0, (struct sockaddr *) & server_addr, &sin_size)) < 0)
    {
        perror("recvfrom");
    }
    puts(buf);  
    getchar();
}

void clientRefresh()
{
    printf("Requesting latest auction state...\n");
    makeBuf(1, NULL);   
    if(sendto(client_sockfd, buf, BUFSIZ, 0, (struct sockaddr *) & server_addr, sizeof(struct sockaddr)) < 0)
    {
        perror("Refresh failed");
        close(client_sockfd);
        exit(EXIT_FAILURE);
    }
}

void clientBid()
{
    printf("Trying to bid...\n");
    makeBuf(2, NULL);   
    if(sendto(client_sockfd, buf, BUFSIZ, 0, (struct sockaddr *) & server_addr, sizeof(struct sockaddr)) < 0)
    {
        perror("Bidding failed");
        close(client_sockfd);
        exit(EXIT_FAILURE);
    }
}

void clientLeave()
{
    printf("Leaving ...\n");
    makeBuf(3, NULL);   
    if(sendto(client_sockfd, buf, BUFSIZ, 0, (struct sockaddr *) & server_addr, sizeof(struct sockaddr)) < 0)
    {
        perror("Leaving failed");
        close(client_sockfd);
        exit(EXIT_FAILURE);
    }
}

void exeCommand(char command[])
{
    if (command[0] != '/')
    {
        printf("Invalid format. Commands should start with `/\'\n");
        return;
    }
    if (strcmp(command, "/help") == 0 || strcmp(command, "/?") == 0) 
    {
        puts(Manual);
        return;
    }
    if (strcmp(command, "/clear") == 0)
    {
        system("clear");
        return;
    }
    if (strcmp(command, "/refresh") == 0)
    {
        clientRefresh();
        return;
    }
    if (strcmp(command, "/bid") == 0)
    {
        clientBid();
        return;
    }
    if (strcmp(command, "/leave") == 0)
    {
        clientLeave();
        return;
    }
    printf("Command not found.\n");
    return;
}

void * readCommand (void * args)
{
    char command[CMDSIZE];
    while (1)
    {
    GETCMD:
        putchar('>');
        memset(command, 0, sizeof(command));
        scanf("%[^\n]", command);
        exeCommand(command);
        getchar();
    }
    return NULL;
}

int main()
{
    startClient(); 
    clientLoggin(); 
    pthread_t listeningT, readCMD;  
    pthread_create(&listeningT, NULL,(void *)listening, NULL);
    pthread_create(&readCMD, NULL, (void *)readCommand, NULL);
    pthread_join(listeningT, NULL);
    pthread_join(readCMD, NULL);
    return 0;
}
