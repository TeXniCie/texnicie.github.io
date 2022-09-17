var express = require('express')
var serveStatic = require('serve-static')
var http = require("http")
var finalhandler = require("finalhandler")
var fs = require("fs");
var path = require("path");

var app = express()

var serve = serveStatic('.', { index: ['index.html'], extensions: ["html"], redirect: false })

function findTarget(orig) {
    let p = path.join(".", orig);
    let slashStripped = orig.match(/^(.*?)\/?$/)[1];

    if (fs.existsSync(p) && !fs.lstatSync(p).isDirectory())
        return orig;

    //console.log(`Finding suitable target for ${orig}`);
    if (fs.existsSync(p + ".html"))
        return orig + ".html";
    if (fs.existsSync(path.join(p, "index.html")))
        return path.join(orig, "index.html");

    if (fs.existsSync(path.join(".", slashStripped + ".html")))
        return slashStripped + ".html";
    
    return orig;
}

app.use((req, res, next) => {
    //console.log(req.path);
    // req.path = "/index.html";

    //console.log(`Slash stripped: ${req.path.match(/^(.*?)\/$/)[1]}`);
    // console.log(`Slash stripped: ${req.path.match(/^(.*?)\/?$/)[1]}`);

    // let slashStripped = req.path.match(/^(.*?)\/?$/)[1];

    // let p = path.join(".", req.path);

    // if (!fs.existsSync(p) || fs.lstatSync(p).isDirectory()) {
    //     console.log("Finding suitable target");

    //     if (fs.existsSync(p))

    // }

    // console.log([
    //     fs.existsSync(p),
    //     fs.existsSync(p + ".html"),
    //     fs.existsSync(p + "/"),
    //     fs.existsSync(p + "/index.html"),
    //     fs.existsSync(p.match(/^(.*?)\/?$/)[1] + ".html")
    // ]);

    req.url = findTarget(req.path)

    //req.url = "/index.html";
    //console.log(`URL: ${req.url}`);
    next();
});

app.use(serve)

// var server = http.createServer((req, res) => {
//     console.log(req.path);
//     req.path = "/index.html";
//     serve(req, res, finalhandler(req, res));
// });


console.log("Starting");
app.listen(3000)
//server.listen(3000);
console.log("Started");

