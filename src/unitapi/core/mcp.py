"""
UnitAPI Message Communication Protocol (MCP) Module

This module provides broker and client functionality for internal message passing.
"""

import time
import uuid
import logging
import threading
from typing import Dict, Any, Callable, List, Optional

logger = logging.getLogger("unitapi.mcp")

class MCPBroker:
    """
    Message Communication Protocol Broker
    
    Handles message routing between clients.
    """
    
    def __init__(self):
        """Initialize the MCP broker."""
        self.clients = {}
        self.subscriptions = {}
        self.lock = threading.RLock()
        logger.debug("MCP Broker initialized")
    
    def register_client(self, client_id: str, callback: Callable) -> bool:
        """
        Register a client with the broker.
        
        Args:
            client_id: Unique identifier for the client
            callback: Function to call when a message is received
            
        Returns:
            True if registration was successful, False otherwise
        """
        with self.lock:
            if client_id in self.clients:
                logger.warning(f"Client {client_id} already registered")
                return False
            
            self.clients[client_id] = callback
            logger.debug(f"Client {client_id} registered")
            return True
    
    def unregister_client(self, client_id: str) -> bool:
        """
        Unregister a client from the broker.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        with self.lock:
            if client_id not in self.clients:
                logger.warning(f"Client {client_id} not registered")
                return False
            
            # Remove client from subscriptions
            for topic in list(self.subscriptions.keys()):
                if client_id in self.subscriptions[topic]:
                    self.subscriptions[topic].remove(client_id)
                    
                    # Remove topic if no subscribers
                    if not self.subscriptions[topic]:
                        del self.subscriptions[topic]
            
            # Remove client
            del self.clients[client_id]
            logger.debug(f"Client {client_id} unregistered")
            return True
    
    def subscribe(self, client_id: str, topic: str) -> bool:
        """
        Subscribe a client to a topic.
        
        Args:
            client_id: Unique identifier for the client
            topic: Topic to subscribe to
            
        Returns:
            True if subscription was successful, False otherwise
        """
        with self.lock:
            if client_id not in self.clients:
                logger.warning(f"Client {client_id} not registered")
                return False
            
            if topic not in self.subscriptions:
                self.subscriptions[topic] = []
            
            if client_id in self.subscriptions[topic]:
                logger.debug(f"Client {client_id} already subscribed to {topic}")
                return True
            
            self.subscriptions[topic].append(client_id)
            logger.debug(f"Client {client_id} subscribed to {topic}")
            return True
    
    def unsubscribe(self, client_id: str, topic: str) -> bool:
        """
        Unsubscribe a client from a topic.
        
        Args:
            client_id: Unique identifier for the client
            topic: Topic to unsubscribe from
            
        Returns:
            True if unsubscription was successful, False otherwise
        """
        with self.lock:
            if client_id not in self.clients:
                logger.warning(f"Client {client_id} not registered")
                return False
            
            if topic not in self.subscriptions:
                logger.debug(f"Topic {topic} has no subscribers")
                return True
            
            if client_id not in self.subscriptions[topic]:
                logger.debug(f"Client {client_id} not subscribed to {topic}")
                return True
            
            self.subscriptions[topic].remove(client_id)
            
            # Remove topic if no subscribers
            if not self.subscriptions[topic]:
                del self.subscriptions[topic]
            
            logger.debug(f"Client {client_id} unsubscribed from {topic}")
            return True
    
    def publish(self, client_id: str, topic: str, message: Dict[str, Any]) -> bool:
        """
        Publish a message to a topic.
        
        Args:
            client_id: Unique identifier for the client
            topic: Topic to publish to
            message: Message to publish
            
        Returns:
            True if publication was successful, False otherwise
        """
        with self.lock:
            if client_id not in self.clients:
                logger.warning(f"Client {client_id} not registered")
                return False
            
            # Add metadata to message
            full_message = {
                "topic": topic,
                "timestamp": time.time(),
                "sender": client_id,
                "data": message
            }
            
            # Find matching topics (including wildcards)
            matching_topics = []
            for subscription_topic in self.subscriptions:
                if self._topic_matches(subscription_topic, topic):
                    matching_topics.append(subscription_topic)
            
            # Deliver message to subscribers
            for matching_topic in matching_topics:
                for subscriber_id in self.subscriptions[matching_topic]:
                    if subscriber_id != client_id or topic.startswith("system/"):
                        try:
                            self.clients[subscriber_id](full_message)
                        except Exception as e:
                            logger.error(f"Error delivering message to {subscriber_id}: {e}")
            
            logger.debug(f"Message published to {topic} by {client_id}")
            return True
    
    def _topic_matches(self, subscription_topic: str, publish_topic: str) -> bool:
        """
        Check if a subscription topic matches a publish topic.
        
        Args:
            subscription_topic: Topic pattern subscribed to
            publish_topic: Topic being published to
            
        Returns:
            True if the topics match, False otherwise
        """
        # Split topics into segments
        sub_segments = subscription_topic.split('/')
        pub_segments = publish_topic.split('/')
        
        # Check if lengths match (accounting for wildcards)
        if len(sub_segments) > len(pub_segments) and sub_segments[-1] != '#':
            return False
        
        # Check each segment
        for i, sub_segment in enumerate(sub_segments):
            # Multi-level wildcard
            if sub_segment == '#':
                return True
            
            # Single-level wildcard
            if sub_segment == '+':
                continue
            
            # Check if we've reached the end of the publish topic
            if i >= len(pub_segments):
                return False
            
            # Exact match
            if sub_segment != pub_segments[i]:
                return False
        
        # Check if we've matched all segments
        return len(sub_segments) == len(pub_segments)


class MCPClient:
    """
    Message Communication Protocol Client
    
    Handles communication with the MCP broker.
    """
    
    def __init__(self, broker: MCPBroker, client_id: Optional[str] = None):
        """
        Initialize the MCP client.
        
        Args:
            broker: MCP broker to connect to
            client_id: Unique identifier for the client (optional)
        """
        self.broker = broker
        self.client_id = client_id or f"client_{uuid.uuid4().hex[:8]}"
        self.callbacks = {}
        self.subscriptions = []
        
        # Register with broker
        self.broker.register_client(self.client_id, self._message_handler)
        logger.debug(f"MCP Client {self.client_id} initialized")
    
    def subscribe(self, topic: str, callback: Callable) -> bool:
        """
        Subscribe to a topic.
        
        Args:
            topic: Topic to subscribe to
            callback: Function to call when a message is received
            
        Returns:
            True if subscription was successful, False otherwise
        """
        if topic in self.callbacks:
            logger.warning(f"Already subscribed to {topic}")
            return False
        
        # Subscribe with broker
        if not self.broker.subscribe(self.client_id, topic):
            return False
        
        # Store callback
        self.callbacks[topic] = callback
        self.subscriptions.append(topic)
        logger.debug(f"Subscribed to {topic}")
        return True
    
    def unsubscribe(self, topic: str) -> bool:
        """
        Unsubscribe from a topic.
        
        Args:
            topic: Topic to unsubscribe from
            
        Returns:
            True if unsubscription was successful, False otherwise
        """
        if topic not in self.callbacks:
            logger.warning(f"Not subscribed to {topic}")
            return False
        
        # Unsubscribe from broker
        if not self.broker.unsubscribe(self.client_id, topic):
            return False
        
        # Remove callback
        del self.callbacks[topic]
        self.subscriptions.remove(topic)
        logger.debug(f"Unsubscribed from {topic}")
        return True
    
    def publish(self, topic: str, message: Dict[str, Any]) -> bool:
        """
        Publish a message to a topic.
        
        Args:
            topic: Topic to publish to
            message: Message to publish
            
        Returns:
            True if publication was successful, False otherwise
        """
        return self.broker.publish(self.client_id, topic, message)
    
    def close(self) -> bool:
        """
        Close the client connection.
        
        Returns:
            True if closure was successful, False otherwise
        """
        # Unsubscribe from all topics
        for topic in list(self.subscriptions):
            self.unsubscribe(topic)
        
        # Unregister from broker
        result = self.broker.unregister_client(self.client_id)
        logger.debug(f"Client {self.client_id} closed")
        return result
    
    def _message_handler(self, message: Dict[str, Any]):
        """
        Handle incoming messages.
        
        Args:
            message: Message received from the broker
        """
        topic = message["topic"]
        
        # Find matching callbacks
        for subscription_topic, callback in self.callbacks.items():
            if self.broker._topic_matches(subscription_topic, topic):
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Error in callback for {topic}: {e}")
