/*
Basic_I2C.ino
Brian R Taylor
brian.taylor@bolderflight.com

Copyright (c) 2017 Bolder Flight Systems

Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
and associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, 
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or 
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING 
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

#include <MPU9250.h>
#include <Battery.h>

// an MPU9250 object with the MPU-9250 sensor on I2C bus 0 with address 0x68
MPU9250 IMU(Wire,0x68);
int status;

const int trigPin = 9;
const int echoPin = 10;

float errors[6];

Battery battery(10500, 12000, A0);


float hxb;
float hxs;
float hyb;
float hys;
float hzb;
float hzs;

int freq;
float t0;

void setup() {
  // serial to display data
  Serial.begin(115200);
  while(!Serial) {}

  // start communication with IMU 
  status = IMU.begin();
  //status = IMU.calibrateAccel();
  status = IMU.setSrd(9);
  battery.begin(4900, 2.4);

  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
  
  /*
  float axb;
  axb = IMU.getAccelBiasX_mss();
  float axs;
  axs = IMU.getAccelScaleFactorX();
  float ayb;
  ayb = IMU.getAccelBiasY_mss();
  float ays;
  ays = IMU.getAccelScaleFactorY();
  float azb;
  azb = IMU.getAccelBiasZ_mss();
  float azs;
  azs = IMU.getAccelScaleFactorZ();
  IMU.setAccelCalX(axb,axs);
  IMU.setAccelCalY(ayb,ays);
  IMU.setAccelCalZ(azb,azs);*/

  if (status < 0) {
    Serial.println("IMU initialization unsuccessful");
    Serial.println("Check IMU wiring or try cycling power");
    Serial.print("Status: ");
    Serial.println(status);
    while(1) {}
  }
  calculate_IMU_error(errors);
  //Serial.println(errors[0]);
  //Serial.println(errors[1]);
  //Serial.println(errors[2]);
  
  
  if(status < 0)
    Serial.println("mag cal err");
  else{
    Serial.println("calibrate mag");
    while(!Serial.available()){
      Serial.println("calibrate mag");
      }
      /*
    status = IMU.calibrateMag();
    hxb = IMU.getMagBiasX_uT();
    hxs = IMU.getMagScaleFactorX();
    hyb = IMU.getMagBiasY_uT();
    hys = IMU.getMagScaleFactorY();
    hzb = IMU.getMagBiasZ_uT();
    hzs = IMU.getMagScaleFactorZ();
    */
    Serial.println("OK");
    Serial.println("OK");
    
    /*
    Serial.println(hxb);  
    Serial.println(hxs);
    Serial.println(hyb);
    Serial.println(hys);
    Serial.println(hzb);
    Serial.println(hzs);
    //IMU.setMagCalX(hxb,hxs);
    //IMU.setMagCalY(hyb,hys);
    //IMU.setMagCalZ(hzb,hzs);
    */
   }
   //t0 = millis();
   //freq = 0;
   IMU.setAccelRange(MPU9250::ACCEL_RANGE_2G);
   IMU.setGyroRange(MPU9250::GYRO_RANGE_250DPS);
   IMU.setSrd(9);
}

void loop() {
  // read the sensor
  // x ve y nin bi sebepten yeri degisik. ve niyeyse calibre olmuyo kendiliginden
  IMU.readSensor();
  // display the data
  Serial.print(IMU.getAccelY_mss()-errors[1],6);
  Serial.print(",");
  Serial.print(IMU.getAccelX_mss()-errors[0],6);
  Serial.print(",");
  Serial.print(IMU.getAccelZ_mss()-errors[2],6);
  Serial.print(";");
  Serial.print(IMU.getGyroY_rads()-errors[4],6);
  Serial.print(",");
  Serial.print(IMU.getGyroX_rads()-errors[3],6);
  Serial.print(",");
  Serial.print(IMU.getGyroZ_rads()-errors[5],6);
  Serial.print(";");
  /*
  Serial.print((IMU.getMagX_uT() - hxb) * hxs,6);
  Serial.print(",");
  Serial.print((IMU.getMagY_uT() - hyb) * hys,6);
  Serial.print(",");
  Serial.print((IMU.getMagZ_uT() - hzb) * hzs,6);
  Serial.print(";");
  */
  Serial.print(get_dist(), 6);
  Serial.print(";");
  float b = 0;
  b = battery.level();
  Serial.print(b);
  //Serial.print(++freq/(millis()-t0)*1000);
  //tprev = millis();
  Serial.print("\n");
  //Serial.println(IMU.getTemperature_C(),6);
  //delay(10);
}

void calculate_IMU_error(float arr[]) {
  // We can call this funtion in the setup section to calculate the accelerometer and gyro data error. From here we will get the error values used in the above equations printed on the Serial Monitor.
  // Note that we should place the IMU flat in order to get the proper values, so that we then can the correct values
  // Read accelerometer values 200 times
  float GyroX, GyroY, GyroZ;
  float AccErrorX = 0, AccErrorY = 0, AccErrorZ = 0, GyroErrorX = 0, GyroErrorY = 0, GyroErrorZ = 0;
  int n = 800;
  
  for(int i=0; i < n; i++){
    IMU.readSensor();
    AccErrorX += IMU.getAccelX_mss();
    AccErrorY += IMU.getAccelY_mss();
    AccErrorZ += IMU.getAccelZ_mss();
    GyroErrorX += IMU.getGyroX_rads();
    GyroErrorY += IMU.getGyroY_rads();
    GyroErrorZ += IMU.getGyroZ_rads();
  }

  float rva[] = {AccErrorX, AccErrorY, AccErrorZ, GyroErrorX, GyroErrorY, GyroErrorZ};
  for(int i=0; i<6; i++){
      arr[i] = rva[i]/n;
  }
  arr[2] = (-9.81 + arr[2]);
}

float get_dist(){
  long duration;
  float distance;
  // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  distance = duration*0.034/2;
  return distance;
}
