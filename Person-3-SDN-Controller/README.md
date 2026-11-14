# Person 3 – SDN Controller & Dynamic Host Blocking

This folder contains the SDN controller implementation developed for the Dynamic Host Blocking System project.

## 1. Project Overview

This component implements an SDN-based dynamic host blocking mechanism using OS-Ken, OpenFlow 1.3 and Open vSwitch.

The controller receives IP addresses through an HTTP API and installs OpenFlow DROP rules to block traffic originating from selected hosts. It also supports unblocking, blocklist retrieval, flow statistics and event logging.

## 2. Files

- `controller.py` – Original SDN controller implementation.
- `controller_backup.py` – Backup of the original controller.
- `controller_v2.py` – Upgraded controller with blocking, unblocking, blocklist management, flow statistics and event logging.
- `events.log` – Controller event log generated during testing.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Controller implementation |
| OS-Ken | SDN controller framework |
| OpenFlow 1.3 | Controller-switch communication |
| Open vSwitch | Software-based network switch |
| Mininet | Network emulation |
| Docker | Controller execution environment |
| Ubuntu | Development and testing environment |

## 4. Controller Architecture

The controller communicates with the Open vSwitch instance using OpenFlow 1.3.

Its main responsibilities include:

- Learning host MAC addresses and associated switch ports.
- Forwarding packets using learned MAC-to-port mappings.
- Receiving HTTP requests for blocking and unblocking IP addresses.
- Installing high-priority DROP flow rules.
- Removing blocking rules when an IP address is unblocked.
- Maintaining an in-memory blocklist.
- Requesting and collecting switch flow statistics.
- Recording controller events in a log file.

## 5. HTTP API

The controller exposes an HTTP API on port `8080`.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/block` | Blocks a specified IP address |
| POST | `/unblock` | Removes the blocking rule for an IP address |
| GET | `/blocklist` | Retrieves currently blocked IP addresses |
| GET | `/stats` | Requests and retrieves switch flow statistics |

### Example Requests

**Block an IP address**

```json
{
  "ip": "10.0.0.2"
}
```

Send as a POST request to:

```text
http://<controller-ip>:8080/block
```

**Unblock an IP address**

```json
{
  "ip": "10.0.0.2"
}
```

Send as a POST request to:

```text
http://<controller-ip>:8080/unblock
```

**Retrieve the blocklist**

```text
GET /blocklist
```

**Retrieve flow statistics**

```text
GET /stats
```

## 6. Mininet Network Topology

The network was emulated using Mininet with three hosts connected to one Open vSwitch instance.

```text
              OS-Ken Controller
                      |
                OpenFlow 1.3
                      |
                Open vSwitch
                     s1
                /     |     \
               /      |      \
              h1      h2      h3
           10.0.0.1 10.0.0.2 10.0.0.3
```

### Host Addressing

| Host | IP Address |
|---|---|
| h1 | 10.0.0.1 |
| h2 | 10.0.0.2 |
| h3 | 10.0.0.3 |

## 7. Dynamic Blocking Mechanism

The controller installs a high-priority OpenFlow rule matching IPv4 traffic with the specified source IP address.

The rule uses an empty instruction list, causing matching packets to be dropped.

The controller uses:

- Priority 100 for blocking rules.
- Priority 1 for learned forwarding rules.
- Priority 0 for the table-miss rule.

When an unblock request is received, the corresponding blocking rule is deleted.

## 8. Testing and Verification

The following operations were successfully tested:

| Test | Observed Result |
|---|---|
| Initial host connectivity | Successful |
| Block 10.0.0.2 | Blocking request successful |
| h1 to h2 after blocking | 100% packet loss |
| h1 to h3 after blocking h2 | Communication successful |
| Unblock 10.0.0.2 | Unblocking request successful |
| h1 to h2 after unblocking | Communication restored |
| Blocklist API | Returned blocked IP addresses |
| Flow statistics API | Returned switch flow statistics |
| Event logging | Controller events recorded |

These tests demonstrate that the controller can dynamically install and remove blocking rules while preserving communication with other hosts.

## 9. Integration with Other Components

This component is designed to work with the traffic monitoring and detection modules developed by the other team members.

- Person 1 provides TCP traffic monitoring information.
- Person 2 identifies suspicious host IP candidates.
- Person 3 uses the SDN controller to block or unblock selected IP addresses.

The suspicious IP handoff is currently manual. Automatic integration between the detection module and controller has not yet been demonstrated.

## 10. Limitations

- The blocklist is maintained in memory and is not persistent across controller restarts.
- Blocking rules are not automatically reinstalled when a switch reconnects.
- The HTTP API does not currently implement authentication.
- The current detection-to-controller handoff is manual.

## 11. Future Enhancements

- Automate the handoff of suspicious IP addresses to the controller.
- Persist blocked IP addresses across restarts.
- Automatically reinstall blocking rules after switch reconnection.
- Introduce authentication and API access control.
- Develop a dashboard for real-time monitoring of blocked hosts and flow statistics.

## 12. Team Contribution

**Sayar Mitra – SDN Controller and Dynamic Host Blocking**

