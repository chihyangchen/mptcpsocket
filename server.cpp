// Server side C/C++ program to demonstrate Socket
// programming
#include <netinet/in.h>
#include <stdio.h>
// #include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <time.h>
#include <chrono>
#include <thread>
#include <iomanip>
#include <sstream>
#include <iostream>

#define PORT 3270

using namespace std;

int sendall(int s, char *buf, int *len)
{
    int total = 0;        // how many bytes we've sent
    int bytesleft = *len; // how many we have left to send
    int n;

    while(total < *len) {
        n = send(s, buf+total, bytesleft, 0);
        if (n == -1) { break; }
        total += n;
        bytesleft -= n;
    }

    *len = total; // return number actually sent here

    return n==-1?-1:0; // return -1 on failure, 0 on success
}



int main(int argc, char const* argv[])
{

	int time = 3600;
	int timer_c = 1;
	double recv_bytes = 0;
	int server_fd, new_socket, valread;
	struct sockaddr_in address;
	int opt = 1;
	int addrlen = sizeof(address);
	char buffer[1024] = { 0 };
	int seq = 0;
	int timeout_in_seconds = 5;
	// Creating socket file descriptor
	cout << "create socket\n";
	if ((server_fd = socket(AF_INET, SOCK_STREAM, 0))
		== 0) {
		perror("socket failed");
		exit(EXIT_FAILURE);
	}

	// Forcefully attaching socket to the port 8080
	if (setsockopt(server_fd, SOL_SOCKET,
				SO_REUSEADDR | SO_REUSEPORT, &opt,
				sizeof(opt))) {
		perror("setsockopt");
		exit(EXIT_FAILURE);
	}
	address.sin_family = AF_INET;
	address.sin_addr.s_addr = INADDR_ANY;
	address.sin_port = htons(PORT);

	// Forcefully attaching socket to the port 8080
	if (bind(server_fd, (struct sockaddr*)&address,
			sizeof(address))
		< 0) {
		perror("bind failed");
		exit(EXIT_FAILURE);
	}
	if (listen(server_fd, 3) < 0) {
		perror("listen");
		exit(EXIT_FAILURE);
	}
	if ((new_socket
		= accept(server_fd, (struct sockaddr*)&address,
				(socklen_t*)&addrlen))
		< 0) {
		perror("accept");
		exit(EXIT_FAILURE);
	}
	cout << "connection establishment\n";

	// LINUX
	struct timeval tv;
	tv.tv_sec = timeout_in_seconds;
	tv.tv_usec = 0;
	setsockopt(new_socket, SOL_SOCKET, SO_RCVTIMEO, (const char*)&tv, sizeof(tv));
    auto start_time = chrono::steady_clock::now();



	while (true) {
		valread = read(new_socket, buffer, 1024);
		if (valread==0) {
			cout << "other side close" << endl;
			break;
		}
		else if (valread < 0) {
			cout << "connection timeout" << endl;
			break;
		}
		recv_bytes += valread;
        auto now = chrono::steady_clock::now();
		// printf("%s\n", buffer);
		if (chrono::duration_cast<chrono::seconds>(now - start_time).count() > timer_c) {
			if (recv_bytes <= 1024*1024) {
				printf("[%d-%d]\t%g kbps\n", timer_c, timer_c+1, recv_bytes/1024*8);
			}
			else {
				printf("[%d-%d]\t%g Mbps\n", timer_c, timer_c+1, recv_bytes/1024/1024*8);
			}
			recv_bytes = 0;
			timer_c += 1;
		}
	}
	cout << "finish\n";
	return 0;
}
