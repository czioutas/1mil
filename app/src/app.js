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

app.post('/load-test', async (req, res) => {
  const { numberOfMessages = 100000, organizationIds = [1, 2, 3] } = req.body;
  const batchSize = 1000; // Increased batch size for better throughput
  const results = {
    total: numberOfMessages,
    successful: 0,
    failed: 0,
    startTime: new Date(),
    endTime: null,
    throughput: 0,
    errors: []
  };

  // Send initial response
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
  });

  try {
    for (let i = 0; i < numberOfMessages; i += batchSize) {
      const batch = [];
      const currentBatchSize = Math.min(batchSize, numberOfMessages - i);
      
      for (let j = 0; j < currentBatchSize; j++) {
        const orgId = organizationIds[Math.floor(Math.random() * organizationIds.length)];
        
        batch.push(
          sendToKafka({
            organizationId: orgId,
            value: Math.floor(Math.random() * 1000),
            timestamp: new Date().toISOString()
          }).then(() => {
            results.successful++;
          }).catch((error) => {
            results.failed++;
            results.errors.push(error.message);
          })
        );
      }
      
      await Promise.all(batch);
      
      const progress = {
        processed: i + currentBatchSize,
        total: numberOfMessages,
        successful: results.successful,
        failed: results.failed,
        throughput: Math.floor(results.successful / ((new Date() - results.startTime) / 1000))
      };
      
      res.write(`data: ${JSON.stringify(progress)}\n\n`);
    }

    results.endTime = new Date();
    const durationSeconds = (results.endTime - results.startTime) / 1000;
    results.throughput = Math.floor(results.successful / durationSeconds);
    
    // Send final results
    res.write(`data: ${JSON.stringify({ ...results, complete: true })}\n\n`);
    res.end();
  } catch (error) {
    console.error('Load test error:', error);
    res.write(`data: ${JSON.stringify({ error: error.message, complete: true })}\n\n`);
    res.end();
  }
});

app.listen(3000, () => console.log('Server running on port 3000'));