# Integrable access control system utilizing deep neural networks for face recognition designed for resource limited edge devices without acceleration componennts

## Setup
Setup assumes database is set up with identities already.      
Otherwise run the setup with the detection_mode in recognition/recognitionService.py set to false. Not tested thoroughly, some manual code config might be necessary.      

Only tested on Rasberry Pi 4

from root folder run:       
docker compose -f deploy/docker-compose.yml --env-file .env.example up --build

