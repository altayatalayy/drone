/*
   Arduino and MPU6050 Accelerometer and Gyroscope Sensor Tutorial
   by Dejan, https://howtomechatronics.com
*/

#include <Wire.h>

const int MPU = 0x68; // MPU6050 I2C address
float elapsedTime, currentTime = 0, previousTime;
float errors[5];

void calculate_IMU_error(float arr[]);
void read_imu(float rv[]);
void send_data(float acc_x, float acc_y, float acc_z, float gyr_x, float gyr_y, float gyr_z);

void setup() {
  Serial.begin(19200);
  Wire.begin();                      // Initialize comunication
  Wire.beginTransmission(MPU);       // Start communication with MPU6050 // MPU=0x68
  Wire.write(0x6B);                  // Talk to the register 6B
  Wire.write(0x00);                  // Make reset - place a 0 into the 6B register
  Wire.endTransmission(true);        //end the transmission
  calculate_IMU_error(errors);
  for(int i=0; i<5; i++)
    Serial.println(errors[i]);
  delay(100);
  Serial.println("ready");

}

void loop() {
  float AccX, AccY, AccZ;
  float GyroX, GyroY, GyroZ;
  float accAngleX, accAngleY, gyroAngleX, gyroAngleY, gyroAngleZ;
  float roll, pitch, yaw;
  // Calculating Roll and Pitch from the accelerometer data
  float vals[6] = {0, 0, 0, 0, 0, 0}; 
  read_imu(vals);
  AccX = vals[0];
  AccY = vals[1];
  AccZ = vals[2];
  GyroX = vals[3];
  GyroY = vals[4];
  GyroZ = vals[5];
  
  
  accAngleX = (atan(AccY / sqrt(pow(AccX, 2) + pow(AccZ, 2))) * 180 / PI) - errors[0]; // AccErrorX ~(0.58) See the calculate_IMU_error()custom function for more details
  accAngleY = (atan(-1 * AccX / sqrt(pow(AccY, 2) + pow(AccZ, 2))) * 180 / PI) - errors[1]; // AccErrorY ~(-1.58)

  // === Read gyroscope data === //
  previousTime = currentTime;        // Previous time is stored before the actual time read
  currentTime = millis();            // Current time actual time read
  elapsedTime = (currentTime - previousTime) / 1000; // Divide by 1000 to get seconds
  
  // Correct the outputs with the calculated error values
  GyroX = GyroX - errors[2]; // GyroErrorX ~(-0.56)
  GyroY = GyroY - errors[3]; // GyroErrorY ~(2)
  GyroZ = GyroZ - errors[4]; // GyroErrorZ ~ (-0.8)

  // Currently the raw values are in degrees per seconds, deg/s, so we need to multiply by sendonds (s) to get the angle in degrees
  gyroAngleX = gyroAngleX + GyroX * elapsedTime; // deg/s * s = deg
  gyroAngleY = gyroAngleY + GyroY * elapsedTime;
  yaw =  yaw + GyroZ * elapsedTime;

  // Complementary filter - combine acceleromter and gyro angle values
  roll = 0.96 * gyroAngleX + 0.04 * accAngleX;
  pitch = 0.96 * gyroAngleY + 0.04 * accAngleY;

  float g = 9.81;
  send_data(AccX * g, AccY * g, AccZ * g, roll, pitch, yaw);
}


void calculate_IMU_error(float arr[]) {
  // We can call this funtion in the setup section to calculate the accelerometer and gyro data error. From here we will get the error values used in the above equations printed on the Serial Monitor.
  // Note that we should place the IMU flat in order to get the proper values, so that we then can the correct values
  // Read accelerometer values 200 times
  float AccX, AccY, AccZ;
  float GyroX, GyroY, GyroZ;
  float AccErrorX, AccErrorY, GyroErrorX, GyroErrorY, GyroErrorZ;
  int c = 0;
  while (c < 200) {
    Wire.beginTransmission(MPU);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, 6, true);
    AccX = (Wire.read() << 8 | Wire.read()) / 16384.0 ;
    AccY = (Wire.read() << 8 | Wire.read()) / 16384.0 ;
    AccZ = (Wire.read() << 8 | Wire.read()) / 16384.0 ;
    // Sum all readings
    AccErrorX = AccErrorX + ((atan((AccY) / sqrt(pow((AccX), 2) + pow((AccZ), 2))) * 180 / PI));
    AccErrorY = AccErrorY + ((atan(-1 * (AccX) / sqrt(pow((AccY), 2) + pow((AccZ), 2))) * 180 / PI));
    c++;
  }
  //Divide the sum by 200 to get the error value
  AccErrorX = AccErrorX / 200;
  AccErrorY = AccErrorY / 200;
  c = 0;
  // Read gyro values 200 times
  while (c < 200) {
    Wire.beginTransmission(MPU);
    Wire.write(0x43);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, 6, true);
    GyroX = Wire.read() << 8 | Wire.read();
    GyroY = Wire.read() << 8 | Wire.read();
    GyroZ = Wire.read() << 8 | Wire.read();
    // Sum all readings
    GyroErrorX = GyroErrorX + (GyroX / 131.0);
    GyroErrorY = GyroErrorY + (GyroY / 131.0);
    GyroErrorZ = GyroErrorZ + (GyroZ / 131.0);
    c++;
  }
  //Divide the sum by 200 to get the error value
  GyroErrorX = GyroErrorX / 200;
  GyroErrorY = GyroErrorY / 200;
  GyroErrorZ = GyroErrorZ / 200;

  float rva[] = {AccErrorX, AccErrorY, GyroErrorX, GyroErrorY, GyroErrorZ};
  for(int i=0; i<5; i++){
      arr[i] = rva[i];
    }
}

void read_imu(float rv[]){
  // === Read acceleromter data === //
  float acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z;
  Wire.beginTransmission(MPU);
  Wire.write(0x3B); // Start with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6, true); // Read 6 registers total, each axis value is stored in 2 registers
  //For a range of +-2g, we need to divide the raw values by 16384, according to the datasheet
  acc_x = (Wire.read() << 8 | Wire.read()) / 16384.0; // X-axis value
  acc_y = (Wire.read() << 8 | Wire.read()) / 16384.0; // Y-axis value
  acc_z = (Wire.read() << 8 | Wire.read()) / 16384.0; // Z-axis value

  Wire.beginTransmission(MPU);
  Wire.write(0x43); // Gyro data first register address 0x43
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6, true); // Read 4 registers total, each axis value is stored in 2 registers
  gyr_x = (Wire.read() << 8 | Wire.read()) / 131.0; // For a 250deg/s range we have to divide first the raw value by 131.0, according to the datasheet
  gyr_y = (Wire.read() << 8 | Wire.read()) / 131.0;
  gyr_z = (Wire.read() << 8 | Wire.read()) / 131.0;
  Wire.endTransmission(true);
  
  float rva[] = {acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z};
  for(int i=0; i<6; i++){
      rv[i] = rva[i];
    }
}

void send_data(float acc_x, float acc_y, float acc_z, float gyr_x, float gyr_y, float gyr_z){
  Serial.print("x:"); Serial.print(acc_x);
  Serial.print(",y:"); Serial.print( acc_y);
  Serial.print(",z:"); Serial.print(acc_z);
  Serial.print(";x:"); Serial.print(gyr_x);
  Serial.print(",y:"); Serial.print(gyr_y);
  Serial.print(",z:"); Serial.println(gyr_z);
}
