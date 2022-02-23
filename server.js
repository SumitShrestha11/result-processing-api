const path = require('path');
const express = require('express');
const fileUpload = require('express-fileupload');
const bodyParser = require('body-parser');
var cors = require('cors');
const dummyResponse = require('./test.json');
const db = require('./db/queries');



const app = express();

app.use(express.static("public"));

app.use(bodyParser.json())
app.use(
  bodyParser.urlencoded({
    extended: true,
  })
)

app.use(cors());
app.use(fileUpload());

app.get('/',(req,res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
})

app.get('/script-test', (req,res) => {
  let spawn = require("child_process").spawn;

  let process = spawn('python',["./segmentation.py"] );

  let resultString = '';

  process.stdout.on('data', (data) => {
    resultString += data.toString();
    //res.json(resultString);
    res.json(JSON.parse(resultString));

})


})

// Upload Endpoint
app.post('/upload', (req, res) => {
  if (req.files === null) {
    return res.status(400).json({ msg: 'No file uploaded' });
  }

  const file = req.files.file;

  file.mv(`${__dirname}/uploads/result.${file.name.split('.')[1]}`, err => {
    if (err) {
      console.error(err);
      return res.status(500).send(err);
    }

    //res.json({ fileName: file.name, filePath: `/uploads/${file.name}` });
    let spawn = require("child_process").spawn;

    let process = spawn('python',["./segmentation.py"] );

    let resultString = '';

    process.stdout.on('data', (data) => {
      resultString += data.toString();
      //res.json(resultString);
      res.json(JSON.parse(resultString));

    })
  });
});

//Confirm Endpoint
app.post('/confirm', db.insertData);

app.get('/allData', db.showData);

app.listen(5000, () => console.log('Server Started...'));