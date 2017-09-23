/*  NTX2 Radio Test Part 2

    Transmits data via RTTY with a checksum.

    Created 2012 by M0UPU as part of a UKHAS Guide on linking NTX2 Modules to Arduino.
    RTTY code from Rob Harrison Icarus Project.
    http://ukhas.org.uk
*/

#define AFSK_PIN 13

#define SPACE 1200
#define MARK 2200
#define BAUDRATE 100

#include <string.h>
#include <util/crc16.h>

union {
    char dataByte[4];
    long data;
} lat, lon, crc16;

uint16_t crc;
unsigned long delay_rate;

void setup() {
  pinMode(AFSK_PIN, OUTPUT);
  delay_rate = 1000/BAUDRATE;
}

void loop() {

  for(int i=0; i<100; i++) {
    lat.data = 36.723489 * 1000000;
    lon.data = -4.435540 * 1000000;

    //lat.data = i * 1000000;
    //lon.data = i * 100000;

    crc = 0;
    crc = get_crc16(lat.dataByte, 4, crc);  // Calculates the checksum for this datastring
    crc = get_crc16(lon.dataByte, 4, crc);  // Calculates the checksum for this datastring
    crc16.data = crc;
  
    rtty_txstring ("  ", 2);
    rtty_txstring (lat.dataByte, 4);
    rtty_txstring (lon.dataByte, 4);
    rtty_txstring (crc16.dataByte, 4);
    rtty_txstring ("**", 2);
  }
}


void rtty_txstring (char * string, int len)
{

  /* Simple function to sent a char at a time to
     ** rtty_txbyte function.
    ** NB Each char is one byte (8 Bits)
    */

  char c;

  c = *string;

  for (int i=0; i<len; i++) {
    rtty_txbyte (string[i]);
  }
  
}


void rtty_txbyte (char c)
{
  /* Simple function to sent each bit of a char to
    ** rtty_txbit function.
    ** NB The bits are sent Least Significant Bit first
    **
    ** All chars should be preceded with a 0 and
    ** proceded with a 1. 0 = Start bit; 1 = Stop bit
    **
    */

  int i;

  rtty_txbit (0); // Start bit

  // Send bits for for char LSB first

  for (i=0;i<8;i++) // Change this here 7 or 8 for ASCII-7 / ASCII-8
  {
    if (c & 1) rtty_txbit(1);

    else rtty_txbit(0);

    c = c >> 1;

  }

  rtty_txbit (1); // Stop bit
  rtty_txbit (1); // Stop bit
}

void rtty_txbit (int bit)
{
  if (bit)
  {
    // MARK = 1
    tone(AFSK_PIN, MARK);
  }
  else
  {
    // SPACE = 0
    tone(AFSK_PIN, SPACE);
  }

  delay(delay_rate);
}

uint16_t get_crc16 (char *string, int data_size, uint16_t crc)
{
  size_t i;
  
  uint8_t c;

  // Calculate checksum ignoring the first two $s
  for (int i = 0; i < data_size; i++)
  {
    c = string[i];
    crc = _crc16_update (crc, c);
  }

  return crc;
}

