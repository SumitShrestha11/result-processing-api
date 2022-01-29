const express = require('express');
const fileUpload = require('express-fileupload');
const bodyParser = require('body-parser');
var cors = require('cors');
const dummyResponse = require('./test.json');
const db = require('./db/queries');

const app = express();

app.use(bodyParser.json())
app.use(
  bodyParser.urlencoded({
    extended: true,
  })
)

app.use(cors());
app.use(fileUpload());

// Upload Endpoint
app.post('/upload', (req, res) => {
  if (req.files === null) {
    return res.status(400).json({ msg: 'No file uploaded' });
  }

  const file = req.files.file;

  file.mv(`${__dirname}/uploads/${file.name}`, err => {
    if (err) {
      console.error(err);
      return res.status(500).send(err);
    }

    //res.json({ fileName: file.name, filePath: `/uploads/${file.name}` });
    res.json(dummyResponse);
  });
});

//Confirm Endpoint
app.post('/confirm', db.insertData);

app.get('/allData', db.showData);

app.listen(5000, () => console.log('Server Started...'));