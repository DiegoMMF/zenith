#!/usr/bin/env python3
import json
import sys
import os

def respond(message_id, result=None, error=None):
    response = {"jsonrpc": "2.0", "id": message_id}
    if result is not None:
        response["result"] = result
    elif error is not None:
        response["error"] = error
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()

def notify(method, params=None):
    notification = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        notification["params"] = params
    sys.stdout.write(json.dumps(notification) + "\n")
    sys.stdout.flush()

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
            
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
            
        if "method" in req:
            method = req["method"]
            msg_id = req.get("id")
            
            if method == "initialize":
                respond(msg_id, result={"capabilities": {"tools": {}, "streaming": True}})
            elif method == "chat/completions" or method == "run":
                # Simulated response for proof of concept
                respond(msg_id, result={"status": "success", "content": "Simulated Antigravity response"})
            elif method == "ping":
                respond(msg_id, result={"status": "ok"})
            elif method == "exit":
                if msg_id:
                    respond(msg_id, result={"status": "exiting"})
                sys.exit(0)
            else:
                if msg_id:
                    respond(msg_id, error={"code": -32601, "message": f"Method {method} not found"})

if __name__ == "__main__":
    main()
