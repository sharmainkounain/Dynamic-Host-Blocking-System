import json
import threading
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

        controller = self

        class APIHandler(BaseHTTPRequestHandler):

            def do_POST(self):
                try:
                    length = int(self.headers.get("Content-Length", 0))
                    data = json.loads(self.rfile.read(length).decode())

                    ip = data.get("ip")

                    if not ip:
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(b"Missing IP address")
                        return

                    if self.path == "/block":
                        controller.block_ip(ip)
                        message = f"Blocked {ip}"

                    elif self.path == "/unblock":
                        controller.unblock_ip(ip)
                        message = f"Unblocked {ip}"

                    else:
                        self.send_response(404)
                        self.end_headers()
                        return

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps({"message": message}).encode()
                    )

                except Exception as error:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(error).encode())

            def log_message(self, format, *args):
                return

        server = HTTPServer(("0.0.0.0", 8080), APIHandler)

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True
        )
        thread.start()

        self.logger.info("HTTP API running on port 8080")

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

        match = parser.OFPMatch()

        actions = [
            parser.OFPActionOutput(
                ofproto.OFPP_CONTROLLER,
                ofproto.OFPCML_NO_BUFFER
            )
        ]

        self.add_flow(datapath, 0, match, actions)

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

        actions = [
            parser.OFPActionOutput(out_port)
        ]

        if out_port != ofproto.OFPP_FLOOD:

            match = parser.OFPMatch(
                in_port=in_port,
                eth_src=src,
                eth_dst=dst
            )

            self.add_flow(
                datapath,
                1,
                match,
                actions
            )

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

        self.blocked_ips.add(ip)

        for datapath in self.datapaths.values():

            parser = datapath.ofproto_parser

            match = parser.OFPMatch(
                eth_type=0x0800,
                ipv4_src=ip
            )

            flow_mod = parser.OFPFlowMod(
                datapath=datapath,
                priority=100,
                match=match,
                instructions=[]
            )

            datapath.send_msg(flow_mod)

        self.logger.info("BLOCKED IP: %s", ip)

    def unblock_ip(self, ip):

        self.blocked_ips.discard(ip)

        for datapath in self.datapaths.values():

            parser = datapath.ofproto_parser
            ofproto = datapath.ofproto

            match = parser.OFPMatch(
                eth_type=0x0800,
                ipv4_src=ip
            )

            flow_mod = parser.OFPFlowMod(
                datapath=datapath,
                command=ofproto.OFPFC_DELETE,
                out_port=ofproto.OFPP_ANY,
                out_group=ofproto.OFPG_ANY,
                match=match
            )

            datapath.send_msg(flow_mod)

        self.logger.info("UNBLOCKED IP: %s", ip)
