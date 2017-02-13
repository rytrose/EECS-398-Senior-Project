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

/*************************
 * Data collection globals
 *************************/

// MAC address of Ethernet 2 Shield
byte mac[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
char server[] = {72, 30, 202, 51}; // Yahoo! Weather

EthernetClient client;
TextFinder finder(client);

int temp;
char condition[40];

/*************************
 * Audio processing globals
 *************************/

// Analog input pins
int panel_0 = A0;
int panel_1 = A1;
int panel_2 = A2;
int panel_3 = A3;
int panel_4 = A4;
int panel_5 = A5;
int panel_6 = A6;
int panel_7 = A7;
int panel_8 = A8;
int panel_9 = A9;

void setup() {
  
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
  if(!(minute() % 3)){
    // If the client is connected to the Yahoo! server
    if(client.connected()){
      finder.find("temp=");
      temp = finder.getValue();
      finder.find("<yweather:condition  text=");
      finder.getString("\"", "\"", condition, 40);
    }
  }

  // Reset client
  client.stop();
  client.flush();

  /********************
   * Audio processing
   ********************/

  
   
   
}
