# README.md

There is a sleeping issue in FIWARE orion-ld context broker.
This application 
* will run into the issue for testing an orion-ld service.
* creates so many entities until the orion-ld context broker can't read entities behind a threshold.
* shows the threshold

for setup the Test-Environment with actual or ne Orion-LD boker
```bash
docker-compose up -d

