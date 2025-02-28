# Setting Up the Project

Follow these steps to download and set up the project from GitHub, create a virtual environment, install dependencies, and run the script.

## 1. Clone the GitHub Repository

First, clone the repository to your local machine. Open a terminal (Command Prompt, PowerShell, or Bash), and run the following command:

```bash
git clone https://github.com/Maveronic/polymarket-mock.git
```
## 2. Navigate into the project directory

After cloning the repository, change into the project directory:

```bash
cd polymarket-mock.git
```

## 3. Create a Virtual Environment

On Windows:

Run the following command to create a virtual environment:

```bash
python -m venv venv
```
On Unix-based systems (Linux/MacOS):

Run this command to create a virtual environment:

```bash
python3 -m venv venv
```

## 4. Activate the Virtual Environment
On Windows:

Activate the virtual environment using:

```bash
venv\Scripts\activate
```
On Unix-based systems (Linux/MacOS):

Activate the virtual environment using:

```bash
source venv/bin/activate
```

Once activated, you should see (venv) at the beginning of your terminal prompt, indicating that the virtual environment is active.

## 7. Navigate into the prediction_market directory
```bash
cd prediction_market
```

## 8. Run the server
To start the server, run the following command:
On Windows:

Use the following command:

```bash
python manage.py runserver
```

On Unix-based systems (Linux/MacOS):

Use the following command:

```bash
python3 manager.py runserver
```

## 9. Check out the API Documentation
Check out the API documentation at:
```bash
localhost:8000/api/docs/
```
or
```bash
localhost:8000/api/redoc/
```
