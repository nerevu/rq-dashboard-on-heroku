# ClozeCart
An API that connects Cloze and OpenCart for the Alegna Company.

## API Usage

1. Create and activate a virtual environment:

    `Mac`
    ```bash
    virtualenv env
    source env/bin/activate
    ```
    `Linux`
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    `Windows`
    ```bash
    virtualenv env
     ./env/Scripts/activate
    ```

2. Install requirements::

    ```bash
    pip install -r requirements.txt
    ```

3. Run the application with Ngrok for https tunneling:

    ```bash
    manage -m Ngrok serve
    ```
    This code may break at first if some needed packages were not properly installed. Look at the error in the console to determine what packages need installed, and `pip install` them individually. After each `pip install` you can run `manage -m Ngrok serve` again to see if there are any more packages that need installed. If not, the app should start running.

4. Start Ngrok in a different terminal
    - After joining Reuben's paid account, follow the instructions [here](https://dashboard.ngrok.com/get-started) to setup ngrok
    - Run the code below to start tunneling from localhost:5000 to https://nerevu.ngrok.io
        ```bash
        {path/to/ngrok}/ngrok http 5000 -subdomain=nerevu
        (e.g. ~/Desktop/code/ngrok http 5000 -subdomain=nerevu)
        ```
        - If it does not bring up `Forwarding https://nerevu.ngrok.io -> http://localhost:5000` in your terminal after 15 seconds, that stinks and good luck.
    - Go to `https://nerevu.ngrok.io/v1`

5. Open the API at https://nerevu.ngrok.io/v1

6. If you are contributing to this repo, install dev-requirements::

```bash
pip install -r dev-requirements.txt
```

## Cloze API Docs
- https://www.cloze.com/api-docs/



## Notes

- To disable route caching, set [config.py#L67](https://github.com/nerevu/commissioner/blob/6feb4945e2971fc5bf949b33fe7edfa124d7c218/config.py#L67) to `ROUTE_TIMEOUT = get_seconds(0)`

## Configuration

Environment Variable | Description
---------------------|------------

Create your own `.env` file in the root of your project. We use python-dotenv to manage environment variables in the `.env` file.
