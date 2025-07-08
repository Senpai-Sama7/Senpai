"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var express = require("express");
var path = require("path");
var app = express();
var port = parseInt(process.env.PORT) || process.argv[3] || 8080;
app.use(express.static(path.join(__dirname, 'public')))
    .set('views', path.join(__dirname, 'views'))
    .set('view engine', 'ejs');
app.get('/', function (req, res) {
    res.render('index');
});
app.get('/api', function (req, res) {
    res.json({ "msg": "Hello world" });
});
app.listen(port, function () {
    console.log("Listening on http://localhost:".concat(port));
});
//# sourceMappingURL=index.js.map