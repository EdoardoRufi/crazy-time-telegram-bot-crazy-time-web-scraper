package edoardo.rufi.service;

import org.eclipse.paho.client.mqttv3.*;
import org.eclipse.paho.client.mqttv3.persist.MqttDefaultFilePersistence;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Service;

import java.sql.Timestamp;
import java.util.UUID;

@Service
public class MqttClientService {

    @Value("${mqtt.brokerUrl}")
    private String brokerUrl;

    //    @Value("${mqtt.clientId}")
    private final String clientId = UUID.randomUUID().toString();

    @Value("${mqtt.lastExtraction.topicName}")
    private String topicName;

//    @Value("${mqtt.username}")
//    private String username;
//
//    @Value("${mqtt.password}")
//    private String password;

    @Bean
    public MqttClient mqttClient() throws Exception {
        MqttConnectOptions options = new MqttConnectOptions();
        options.setCleanSession(true);
        options.setAutomaticReconnect(true);
        options.setConnectionTimeout(10);
//        options.setUserName(username);
//        options.setPassword(password.toCharArray());

        MqttClient client = new MqttClient(brokerUrl, clientId, new MqttDefaultFilePersistence("/tmp"));

        client.connect(options);

        System.out.println("start prova");

        client.setCallback(new MqttCallback() {

            public void messageArrived(String topic, MqttMessage message) throws Exception {
                String time = new Timestamp(System.currentTimeMillis()).toString();
                System.out.println("\nReceived a Message!" +
                        "\n\tTime:    " + time +
                        "\n\tTopic:   " + topic +
                        "\n\tMessage: " + new String(message.getPayload()) +
                        "\n\tQoS:     " + message.getQos() + "\n");
            }

            public void connectionLost(Throwable cause) {
                System.out.println("Connection to Solace broker lost!" + cause.getMessage());
            }

            public void deliveryComplete(IMqttDeliveryToken token) {
            }

        });

        client.subscribe(topicName);

        return client;
    }
}
