/**
 * Agent WebSocket Hook
 * 
 * Custom hook for managing WebSocket connections to receive real-time
 * agent status updates and workflow progress.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { 
  AgentUpdateMessage, 
  AgentStatusUpdate, 
  WorkflowProgressUpdate,
  WorkflowState 
} from '../types/agent';

interface UseAgentWebSocketOptions {
  scanId: string;
  onAgentStatusUpdate?: (update: AgentStatusUpdate) => void;
  onWorkflowProgress?: (update: WorkflowProgressUpdate) => void;
  onWorkflowComplete?: (finalState: any) => void;
  onError?: (error: Error) => void;
  autoReconnect?: boolean;
  reconnectDelay?: number;
  maxReconnectAttempts?: number;
}

interface UseAgentWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  lastMessage: AgentUpdateMessage | null;
  sendMessage: (message: any) => void;
  reconnect: () => void;
  disconnect: () => void;
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error';
}

const useAgentWebSocket = ({
  scanId,
  onAgentStatusUpdate,
  onWorkflowProgress,
  onWorkflowComplete,
  onError,
  autoReconnect = true,
  reconnectDelay = 3000,
  maxReconnectAttempts = 5,
}: UseAgentWebSocketOptions): UseAgentWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState<AgentUpdateMessage | null>(null);
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  // WebSocket URL - update this to match your backend
  const getWebSocketUrl = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}/ws/scan/${scanId}`;
  }, [scanId]);

  // Send message through WebSocket
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Cannot send message:', message);
    }
  }, []);

  // Handle incoming messages
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: AgentUpdateMessage = JSON.parse(event.data);
      setLastMessage(message);

      // Route message to appropriate handler
      switch (message.type) {
        case 'agent_status_update':
          onAgentStatusUpdate?.(message.data as AgentStatusUpdate);
          break;
        case 'workflow_progress':
          onWorkflowProgress?.(message.data as WorkflowProgressUpdate);
          break;
        case 'workflow_complete':
          onWorkflowComplete?.(message.data);
          break;
        case 'agent_log':
          // Handle agent logs if needed
          break;
        default:
          console.warn('Unknown message type:', message.type);
      }
    } catch (err) {
      console.error('Failed to parse WebSocket message:', err);
      setError('Failed to parse message from server');
    }
  }, [onAgentStatusUpdate, onWorkflowProgress, onWorkflowComplete]);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    if (wsRef.current) {
      wsRef.current.close();
    }

    setIsConnecting(true);
    setConnectionState('connecting');
    setError(null);

    try {
      const ws = new WebSocket(getWebSocketUrl());
      wsRef.current = ws;

      ws.onopen = () => {
        if (!mountedRef.current) return;
        
        console.log('WebSocket connected for scan:', scanId);
        setIsConnected(true);
        setIsConnecting(false);
        setConnectionState('connected');
        setError(null);
        reconnectAttemptsRef.current = 0;

        // Send initial handshake message
        sendMessage({
          type: 'subscribe',
          scanId: scanId,
          timestamp: new Date().toISOString()
        });
      };

      ws.onmessage = handleMessage;

      ws.onclose = (event) => {
        if (!mountedRef.current) return;

        console.log('WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        setIsConnecting(false);
        
        if (event.code !== 1000 && event.code !== 1001) {
          // Abnormal closure
          setConnectionState('error');
          setError(`Connection closed unexpectedly (${event.code})`);
          
          // Attempt reconnection if enabled
          if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current++;
            console.log(`Attempting reconnection ${reconnectAttemptsRef.current}/${maxReconnectAttempts}`);
            
            reconnectTimeoutRef.current = setTimeout(() => {
              if (mountedRef.current) {
                connect();
              }
            }, reconnectDelay);
          } else {
            setConnectionState('disconnected');
          }
        } else {
          setConnectionState('disconnected');
        }
      };

      ws.onerror = (event) => {
        if (!mountedRef.current) return;

        console.error('WebSocket error:', event);
        setConnectionState('error');
        setError('WebSocket connection error');
        onError?.(new Error('WebSocket connection error'));
      };

    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      setIsConnecting(false);
      setConnectionState('error');
      setError('Failed to create WebSocket connection');
      onError?.(err as Error);
    }
  }, [scanId, getWebSocketUrl, handleMessage, autoReconnect, maxReconnectAttempts, reconnectDelay, sendMessage, onError]);

  // Disconnect WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Client disconnect');
      wsRef.current = null;
    }

    setIsConnected(false);
    setIsConnecting(false);
    setConnectionState('disconnected');
    setError(null);
  }, []);

  // Manual reconnect
  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    setTimeout(() => {
      if (mountedRef.current) {
        connect();
      }
    }, 100);
  }, [connect, disconnect]);

  // Auto-connect on mount and when scanId changes
  useEffect(() => {
    if (scanId) {
      connect();
    }

    return () => {
      mountedRef.current = false;
      disconnect();
    };
  }, [scanId, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    isConnected,
    isConnecting,
    error,
    lastMessage,
    sendMessage,
    reconnect,
    disconnect,
    connectionState,
  };
};

export default useAgentWebSocket;