var express = require('express')
var serveStatic = require('serve-static')

var app = express()

app.use(serveStatic('.', { index: ['index.html'], extensions: ["html"] }))
console.log("Starting");
app.listen(3000)
console.log("Started");

