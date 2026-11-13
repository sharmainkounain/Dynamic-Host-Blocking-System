# Dynamic Host Blocking System

### An SDN-Based Network Security and Intrusion Detection System

## Overview

The **Dynamic Host Blocking System** is a network security project designed to identify abnormal TCP traffic patterns and dynamically block suspicious hosts using Software-Defined Networking (SDN).

The system monitors network traffic, analyzes connection rates and flow statistics, detects potentially malicious hosts based on predefined thresholds, and updates blocking rules through an SDN controller.

## Objectives

- Generate TCP traffic from multiple network hosts.
- Monitor TCP connection rates and network activity.
- Collect and analyze network flow statistics.
- Define thresholds to identify abnormal traffic patterns.
- Detect and identify suspicious hosts.
- Maintain a dynamic blacklist of suspicious IP addresses.
- Install SDN flow rules to block identified hosts.

## System Workflow

1. **Traffic Generation:** Generate TCP traffic from multiple hosts in a virtual network.
2. **Traffic Monitoring:** Monitor network connections and collect traffic statistics.
3. **Traffic Analysis:** Analyze TCP traffic patterns and connection rates.
4. **Suspicious Host Detection:** Identify hosts exhibiting abnormal traffic behaviour using predefined thresholds.
5. **Dynamic Blacklisting:** Add detected suspicious hosts to a blacklist.
6. **SDN-Based Blocking:** Install flow rules through the SDN controller to block traffic from suspicious hosts.

## Technologies Used

- **Python** – Traffic analysis, detection and socket programming.
- **Mininet** – Virtual network emulation.
- **Software-Defined Networking (SDN)** – Network traffic control and dynamic blocking.
- **TCP/IP** – Network communication and traffic monitoring.
- **Linux / Ubuntu** – Development and execution environment.
- **Git & GitHub** – Version control and collaborative development.

## Expected Outcome

The system aims to detect abnormal TCP traffic patterns, identify suspicious hosts, and dynamically restrict their network access through SDN flow rules.

