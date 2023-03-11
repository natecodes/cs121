// @ts-check
"use strict"

const { PythonShell } = require('python-shell')
const { spawn } = require('child_process');

const pyProg = spawn('python', ['test.py']);
pyProg.stdout.on('data', function(data) {
    console.log(data.toString());
});


// let testshell = new PythonShell('test.py')
// testshell.on('message', function (message) {
//     console.log(message)
// })
//
// await testshell
//
// // setTimeout(() => {
// //     pyshell.send("Another Hello");
// // }, 3000);
// const end = () => {
//     pyshell.end(function (err, code, signal) {
//         if (err) throw err;
//         console.log("finished");
//     });
// };
//
// // let pyshell = new PythonShell('../cs121/assignment3/search.py', {mode: 'text', pythonOptions: ['-u']})
// //
// // pyshell.send('hi')
// //
// // pyshell.on('message', function (message) {
// //     console.log(message)
// // })
//
console.log('hi')
