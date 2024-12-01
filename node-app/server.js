const express = require('express');
const app = express();

app.get('/api/node', (req, res) => {
  res.send('Hello, World from Node.js!');
});

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
