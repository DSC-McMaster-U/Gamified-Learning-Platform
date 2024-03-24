## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them.

<!-- - Python 3.x
- pip (Python package manager) -->
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (available for Windows, Mac, and Linux).
- Alternatively, if using a supported Linux distro, you can install the [Docker Engine](https://docs.docker.com/engine/install/) standalone and [Docker Compose](https://docs.docker.com/compose/install/) plugin instead.

### Installing

A step by step series of examples that tell you how to create and manage the application through a local Docker image.

### Building and Running a Docker Image

First, ensure that you have Docker installed, along with Docker Compose V2. You can check this by running `docker --version` and `docker compose version` respectively to get version-related output for both.

Afterwards, navigate to the root of the project and run:
```bash
docker compose up
```

Upon executing this command for the first time, Docker will package the project within a local image, installing any dependencies needed to run—this can take anywhere from 20 seconds up to a minute. Afterwards, a new container environment will be set up and the packaged application will immediately run in it, starting up a local server at `127.0.0.1:8080`. Note that Docker only needs to compile an image once; subsequent startups of the same image will execute within a matter of seconds.

Some additional things you can do at startup:
- To run an application in the background while freeing up the terminal for other commands, append a `-d` flag to the end of the above command.
- To access an interactive bash shell within the container, run the following:

  ```bash
  docker compose up -d
  docker compose exec web sh
  ```
  This can be useful, in the case you need to execute any Flask shell commands while the server is running (e.g. `cd app; flask --app run_app.py clear-db`). To exit this shell, just run the `exit` command.

### Terminating the Application and Removing the Image
If the server is running directly in a terminal, then simply enter `Ctrl + C` to stop the application and shut down the container.

If the image is being run in the background, then run the following at the root of the project:
```bash
docker compose down
```

In the case that you need to remove any images created by Docker, then first get a list of all currently-existing images with `docker images`. Locate either the repository name or image ID of the image you would like to delete in the generated table, then execute the following, replacing `your-repo-name` or `your-img-id` with your choice of info:
```bash
docker rmi -f <your-repo-name | your-img-id>
```

Alternatively, if you would like to clean up all unused Docker resources on your system (containers, images, networks, and caches), run the command below at your own discretion:
```bash
docker system prune -a
```
