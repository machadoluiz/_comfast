#include <ESP8266WiFi.h>
#include "ThingSpeak.h"
#include <Servo.h>
#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define SERVO_DIGITAL_PIN D1
#define DHT11_DIGITAL_PIN D2
#define MQ4_ANALOG_PIN A0
#define MQ4_DIGITAL_PIN D3
#define DS18B20_DIGITAL_PIN D4

const char *rede_ssid = "Wi-Fi 2.4GHz";
const char *rede_senha = "senhadowifi";

unsigned long thingspeak_canal_id = 1922930;
const char *thingspeak_chave_escrita = "****************";

unsigned long sensores_tempo_anterior = 0;
const long sensores_tempo_intervalo = 5 * 60000;

float mq4_valor_analogico = 0.0;

WiFiClient client;

Servo servo;

DHT dht11(DHT11_DIGITAL_PIN, DHT11);

OneWire oneWire(DS18B20_DIGITAL_PIN);
DallasTemperature ds18b20(&oneWire);

void conectaWiFi() {
    Serial.print("[INFO] Estabelecendo conexao com a rede ");
    Serial.print(rede_ssid);

    WiFi.begin(rede_ssid, rede_senha);

    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(500);
    }

    Serial.println();

    Serial.println("[INFO] Conectado com sucesso!");

    Serial.print("[INFO] Endereco de IP: ");
    Serial.println(WiFi.localIP());
}

void iniciaServo() {
    Serial.println("[SERVO] Inicializando a rotacao anti-horaria..");
    for (int pos = 180; pos >= 0; pos -= 1) {
        servo.write(pos);
        delay(100);
    }

    Serial.println("[SERVO] Inicializando a rotacao horaria..");
    for (int pos = 0; pos <= 180; pos += 1) {
        servo.write(pos);
        delay(100);
    }
}

float obtemTemperaturaInterna() {
    ds18b20.requestTemperatures();
    return ds18b20.getTempCByIndex(0);
}

void enviaInformacoesThingSpeak(int thingspeak_field, char *sensor_nome, char *sensor_parametro, float sensor_valor) {
    int status_HTTP = ThingSpeak.writeField(thingspeak_canal_id, thingspeak_field, sensor_valor, thingspeak_chave_escrita);

    Serial.print("[");
    Serial.print(sensor_nome);
    Serial.print("] ");
    Serial.print(sensor_parametro);
    Serial.print(": ");
    Serial.println(sensor_valor);

    delay(2000);

    if (status_HTTP == 200) {
        Serial.println("[INFO] Canal atualizado com sucesso!");
    } else {
        Serial.println("[ERRO] Ocorreu um problema na atualizacao do canal!");

        Serial.print("[ERRO] Resposta HTTP: ");
        Serial.println(status_HTTP);
    }

    delay(20000);
}

void setup() {
    Serial.begin(115200);
    delay(5000);

    Serial.println("\n[INFO] Inicializando o sistema!");

    conectaWiFi();
    ThingSpeak.begin(client);

    // Inicializa o servo
    servo.attach(SERVO_DIGITAL_PIN);
    servo.write(180);

    // Inicializa os sensores
    dht11.begin();
    ds18b20.begin();

    Serial.println("[INFO] Aguarde...");
    delay(10000);
}

void loop() {
    unsigned long sensores_tempo_atual = millis();

    if (sensores_tempo_atual - sensores_tempo_anterior >= sensores_tempo_intervalo) {
        sensores_tempo_anterior = sensores_tempo_atual;

        servo.write(180);

        enviaInformacoesThingSpeak(1, "DHT11", "Temperatura", dht11.readTemperature());
        enviaInformacoesThingSpeak(2, "DHT11", "Umidade", dht11.readHumidity());

        mq4_valor_analogico = analogRead(MQ4_ANALOG_PIN);
        enviaInformacoesThingSpeak(3, "MQ4", "[ANALOG] Gas", mq4_valor_analogico);
        enviaInformacoesThingSpeak(4, "MQ4", "[DIGIT] Gas", digitalRead(MQ4_DIGITAL_PIN));

        enviaInformacoesThingSpeak(5, "DS18B20", "Temperatura", obtemTemperaturaInterna());
    }

    if (mq4_valor_analogico >= 200.0) {
        iniciaServo();
    }
}
