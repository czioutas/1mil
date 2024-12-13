const express = require('express');
const bodyParser = require('body-parser');
const { sendToKafka } = require('./kafka');
const prisma = require('./database');

const app = express();
app.use(bodyParser.json());

app.post('/emissions', async (req, res) => {
  let { organizationId, value } = req.body;

  organizationId = parseInt(organizationId, 10);
  value = parseInt(value, 10);

  if (!organizationId || !value) {
    return res.status(400).json({ error: 'Missing required fields: organizationId, value' });
  }

  try {
    //  send to Kafka for stream processing
    await sendToKafka({ organizationId, value });

        // should we use flink to store the data?
        const emission = await prisma.emission.create({
          data: {
            organizationId,
            value,
          },
        });
    

    res.status(200).json({ 
      message: 'Emission event processed successfully',
      emission 
    });
  } catch (error) {
    console.error('Error processing emission:', error);
    res.status(500).json({ error: 'Failed to process emission event' });
  }
});

app.listen(3000, () => console.log('Server running on port 3000'));