var express = require('express');
var app = express();
var path=require('path');

app.use(express.static('public'));

app.get('/', function (req, res) {
    res.sendFile(path.join(__dirname) + "/" + "index.html" );
})

app.get('/confirm', function (req, res) {
    res.sendFile(path.join(__dirname) + "/" + "confirm.html" );
})
const PORT=process.env.PORT || 8080;
app.listen(PORT,_ => {
    console.log(`App deployed at Port ${PORT}`)
})