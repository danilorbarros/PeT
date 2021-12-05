// Incluindo a biblioteca Stepper
#include <Stepper.h>

// Definindo a quantidade de passos por volta (SPR)
const int stepsPerRevolution = 200;

// Definindo o objeto motor, que contém uma constante como SPR e sai no formado D1,D3,D2,D4
Stepper Motor(stepsPerRevolution, 8, 9, 10, 11);

// Led para debug, vou usar ele pra toda vez que apertar o botão ele ligar um led pra demonstrar de forma visível que leu a entrada
const int PinLed = 4;

// Botão para controle o led
const int PinButton = 3;

// Inicializando variáveis que serão necessárias, sendo o ângulo que o motor está atualmente, o ângulo que ela vai mover e o número de passos para tanto

int currentAngle = 0;

// Aqui você varia o número de ângulo que será usado no exemplo, ou seja, o tanto que ele vai variar a cada toque no botão
int angle = 45;

int numstep;

// Angulo do Step no Proteus é 90, logo, são necessários 90 / 1.8 = 50 steps para girar 90 Graus
// Angulo total a ser considerado é 360, logo, são necessários 360 / 1.8 = 200 steps para girar todo o eixo
// O valor do stepPerAngle está no proteus, ele pode ser alterado porém vamos deixar 1.8 devido ao sketch utilizar 200 SPR
float stepPerAngle = 1.8; 


void setup() {

  Serial.begin(9600);

  // Setando os pinos de saída

  pinMode(PinButton, INPUT);

}

void loop() {

    int times_pressed = 0;

    // lendo se o botão tá ligado ou não, se sim ele recebe True, se não ele recebe False
    bool button_pressed = digitalRead(PinButton);
    
    if (button_pressed == true){
      // Ligando o led para debug
      digitalWrite(PinLed, HIGH);
      delay(300);
      digitalWrite(PinLed, LOW);
      delay(300);
      //Aumentando a variável de teste
      times_pressed++;
    }

    numstep = (angle * times_pressed)/stepPerAngle;
      
    for(int x = 0; x < numstep; x++) {
      Motor.step(1);
      delay(200);
    }
}
