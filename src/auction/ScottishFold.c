#include "ScottishFold.h"

void addUser (char username[])
{
    int i;
    onboard_addr[clientN] = client_addr;

    printf("\nNew client from %s:\n", inet_ntoa(client_addr.sin_addr));
    buf[len]='\0';
    printf("Name: ");
    for (i = 1; i < strlen(buf); i++)
        putchar(buf[i]);
    putchar('\n');
    
    char toShell0[50], toShell1[50], toShell2[50];
    system("date +%Y%m%d%H%M%S >> userInfo.LazyCat"); 
    sprintf(toShell0, "echo %d >> userInfo.LazyCat", clientN);
    system(toShell0);
    sprintf(toShell1, "echo %s >> userInfo.LazyCat", inet_ntoa(client_addr.sin_addr));
    system(toShell1);
    sprintf(toShell2, "echo %s >> userInfo.LazyCat", username);
    system(toShell2);
    memset(buf, 0, BUFSIZ);
    sprintf(buf, "Success");
    if(sendto(server_sockfd, buf, BUFSIZ, 0, (struct sockaddr *) & client_addr, sizeof(struct sockaddr)) < 0)
    {
        perror("sendto failed");
    }
    clientN++;  
    
    if (currentAuction)
    {
        memset(buf, 0, BUFSIZ);
        sprintf(buf, "\nCurrent auction is running. You're late!\nType `/refresh' to see current auction state.\n");
        if(sendto(server_sockfd, buf, BUFSIZ, 0, (struct sockaddr *) & client_addr, sizeof(struct sockaddr)) < 0)
        {
            perror("sendto failed");
        }

    }
    
    return;
}

void refreshState ()
{
    if (!currentAuction)
    {
        memset(buf, 0, BUFSIZ);
        sprintf(buf, "\nCurrently no auction is running.\n");
        if(sendto(server_sockfd, buf, BUFSIZ, 0, (struct sockaddr *) & client_addr, sizeof(struct sockaddr)) < 0)
        {
            perror("sendto failed");
        }
        return;
    }
    char line[100];
    memset(buf, 0, sizeof(buf));
    FILE * fp = fopen("auctionInfo.LazyCat", "r");
    while(fgets(line, sizeof(line), fp))
    {
        if(sendto(server_sockfd, line, strlen(line), 0, (struct sockaddr *) & client_addr, sizeof(struct sockaddr)) < 0)
        {
            perror("sendto failed");
        }
    }
    fclose(fp);
}

void newBid()
{
    memset(buf, 0, sizeof(buf));
    if (!currentAuction)
    {
        sprintf(buf, "Currently no auction running. Bidding failed.\n");
        if(sendto(server_sockfd, buf, strlen(buf), 0, (struct sockaddr *) & client_addr, sizeof(struct sockaddr)) < 0)
        {
            perror("sendto failed");
        }
        return;
    }
    
    char toShell[100];
    char line[100];
    char * bidderIP = inet_ntoa(client_addr.sin_addr); 
    char tmpArray[100];
    int i;
    FILE * fp;
    fp = fopen("userInfo.LazyCat","r");
    while(!feof(fp))
    {
        fgets(line, sizeof(line), fp);
        if (strncmp(line, bidderIP, strlen(bidderIP)) == 0)
        {
            fgets(line, sizeof(line), fp);  
            line[strlen(line)-1] = '\0';
            sprintf(toShell, "echo '$%d by %s' >> auctionInfo.LazyCat", currentPrice + 10, line);
            system(toShell);
            printf("\nNew bid : %d by %s from %s\n", currentPrice + 10, line, bidderIP);
            currentPrice += 10;
            fclose(fp);
            sprintf(buf, "Success! You're now holding the highest price.\n");
            if(sendto(server_sockfd, buf, strlen(buf), 0, (struct sockaddr *) & client_addr, sizeof(struct sockaddr)) < 0)
            {
                perror("sendto failed");
            }
            for (i = 0; i < clientN; i++)
            {
                memset(tmpArray, 0, sizeof(tmpArray));
                sprintf(tmpArray, "%s", inet_ntoa(onboard_addr[i].sin_addr));
                if (strncmp(tmpArray, inet_ntoa(client_addr.sin_addr), strlen(tmpArray)) == 0)
                    break;
            }
            winnerID = i;
            bidderHoldingHighestPrice = line;
            return;
        }
    }
    sprintf(buf, "You're not on the bidder list.\nBidding failed.\n");
    if(sendto(server_sockfd, buf, strlen(buf), 0, (struct sockaddr *) & client_addr, sizeof(struct sockaddr)) < 0)
    {
        perror("sendto failed");
    }
    fclose(fp);
}   

void sendLeaveCode()
{
    memset(buf, 0, sizeof(buf));
    sprintf(buf, "Uoyj9gJcuDBfEpcFKq9htFGW");  
    sendto(server_sockfd, buf, strlen(buf), 0, (struct sockaddr *) & client_addr, sizeof(struct sockaddr));
}

int holdingHighestPrice (char bidderName[])
{
    if (strcmp(bidderHoldingHighestPrice, bidderName) == 0)
        return 1;
    else
        return 0;
}

void bidderLeave()
{
    int i, j;
    char toShell[100];
    char line[100];
    char tmpArray[100];
    char * bidderIP = inet_ntoa(client_addr.sin_addr);
    FILE * fp;
    fp = fopen("userInfo.LazyCat","r");
    while(!feof(fp))
    {
        fgets(line, sizeof(line), fp);
        if (strncmp(line, bidderIP, strlen(bidderIP)) == 0)
        {
            fgets(line, sizeof(line), fp);
            fclose(fp);
            line[strlen(line)-1] = '\0';
            if (holdingHighestPrice (line) && currentAuction)
            {
                memset(buf, 0, BUFSIZ);
                sprintf(buf, "\nCannot leave because you're holding the highest price.\n");
                if(sendto(server_sockfd, buf, BUFSIZ, 0, (struct sockaddr *) & client_addr, sizeof(struct sockaddr)) < 0)
                {
                    perror("sendto failed");
                }
                return;
            }
            sprintf(toShell, "sed 's/%s/%s [Leaved]/' < userInfo.LazyCat > userInfo.tmp", line, line);
            system(toShell);
            system("mv userInfo.tmp userInfo.LazyCat");
            for (i = 0; i < clientN; i++)
            {
                memset(tmpArray, 0, sizeof(tmpArray));
                sprintf(tmpArray, "%s", inet_ntoa(onboard_addr[i].sin_addr));
                if (strncmp(tmpArray, inet_ntoa(client_addr.sin_addr), strlen(tmpArray)))
                    break;
            }
            for (j = i; i < clientN; i++)
            {
                onboard_addr[j] = onboard_addr[j+1];
            }
            clientN--;
            sendLeaveCode();
            return;
        }
    }
    fclose(fp);
    sendLeaveCode();
}

void * listening (void * args)
{
    while (1)
    {
        if((len = recvfrom (server_sockfd, buf, BUFSIZ, 0, (struct sockaddr *) & client_addr, & sin_size)) < 0)
        {
            perror("recvfrom");
        }
        
        switch (buf[0])
        {
            case '0':
                addUser(&buf[1]);   
                break;
            case '1':
                refreshState(); 
                break;
            case '2':
                newBid();   
                break;
            case '3':
                bidderLeave();  
                break;
            default:
                break;
        }
    }
    return NULL;
}

void listBidders()
{
    printf("\nCurrent online bidders:\n");
    system("python listBidders.py");    
}

void sendMessage ()
{
    int Num = -1;
    char nameList[80];
    char userID[14];
    char line[50];
    getchar();
    printf("Enter BidderIDs for message receivers: (Hit `Enter' when finish)\n");
    scanf("%[^\n]", nameList);
    getchar();
    printf("Enter message to send:\n");
    char msg[100];
    scanf("%[^\n]", msg);   
    getchar();
    sprintf(msg, "%s\n", msg);  
    printf("Sending ... \n");
    int i = 0, j;
    while (nameList[i] != '\0')
    {
        if (nameList[i] != ' ')
        {
            for (j = 0; j < 14; j++)
                userID[j] = nameList[i+j];
            userID[j] = '\0';
            FILE * fp;
            fp = fopen("userInfo.LazyCat","r");
            while(!feof(fp))
            {
                fgets(line, sizeof(line), fp);
                if (strncmp(line, userID, 14) == 0)
                {
                    fscanf(fp, "%d", & Num);
                    break;
                }
            }
            fclose(fp);
            if(sendto(server_sockfd, msg, strlen(msg), 0, (struct sockaddr *) & onboard_addr[Num], sizeof(struct sockaddr)) < 0)
            {
                perror("sendto failed");
            }
            i += 14;
            continue;
        }
        i++;
    }
    printf("Done"); 
}

void kickoutBidders()
{
    char kickoutID[15], line[50];
    int shortID = -1, i;
    struct sockaddr_in tmpaddr;
    printf("Enter ID to kickout bidder :"); 
    scanf("%s", kickoutID);
    FILE * fp;
    fp = fopen("userInfo.LazyCat","r");
    while(!feof(fp))
    {
        fgets(line, sizeof(line), fp);
        if (strncmp(line, kickoutID, 14) == 0)
        {
            fscanf(fp, "%d", & shortID);
            break;
        }
    }
    fclose(fp);
    for (i = shortID; i < clientN-1; i++)
    {
        tmpaddr = onboard_addr[i];
        onboard_addr[i] = onboard_addr[i+1];
    }
    clientN--;  
    system("python kickoutBidders.py"); 
}

void openAuction()
{
    if (currentAuction)
    {
        printf("\nsCannot open a new auction.\nCurrent auction should be finished first.\n");
        return;
    }
    if (!clientN)
    {
        printf("\nNo bidder found.\n");
        return;
    }
    system("touch auctionInfo.LazyCat");
    auctionCount++; 
    winnerID = -1; 
    char toShell[100];  
    sprintf(toShell, "echo Auction [%d] starting. > auctionInfo.LazyCat", auctionCount);
    system(toShell);    
    int i = 0;
    currentPrice = 100;
    memset(buf, 0, sizeof(buf));
    
    sprintf(buf, "Announcement : A new auction opened.\nStarting price $100\n");
    system("echo 'Starting price $100' >> auctionInfo.LazyCat");
    for (i = 0; i < clientN; i++)
    {
        if(sendto(server_sockfd, buf, BUFSIZ, 0, (struct sockaddr *) & onboard_addr[i], sizeof(struct sockaddr)) < 0)
        {
            perror("sendto failed");
        }
    }
    currentAuction = 1; 
}

void startServer()
{
    printf("Server starting");
    clientN = 0;
    printf(" ...");
    system("touch serverIP.LazyCat");
    system("touch userInfo.LazyCat");
    
    printf(" ...");
    memset(& server_addr, 0, sizeof(server_addr)); 
    server_addr.sin_family = AF_INET;   
    server_addr.sin_addr.s_addr = INADDR_ANY; 
    server_addr.sin_port = htons(8000);  
    
    if((server_sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) < 0)
    {
        perror("Error: Can not create socket.");
        return;
    }
    
    printf(" ...");
    
    if (bind(server_sockfd,(struct sockaddr *)& server_addr,sizeof(struct sockaddr))<0)
    {
        perror("Error: Bind failed.");
        return;
    }
    
    printf(" ...");
    
    sin_size = sizeof(struct sockaddr_in);
    
    system("python getIP.py");  
    printf(" [Done]\n");
}

void notifyWinner ()
{
    memset(buf, 0, sizeof(buf));
    sprintf(buf, "\n---------------\nDear %s,\nCongratulations! You win!\n---------------\n", bidderHoldingHighestPrice);
    if(sendto(server_sockfd, buf, BUFSIZ, 0, (struct sockaddr *) & onboard_addr[winnerID], sizeof(struct sockaddr)) < 0)
    {
        perror("sendto failed");
    }
}

void abortiveAuction ()
{
    int i;
    memset(buf, 0, sizeof(buf));
    sprintf(buf, "\n---------------\nCurrent auction failed. No winner.\n---------------\n");
    for (i = 0; i < clientN; i++)
    {
        if(sendto(server_sockfd, buf, BUFSIZ, 0, (struct sockaddr *) & onboard_addr[i], sizeof(struct sockaddr)) < 0)
        {
            perror("sendto failed");
        }
    }
}

void closeAuction()
{
    if (winnerID == -1)
        abortiveAuction();  
    int i, sum;
    float averagePrice, lowestPrice, highestPrice;
    priceHistory[auctionCount-1] = currentPrice; 
    for (i = 0, sum = 0; i < auctionCount; i++)
        sum += priceHistory[i];
    averagePrice = sum / auctionCount;
    for (i = 1, lowestPrice = priceHistory[0]; i < auctionCount; i++)
    {
        if (priceHistory[i] < lowestPrice)
            lowestPrice = priceHistory[i];
    }
    for (i = 1, highestPrice = priceHistory[0]; i < auctionCount; i++)
    {
        if (priceHistory[i] > highestPrice)
            highestPrice = priceHistory[i];
    }
    if (winnerID != -1)
    {
        memset(buf, 0, sizeof(buf));
        sprintf(buf, "\nSold!\n---------------\nHammer price: $%d\n---------------\n\nPrice history:\nLowest: $%f\nHighest: $%f\n---------------\nAverage: $%f\n---------------\n", currentPrice, lowestPrice, highestPrice, averagePrice);
        for (i = 0; i < clientN; i++)
        {
            if(sendto(server_sockfd, buf, BUFSIZ, 0, (struct sockaddr *) & onboard_addr[i], sizeof(struct sockaddr)) < 0)
            {
                perror("sendto failed");
            }
        }
        notifyWinner ();
    }
    for (i = 0; i < clientN; i++)
    {
        memset(buf, 0, sizeof(buf));
        sprintf(buf, "Uoyj9gJcuDBfEpcFKq9htFGW");
        if(sendto(server_sockfd, buf, strlen(buf), 0, (struct sockaddr *) & onboard_addr[i], sizeof(struct sockaddr)) < 0)
        {
            perror("sendto failed");
        }
    }
    system("rm auctionInfo.Lazycat");
    system("rm userInfo.Lazycat");
    system("touch userInfo.LazyCat");
    clientN = 0;
    currentAuction = 0;
}

void exitScottishFold()
{
    int i;
    char command[10];
    if (currentAuction)
    {
        printf("Currently auction is running. Are you sure to exit? [Y/n]");
        scanf("%s", command);
        if(strcmp(command, "Y") == 0 || strcmp(command, "y") == 0)
            exit(0);    
        else
            return;
    }
    else
    {
        printf("Force shutting down clients ... ");
        for (i = 0; i < clientN; i++)
        {
            memset(buf, 0, sizeof(buf));
            sprintf(buf, "PaVk49AavrrxmuMxxADUjcr");    
            if(sendto(server_sockfd, buf, strlen(buf), 0, (struct sockaddr *) & onboard_addr[i], sizeof(struct sockaddr)) < 0)
            {
                perror("sendto failed");
            }
        }
        system("rm *.LazyCat");
        printf("Done\n.........\nBye");
        exit(0);
    }
}

void exeCommand(char command[])
{
    if (command[0] != '/')
    {
        printf("Invalid format. Commands should start with `/\'\n");
        return;
    }
    if (strcmp(command, "/help") == 0 || strcmp(command, "/?") == 0)   //See manual
    {
        puts(Manual);
        return;
    }
    if (strcmp(command, "/clear") == 0)   //Clear
    {
        system("clear");
        return;
    }
    if (strcmp(command, "/msg") == 0)
    {
        sendMessage();
        return;
    }
    if (strcmp(command, "/list") == 0)
    {
        listBidders();
        return;
    }
    if (strcmp(command, "/kickout") == 0)
    {
        kickoutBidders();
        return;
    }
    if (strcmp(command, "/openauction") == 0)
    {
        openAuction();
        return;
    }
    if (strcmp(command, "/closeauction") == 0)
    {
        closeAuction();
        return;
    }
    if (strcmp(command, "/exit") == 0)
    {
        exitScottishFold();
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
    startServer();  
    pthread_t listeningT, readCMD;  
    pthread_create(&listeningT, NULL,(void *)listening, NULL);
    pthread_create(&readCMD, NULL, (void *)readCommand, NULL);
    pthread_join(listeningT, NULL);
    pthread_join(readCMD, NULL);
    return 0;
}
