#include <ArduinoPins.h>
#include <FatReader.h>
#include <FatStructs.h>
#include <mcpDac.h>
#include <SdInfo.h>
#include <SdReader.h>
#include <WaveHC.h>
#include <Wavemainpage.h>
#include <WavePinDefs.h>
#include <WaveUtil.h>

#include <SPI.h>
#include <Ethernet2.h>
#include <TextFinder.h>
#include <Time.h>
#include <TimeLib.h>

// Defines voltage threshold for audio playing
#define THRESH 3000

// Defines number of iterations the audio logic loops
#define SONG_ITERATIONS 100

// Analog input pins
#define panel_0 A0
#define panel_1 A1
#define panel_2 A2
#define panel_3 A3
#define panel_4 A4
#define panel_5 A5
#define panel_6 A6
#define panel_7 A7
#define panel_8 A8
#define panel_9 A9

/**************************
 * Data collection globals
 **************************/

// MAC address of Ethernet 2 Shield
byte mac[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
char server[] = {72, 30, 202, 51}; // Yahoo! Weather

EthernetClient client;
TextFinder finder(client);

int temp;
char condition[40];

/**********
 * Setup
 **********/

void setup() {
  // Setup serial
  Serial.begin(9600);
  
  // PINS DEFAULT TO INPUT
  
  // Check IP status
  if(Ethernet.begin(mac)){
    Serial.println("Got IP address.");
  }
  else{
    Serial.println("Unable to get IP using DHCP.");
  }
}

void loop() {
  /***************************
   * Weather data collection
   ***************************/
  
  // Connect to Yahoo! weather
  if(client.connect(server, 80)){
    Serial.println("Connected to Yahoo! Weather.");
    // GET weather forcast for Kirtland, OH
    client.println("GET http://weather.yahooapis.com/forecastrss?w=2433149");
    client.println();
  }
  else{
    Serial.println("Unable to connect to Yahoo! Weather.");
  }

  // Read data from Yahoo! Weather
  // If the client is connected to the Yahoo! server
  if(client.connected()){
    finder.find("temp=");
    temp = finder.getValue();
    finder.find("<yweather:condition  text=");
    finder.getString("\"", "\"", condition, 40);
  }
  
  // Reset client
  client.stop();
  client.flush();

  /********************
   * Audio processing
   ********************/
  int thresholds[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
  int panels[10] = {panel_0, panel_1, panel_2, panel_3, panel_4, panel_5, panel_6, panel_7, panel_8, panel_9}; 

  // Audio processing loop
  for(int iterations = 0; iterations < SONG_ITERATIONS; iterations++){
    for(int i = 0; i < 10; i++){
      // Calculate new threshold (voltage input) value for panel i
      thresholds[i] += analogRead(panels[i]);
      // If exceeds threshold, play sound
      if(thresholds[i] > THRESH){
        // Reset threshold measurement
        thresholds[i] = 0;
        // Play sound
        
        // Delay sound length
        delay(500); // e.g.
      }
      // Else loop
    }
  }
}


