import json
import threading
import ipaddress
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import (
    CONFIG_DISPATCHER,
    MAIN_DISPATCHER,
    set_ev_cls
)
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet, ethernet
from os_ken.lib.packet import ether_types


class SDNController(app_manager.OSKenApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SDNController, self).__init__(*args, **kwargs)

        self.mac_to_port = {}
        self.datapaths = {}
        self.blocked_ips = set()
        self.flow_stats = {}
        self.stats_lock = threading.Lock()

        controller = self

        class APIHandler(BaseHTTPRequestHandler):

            def send_json(self, status, data):
                body = json.dumps(data).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):

                if self.path == "/blocklist":
                    self.send_json(200, {
                        "blocked_ips": sorted(controller.blocked_ips)
                    })

                elif self.path == "/stats":
                    controller.request_flow_stats()

                    import time
                    time.sleep(0.5)

                    with controller.stats_lock:
                        stats = dict(controller.flow_stats)

                    self.send_json(200, {
                        "flow_statistics": stats
                    })

                else:
                    self.send_json(404, {"error": "Not found"})

            def do_POST(self):

                try:
                    length = int(self.headers.get("Content-Length", 0))
                    data = json.loads(self.rfile.read(length).decode())

                    ip = str(ipaddress.ip_address(data.get("ip", "")))

                    if self.path == "/block":
                        controller.block_ip(ip)
                        message = "Blocked " + ip

                    elif self.path == "/unblock":
                        controller.unblock_ip(ip)
                        message = "Unblocked " + ip

                    else:
                        self.send_json(404, {"error": "Not found"})
                        return

                    self.send_json(200, {"message": message})

                except ValueError:
                    self.send_json(400, {"error": "Invalid IP address"})

                except Exception as error:
                    self.send_json(500, {"error": str(error)})

            def log_message(self, format, *args):
                return

        server = HTTPServer(("0.0.0.0", 8080), APIHandler)

        threading.Thread(
            target=server.serve_forever,
            daemon=True
        ).start()

        self.logger.info("HTTP API running on port 8080")

    def log_event(self, action, ip):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = f"[{timestamp}] {action} {ip}\n"

        with open("/opt/sdn/events.log", "a") as file:
            file.write(entry)

        self.logger.info(entry.strip())

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        instructions = [
            parser.OFPInstructionActions(
                ofproto.OFPIT_APPLY_ACTIONS,
                actions
            )
        ]

        flow_mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=instructions
        )

        datapath.send_msg(flow_mod)

    @set_ev_cls(
        ofp_event.EventOFPSwitchFeatures,
        CONFIG_DISPATCHER
    )
    def switch_features_handler(self, ev):

        datapath = ev.msg.datapath
        self.datapaths[datapath.id] = datapath

        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        actions = [
            parser.OFPActionOutput(
                ofproto.OFPP_CONTROLLER,
                ofproto.OFPCML_NO_BUFFER
            )
        ]

        self.add_flow(
            datapath,
            0,
            parser.OFPMatch(),
            actions
        )

        self.logger.info("Switch %s connected", datapath.id)

    @set_ev_cls(
        ofp_event.EventOFPPacketIn,
        MAIN_DISPATCHER
    )
    def packet_in_handler(self, ev):

        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        in_port = msg.match["in_port"]

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth is None:
            return

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        src = eth.src
        dst = eth.dst
        dpid = datapath.id

        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        out_port = self.mac_to_port[dpid].get(
            dst,
            ofproto.OFPP_FLOOD
        )

        actions = [parser.OFPActionOutput(out_port)]

        if out_port != ofproto.OFPP_FLOOD:

            match = parser.OFPMatch(
                in_port=in_port,
                eth_src=src,
                eth_dst=dst
            )

            self.add_flow(datapath, 1, match, actions)

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=(
                msg.data
                if msg.buffer_id == ofproto.OFP_NO_BUFFER
                else None
            )
        )

        datapath.send_msg(out)

    def block_ip(self, ip):

        if ip in self.blocked_ips:
            return

        self.blocked_ips.add(ip)

        for datapath in self.datapaths.values():

            match = datapath.ofproto_parser.OFPMatch(
                eth_type=0x0800,
                ipv4_src=ip
            )

            datapath.send_msg(
                datapath.ofproto_parser.OFPFlowMod(
                    datapath=datapath,
                    priority=100,
                    match=match,
                    instructions=[]
                )
            )

        self.log_event("BLOCKED", ip)

    def unblock_ip(self, ip):

        if ip not in self.blocked_ips:
            return

        self.blocked_ips.remove(ip)

        for datapath in self.datapaths.values():

            parser = datapath.ofproto_parser
            ofproto = datapath.ofproto

            match = parser.OFPMatch(
                eth_type=0x0800,
                ipv4_src=ip
            )

            datapath.send_msg(
                parser.OFPFlowMod(
                    datapath=datapath,
                    command=ofproto.OFPFC_DELETE,
                    out_port=ofproto.OFPP_ANY,
                    out_group=ofproto.OFPG_ANY,
                    match=match
                )
            )

        self.log_event("UNBLOCKED", ip)

    @set_ev_cls(
        ofp_event.EventOFPFlowStatsReply,
        MAIN_DISPATCHER
    )
    def flow_stats_reply_handler(self, ev):

        datapath = ev.msg.datapath

        with self.stats_lock:
            self.flow_stats[str(datapath.id)] = [
                {
                    "priority": flow.priority,
                    "packets": flow.packet_count,
                    "bytes": flow.byte_count,
                    "match": str(flow.match),
                    "instructions": str(flow.instructions)
                }
                for flow in ev.msg.body
            ]

    def request_flow_stats(self):

        for datapath in self.datapaths.values():

            parser = datapath.ofproto_parser

            request = parser.OFPFlowStatsRequest(
                datapath,
                0
            )

            datapath.send_msg(request)
