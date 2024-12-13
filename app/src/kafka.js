const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'emissions-app',
  brokers: [process.env.KAFKA_BROKER],
});

const producer = kafka.producer();

(async () => {
  await producer.connect();
  console.log('Kafka producer connected');
})();

const sendToKafka = async (data) => {
  await producer.send({
    topic: 'emissions',
    messages: [{ value: JSON.stringify(data) }],
  });
};

module.exports = { sendToKafka };
