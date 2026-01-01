# LYNKS Test Client (Windows GStreamer)
This is a simple test client for Lynks Safe Connections that:
* Logs in to the Lynks backend (/login)
* Creates a VideoRoom (/create)
* Publishes audio/video to Janus (VideoRoom)
* Optionally subscribes to other participants’ feeds

The client is built using Python + PyGObject (gi) + GStreamer and is intended to run on Windows using MSYS2 (MinGW64).

>⚠️ MSYS2 is required.
On Windows, PyGObject and GStreamer bindings are only reliable when run from MSYS2’s MinGW Python, not from the standard CPython installer.

---

# Requirements

* Windows
* MSYS2 (MinGW64)
* PowerShell
* Lynks backend stack running (Janus + Lynks + MySQL via Docker)

---

## 1) Install MSYS2

Install MSYS2 and make sure you have the MinGW64 environment available.

Default installation path used by the project:

`C:\dev\msys64`

You can find it here on their website: https://www.msys2.org/

> **Note:** If MSYS2 is installed elsewhere, update the path inside the setup script.

---

## 2) Run the setup script (GStreamer + Python bindings)

The project includes a PowerShell script: `setup-gst-env.ps1`.

This script will:
* Update MSYS2 and pacman
* Install GStreamer, plugins, PyGObject, and related dependencies
* Create a Python virtual environment using MSYS2’s MinGW Python
* Enable --system-site-packages so gi bindings are available
* Export required runtime environment variables
* Run diagnostics to verify everything works 

Run it from the project root in PowerShell:

`.\setup-gst-env.ps1`


If PowerShell blocks the script due to execution policy:
```ps
-ExecutionPolicy Bypass -File .\setup-gst-env.ps1
```

When finished, the following checks should succeed:
```
import gi

from gi.repository import Gst

gst-launch-1.0 --version
```

---

## 3) Activate the virtual environment and run the client

For subsequent runs, you only need to activate the venv and start the client:

.\.venv\bin\activate.ps1
python .\main.py


> ⚠️ **Important:**
Make sure you are running the Python from .venv, which is based on MSYS2 MinGW Python.
Running the script with a different Python interpreter will likely cause crashes or missing bindings.

You can verify which Python is in use with:

```shell
    python -c "import sys; print(sys.executable)"
```

---

## 4) Configuration

### Backend endpoints
The client uses constants defined in CommonDefines, such as:
* `HOST_MACHINE_IP` = The IP address where the servers reside. *This assumes both the `janus` AND the `lynks` server 
reside on the same IP*
* `JANUS_WEBSOCKET_PORT` = Port address for the janus websocket (`8188` by standard configurations)
* `LYNKS_HTTP_PORT` = Port address for the `Lynks` http server (`60000` by standard configurations)

Ensure these match your Docker-exposed ports and hostnames (e.g. localhost).

---

# Start the client
To start the client, ensure that the virtual environment is running and configured as described in [`Requirements`](#requirements).

---

## Publish / Subscribe mode
The client can operate in publish-only mode or in publish-and-subscribe mode.

By default, the client will only publish data to the specified endpoint.
If the **-sub** flag is provided, the client will also subscribe to other publishers in the same room.

* **List available commands**
  ```shell
  python main.py -h
  ```
* **Create room** *(publish only)*
  ```shell
  python main.py -create
  ```

* **Create room** *(publish-and-subscribe)*
  ```shell
  python main.py -create -sub
  ```

* **Join room** *(publish only)*
  ```shell
  python main.py -join <ROOM_ID>
  ```

* **Join room** *(publish-and-subscribe)*
  ```shell
    python main.py -join <ROOM_ID> -sub
    ```

> **Attention:** The -create or -join flag is mandatory, as the program will not start if it doesn't connect to
> a room.
---

## Flags
The following flags are available for running the client in the CLI.

| Flag   	                      | Description  	                                           |
|-------------------------------|----------------------------------------------------------|
| -create, -c   	               | Creates a new room and publishes to it      	            |
| -join <ROOM_ID>, -j <ROOM_ID> | Joins the room with <ROOM_ID> and published to it      	 |
| -sub, -s   	                  | Subscribes to all publishing streams in the room      	  |
| --help, -h   	                | List available commands      	                           |

---

## Typical client flow

1. Start the backend stack (docker compose up)
2. Start the GLib main loop
3. Log in to Lynks and receive a session token
4. Create a VideoRoom and receive a room_id
5. Publish media to Janus
6. Poll /list_participants and subscribe to newly discovered feeds

---

## Troubleshooting
Common things to check:

* Are you running the correct Python?
    ```shell
    python -c "import sys; print(sys.executable)"
    ```

* Is C:\dev\msys64\mingw64\bin early in your PATH?

* Does this work in the same terminal?
    ```shell
    python -c "import gi; gi.require_version('Gst','1.0'); from gi.repository import Gst; Gst.init(None); print(Gst.version_string())"
    ```

* Enable GStreamer debug logging:
    ```shell
    $env:GST_DEBUG="2"
    ```

Most crashes happen when the script is run with a Python interpreter not compatible with MSYS2’s GStreamer build.

---

## Project structure (high level)
* Network/GStreamer/ – GLib main loop and base GStreamer pipeline logic
* Network/Janus/ – Janus VideoRoom publisher/subscriber pipelines
* Network/Lynks/ – REST communication with Lynks backend
* main.py – example entry point demonstrating login, room creation, and subscription polling