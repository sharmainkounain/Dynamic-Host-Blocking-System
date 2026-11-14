# Person 3 – SDN Controller & Dynamic Host Blocking

This folder contains the SDN controller implementation developed for the Dynamic Host Blocking System project.

## Files

- `controller.py` – Original SDN controller implementation.
- `controller_backup.py` – Backup of the original controller.
- `controller_v2.py` – Upgraded controller with blocking, unblocking, blocklist, flow statistics and event logging.
- `events.log` – Controller event log generated during testing.

## Technologies

- Python
- OS-Ken
- OpenFlow 1.3
- Open vSwitch
- Mininet
- Docker

## HTTP API

- `POST /block` – Block a specified IP address.
- `POST /unblock` – Unblock a specified IP address.
- `GET /blocklist` – Retrieve blocked IP addresses.
- `GET /stats` – Retrieve switch flow statistics.
