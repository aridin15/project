const express = require('express');
const app = express();
const axios = require('axios')
const dotenv = require('dotenv').config()

// dotenv.config()

app.get('/api/node', (req, res) => {
  res.send('Hello, World from Node.js!');
});

app.post('/api/fetch',async (req, res)=>{
  console.log('indide api fetch')
  console.log(`process env flask uri is: ${process.env.FLASK_URI}`)
  try {
    const result = await axios.get(process.env.FLASK_URI);
    res.status(200).json({
      data: result.data
    })
  } catch (error){
    res.status(500).json({
      error: error.message
    })
  }
})



app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
