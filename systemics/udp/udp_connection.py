# udpconnect
import socket, threading, datetime, json
from typing import Callable, Dict
import asyncio

from .udp_error import UDPConnectionError


class UDPClientProtocol:
    """
    UDPClientProtocol class for managing UDP communication
    """

    def __init__(self, id: str, port: int, 
                 message_handler: Callable[[str, str], None],
                 echo: bool = False,
                 discovery_cue: str = "DISCOVER FROM:",
                 answer_cue: str = "ANSWER FROM:",):
        """
        Initialize the UDPClientProtocol

        :param id: Unique identifier for the client
        :param port: Port number for UDP communication
        :param message_handler: Callback function to handle received messages
        :param echo: Whether to echo the sent messages
        :param discovery_cue: Cue for discovery messages
        :param answer_cue: Cue for answer messages
        """
        self.id = id
        self.port = port
        self.message_handler = message_handler
        self.echo = echo

        self.discovery_cue = discovery_cue
        self.answer_cue = answer_cue
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.port))
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.peers_id_to_ip: Dict[str, str] = {}
        self.peers_ip_to_id: Dict[str, str] = {}

        self.is_running = True
        self.ip = socket.gethostbyname(socket.gethostname())

    def start(self):
        """
        Start the UDP client protocol by initiating the receive_data thread
        """
        threading.Thread(target=self.receive_data, daemon=True).start()

    
    def discovery(self, target_id: str):
        """
        Discover the IP address of a peer by broadcasting a discovery message

        :param target_id: Unique identifier of the target peer
        :return: IP address of the target peer if known
        """
        if target_id in self.peers_id_to_ip:
            return self.peers_id_to_ip[target_id]
        message = f"{self.discovery_cue}{target_id}"
        if self.echo:
            print(f"<Broadcast>\n{message}")
        self.sock.sendto(message.encode(), ('255.255.255.255', self.port))


    async def discovery_with_retries(self, target_id: str, max_count: int = 5):
        """
        Discover the IP address of a peer by broadcasting a discovery message with retries

        :param target_id: Unique identifier of the target peer
        :param max_count: Maximum number of attempts to discover the peer
        :return: IP address of the target peer if known
        """
        for _ in range(max_count):
            if target_id in self.peers_id_to_ip:
                return self.peers_id_to_ip[target_id]
            message = f"{self.discovery_cue}{target_id}"
            if self.echo:
                print(f"<Broadcast>\n{message}\n")
            self.sock.sendto(message.encode(), ('255.255.255.255', self.port))
            await asyncio.sleep(1)


    def send_data(self, message: str, target_id: str = None, target_ip: str = None):
        """
        Send a message to a specific peer

        :param message: Message to send
        :param target_id: Unique identifier of the target peer
        :param target_ip: IP address of the target peer
        """
        if target_id:
            if target_id not in self.peers_id_to_ip:
                raise UDPConnectionError(f"No peer with id {target_id}")
            target_ip = self.peers_id_to_ip.get(target_id)
        elif target_ip:
            pass
        else:
            raise UDPConnectionError("No target specified")
        
        if self.echo:
            print(f"<Me -> {target_id if target_id else target_ip}>\n{message}")
        self.sock.sendto(message.encode(), (target_ip, self.port))


    def receive_data(self):
        """
        Continuously receive data and handle incoming messages
        """
        while self.is_running:
            try:
                data, addr = self.sock.recvfrom(1024)
                if addr[0] == self.ip:
                    continue
                
                from_where = addr[0]

                if addr[0] in self.peers_ip_to_id:
                    from_where = self.peers_ip_to_id.get(addr[0])

                message = data.decode()
                if self.echo:
                    print(f"<{from_where} -> Me>\n{message}\n")

                if message.startswith(self.discovery_cue):
                    target_id = message.split(":")[1]
                    self.peers_id_to_ip[target_id] = addr[0]
                    self.peers_ip_to_id[addr[0]] = target_id
                    self.send_data(f"{self.answer_cue}{self.id}", target_id=target_id)
                    continue 

                if message.startswith(self.answer_cue):
                    target_id = message.split(":")[1]
                    self.peers_id_to_ip[target_id] = addr[0]
                    self.peers_ip_to_id[addr[0]] = target_id
                    continue
                
                self.message_handler(message, from_where)

            except socket.error as e:
                print(f"Socket error: {e}\n")
            except Exception as e:
                if self.echo:
                    print(f"Error: {e}\n")

    def close(self):
        """
        Close the UDP client protocol
        """
        self.is_running = False
        self.sock.close()





