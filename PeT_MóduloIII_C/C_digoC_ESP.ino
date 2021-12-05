
#include <ESP8266WiFi.h>
#define SSID "brisa-1179192"
#define PASSWD "66rrllbl"
#define PORT 53530

float angle_aux;
float angle;
float current_angle;
float stepperangle = 1.8;
int stepsperrevolution = 200;
int revolution = stepperangle * stepsperrevolution;
bool dircw = true;

// Bobina 1
const int stepAmarelo = 1;
const int stepLaranja = 2;
// Bobina 2
const int stepVermelho = 3;
const int stepAzul = 4;


WiFiServer server(PORT);

void setup(){
  Serial.begin(9600);
  delay(1000);
  WiFi.begin(SSID,PASSWD);
  while (WiFi.status() != WL_CONNECTED){delay(100);}
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
  server.begin(); //abre a porta 53530

  //define os pinos de controle do step
  pinMode(stepAmarelo, OUTPUT);
  pinMode(stepLaranja, OUTPUT);
  pinMode(stepVermelho, OUTPUT);
  pinMode(stepAzul, OUTPUT);

}

void loop() {         
  WiFiClient client = server.available();
  if (client){
    while (client.connected()){
            String req = "";
            if (client.available() == 0) {continue;}
            while (client.available() > 0){
                char value = client.read();
                req += value;
                if (client.available() == 0){
                  angle = req.toFloat();
                  client.flush();
                  Serial.print("Ângulo recebido do módulo I: ");
                  Serial.println(angle);
                  // CW
                  if (angle > current_angle){
                    angle_aux = angle - current_angle;
                    //dircw é true porque está seguindo em cw
                    dircw = true;
                    current_angle = angle;
                  // CCW
                  } else if (angle < current_angle){
                    angle_aux = current_angle - angle;
                    //dircw é falso porque está seguindo em ccw
                    dircw = false;
                    current_angle = angle;
                  }
                  int x = 0;
                  if (dircw == true){
                    while (x =< angle_aux/stepperangle){
                      // Amarelo
                      digitalWrite(stepAmarelo, HIGH);
                      delayMicroseconds(1000);
                      digitalWrite(stepAmarelo, LOW);
                      delayMicroseconds(1000);
                      x++;
                      Serial.print(x);
                      Serial.print(" ");
                      if (x =< angle_aux/stepperangle){
                        break;
                      }
                      
                      // Laranja
                      digitalWrite(stepLaranja, HIGH);
                      delayMicroseconds(1000);
                      digitalWrite(stepLaranja, LOW);
                      delayMicroseconds(1000);
                      x++;
                      Serial.print(x);
                      Serial.print(" ");
                      if (x =< angle_aux/stepperangle){
                        break;
                      }
                      
                      // Vermelho
                      digitalWrite(stepVermelho, HIGH);
                      delayMicroseconds(1000);
                      digitalWrite(stepVermelho, LOW);
                      delayMicroseconds(1000);
                      x++;
                      Serial.print(x);
                      Serial.print(" ");
                      if (x =< angle_aux/stepperangle){
                        break;
                      }
                      
                      // Azul
                      digitalWrite(stepAzul, HIGH);
                      delayMicroseconds(1000);
                      digitalWrite(stepAzul, LOW);
                      delayMicroseconds(1000);
                      x++;
                      Serial.print(x);
                      Serial.print(" ");
                      if (x =< angle_aux/stepperangle){
                        break;
                      }
                      
                      }
                  } else if (dircw == false){
                      // Azul
                      digitalWrite(stepAzul, HIGH);
                      delayMicroseconds(1000);
                      digitalWrite(stepAzul, LOW);
                      delayMicroseconds(1000);
                      x++;
                      Serial.print(x);
                      Serial.print(" ");
                      if (x =< angle_aux/stepperangle){
                        break;
                      }
                      
                      // Vermelho
                      digitalWrite(stepVermelho, HIGH);
                      delayMicroseconds(1000);
                      digitalWrite(stepVermelho, LOW);
                      delayMicroseconds(1000);
                      x++;
                      Serial.print(x);
                      Serial.print(" ");
                      if (x =< angle_aux/stepperangle){
                        break;
                      }
                      
                      // Laranja
                      digitalWrite(stepLaranja, HIGH);
                      delayMicroseconds(1000);
                      digitalWrite(stepLaranja, LOW);
                      delayMicroseconds(1000);
                      x++;
                      Serial.print(x);
                      Serial.print(" ");
                      if (x =< angle_aux/stepperangle){
                        break;
                      }    

                      // Amarelo
                      digitalWrite(stepAmarelo, HIGH);
                      delayMicroseconds(1000);
                      digitalWrite(stepAmarelo, LOW);
                      delayMicroseconds(1000);
                      x++;
                      Serial.print(x);
                      Serial.print(" ");
                      if (x =< angle_aux/stepperangle){
                        break;
                      }              
                  }
                  }
                  }
              }
              Serial.println("");
              Serial.print("Ângulo auxiliar: ");
              Serial.println(angle_aux);
              Serial.print("Ângulo atual: ");
              Serial.println(current_angle);
              Serial.println("");
      }
          delay(3000);
    }
        client.stop();
}
