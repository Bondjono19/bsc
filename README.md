# Integrable access control system utilizing deep neural networks for face recognition designed for resource limited edge devices without acceleration components

## Setup & Deployment - Production
This setup is intended for running the system as intended: on an edge-device with continuous deployment.  
Setup assumes linux-based host operating system with docker installation present on device.


### Bootstrapping
1. SSH into the target device.
2. Ensure Docker is installed and camera is attached.
3. Copy the `deploy/docker-compose.yml` file onto the device.
4. Copy the `.env.example` file onto the device and rename it .env and fill it out with your own secrets and configurations.
5. Run 'crobtab -e' and insert a new line like: 
```
     */5 * * * * (cd /dirpath/to/your/deploy && /usr/bin/docker compose -f docker-compose.yml pull && /usr/bin/docker compose -f docker-compose.yml up -d) >> /path/to/log/deploy.log 2>&1
```  
5. (cont.) Ensure docker executable is in the same path. This command sets up a cron job which at 5 minute intervals ensures it has the latest version, and if not, pulls the latest.


### Adding an integration
There are two options for this. 
1. Fork the repository and add your own implementation and set up your own pipeline.
2. Or copy your AccessGrantor implementation to the container when running the system by adding it as a volume for instance:
```
services:
    ...
    recognition
        ...
        volumes:
            - path/to/my/implementation/:/app/recognition/grantors/
        ...
    ...
```
2. (cont.) Remember to change the environment variable `ACCESS_GRANTOR` to the full module path of the implementation.

### TLS Support
To enable TLS support, extend the command for the `API`-service, such that the full command is the following:  
```
    command: ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000","--ssl-certfile","/certs/cert.pem","--ssl-keyfile", "/certs/key.pem"]
```
And make sure to attach the your certs folder to the container:
```
services:
    api:
        ...
        volumes:
            - ./certs:/certs:ro
        ...
    ...
```
Addtionally, to enable TLS for the event broker, set 'ENABLE_TLS_REDIS=True' and make sure to attach a volume to the `Recognition`-service. The cert must be name `broker_cert.pem`:
```
services:
    api:
        ...
        volumes:
            - ./certs:/certs:ro
        ...
    ...
```
