/* ------------------------------------------------
 *
 * From IppSec HackBack YouTube video 
 *
 * https://youtu.be/B9nozi1PrhY
 *
 * ------------------------------------------------ */

#include <string.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>

void xor(char *data, int len, char *key, int klen) {

  unsigned char *a = (unsigned char *)data;
  unsigned char *k = (unsigned char *)key;

  for (int i = 0; i < len; i++) {
    a[i] ^= k[i % klen];
  };
}

int main(int argc, char *argv[]) {
  int in_fd;
  int out_fd;
  char *b;

  if (argc < 4) {
    printf("Usage: \n./encrypt input output key");
  };

  in_fd  = open(argv[1], O_RDONLY);
  out_fd = open(argv[2], O_RDWR | O_CREAT);

  if (in_fd != -1) {
    struct stat s;
    fstat(in_fd, &s);

    b = malloc(s.st_size);
    read(in_fd, b, s.st_size);

    xor(b, s.st_size, argv[3], strlen(argv[3]));

    write(out_fd, b, s.st_size);

    close(in_fd);
    close(out_fd);
			   
  };
  
};
