const express = require('express');
const app = express();
const axios = require('axios')

app.get('/api/node', (req, res) => {
  res.send('Hello, World from Node.js!');
});

app.post('/api/fetch',async (req, res)=>{
  try {
    const result = await axios.get('http://35.236.33.159/api/flask');
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
