#include <SPI.h>
#include <Ethernet2.h>
#include <TextFinder.h>
#include <Time.h>
#include <TimeLib.h>

// MAC address of Ethernet 2 Shield
byte mac[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
char server[] = {72, 30, 202, 51}; // Yahoo! Weather

Client client;
TextFinder finder(client);
int temp;
char condition[40];

void setup() {
  // Check IP status
  if(Ethernet2.begin(mac)){
    Serial.println("Got IP address.");
  }
  else{
    Serial.println("Unable to get IP using DHCP.");
  }
}

void loop() {
  // put your main code here, to run repeatedly:
 
  // Connect to Yahoo! weather
  if(client.connect()){
    Serial.println("Connected to Yahoo! Weather.");
    // GET weather forcast for Kirtland, OH
    client.println("GET http://weather.yahooapis.com/forecastrss?w=2433149";
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
      finder.getString("\"", "\"", cond, 40);
    }
  }

  // Reset client
  client.stop();
  client.flush();
   
}
