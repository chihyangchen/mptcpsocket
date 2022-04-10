// Client side C/C++ program to demonstrate Socket
// programming
#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <string>
#include <chrono>
#include <thread>
#include <iomanip>
#include <sstream>
#include <time.h>
#include <iostream>
#include <unistd.h>

#define PORT 3270

using namespace std; 

string int_to_hex(int i )
{
    stringstream stream;
    stream << "0x" 
        << setfill ('0') << setw(sizeof(int)*2) 
        << hex << i;
    return stream.str();
}

uint64_t timeSinceEpochMillisec() {
  using namespace std::chrono;
  return duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
}

string gen_random(const int len) {
    static const char alphanum[] =
        "0123456789"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz";
    std::string tmp_s;
    tmp_s.reserve(len);

    for (int i = 0; i < len; ++i) {
        tmp_s += alphanum[rand() % (sizeof(alphanum) - 1)];
    }
    
    return tmp_s;
}

int main(int argc, char const* argv[])
{
    int sock = 0, valread;
    struct sockaddr_in serv_addr;
    char send_buf[1024] = {0};
    char buffer[4096] = { 0 };
    int seq = 0;
    int packet_length = 362;   
    time_t timer;
    int time_int_part;
    int time_float_part;
    char ts_buf[32] = {0};
    char seq_buf[16] = {0};
    uint total_time = 10;
    double bandwidth = 289.6*1000;
    double expected_packet_per_sec = bandwidth / (packet_length << 3);
    double sleeptime = 1.0 / expected_packet_per_sec;
    double prev_sleeptime = sleeptime;

    string seq_str = "";
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        printf("\n Socket creation error \n");
        return -1;
    }
 
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);
 
    // Convert IPv4 and IPv6 addresses from text to binary
    // form
    if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr)
        <= 0) {
        printf(
            "\nInvalid address/ Address not supported \n");
        return -1;
    }
 
    if (connect(sock, (struct sockaddr*)&serv_addr,
                sizeof(serv_addr))
        < 0) {
        printf("\nConnection Failed \n");
        return -1;
    }

    time(&timer);  /* get current time; same as: timer = time(NULL)  */
    time_int_part = (int) timer;
    time_float_part = (timer - time_int_part) * 1e8;
    // printf("%d, %d, %d", timer, time_int_part, time_float_part);



    auto now = chrono::steady_clock::now();
    auto ts = timeSinceEpochMillisec();
    string redundent = gen_random(packet_length-16-32);
    
    int count_packet = 0;
    int count_time = 1;
    auto start_time = chrono::steady_clock::now();
    cout << "sleep time " << sleeptime << endl;
    do {
        now = chrono::steady_clock::now();
        ts = timeSinceEpochMillisec();
        sprintf(send_buf, "%32lx%16x%s", ts, seq, redundent.c_str());
        // printf("len: %d\n", strlen(send_buf));
        send(sock, send_buf, strlen(send_buf), 0);
        seq += 1;
        count_packet += 1;
        // this_thread::sleep_for(chrono::milliseconds((int) (sleeptime  * 1000)));
        this_thread::sleep_for(chrono::milliseconds((int) (1000 * sleeptime)));
    // } while (seq  < 10);
        if (chrono::duration_cast<chrono::seconds>(now - start_time).count() > count_time ) {
            // printf("# packet: %d exp%g\n", count_packet, expected_packet_per_sec);
            int tx_bytes = count_packet * packet_length;
            printf("[%d-%d]\t%g kbps\n", count_time-1, count_time, 1.0*tx_bytes/1024*8);
            count_packet = 0;
            count_time += 1;
        }


    } while (chrono::duration_cast<chrono::seconds>(now - start_time).count() < 3600);

    cout << "finish\n";
    close(sock);
    return 0;
}