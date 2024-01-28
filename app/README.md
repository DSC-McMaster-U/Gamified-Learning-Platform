## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them.

- Python 3.x
- pip (Python package manager)

### Installing

A step by step series of examples that tell you how to get a development env running.

### Setting Up a Virtual Environment

1. **Install the virtual environment**

   First, ensure you have Python3 and pip installed. Then, install `virtualenv` via pip:
   ```bash
   pip install virtualenv
2. **Create a Virtual Environment**

    Navigate to your project directory and run:
   ```bash
   virtualenv venv
   ```
3.  **Activate the Virtual Environment**

    On Windows:
    ```bash
    .\venv\Scripts\activate
    ```
    or try:
    ```bash
    source venv/Scripts/activate
    ```

    On Unix or MacOS:
    ```bash
    source venv/bin/activate
    ```

### Installing Dependencies

Install all dependencies that are required for the project by running:
   ```bash
   pip install -r requirements.txt
   ```
### Running the Application
Once your environment is set up and the dependencies are installed, you can run the application:

   ```bash
   python3 app/run_app.py
   ```

### Terminating the Virtual Environment 
To close the virtual environment simply run the `deactivate` or `exit` command.