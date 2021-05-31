# FlyFlix

This repository is a supplement to our preprint [An inexpensive, high-precision, modular spherical treadmill setup optimized for *Drosophila* experiments](https://doi.org/10.1101/2021.04.29.442008).

## Architecture

FlyFlix is a web application that runs in most modern web browsers. While the server component is written in python-3 and requires a computer to run, the client is implemented in JavaScript inside an HTML website. Browsers that access the server receive the client code as part of the website. Through a bidirectional communication server and client exchange status information. Consequently, several clients can connect to the same server.

## Server


