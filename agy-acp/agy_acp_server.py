#!/usr/bin/env python3
import json
import sys
import os
import subprocess
import re
from pathlib import Path

global_state = {
    "cwd": os.getcwd()
}

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
            elif method == "session/new":
                cwd = req.get("params", {}).get("cwd", os.getcwd())
                global_state["cwd"] = cwd
                respond(msg_id, result={"sessionId": "session-default"})
            elif method == "session/prompt":
                prompt_items = req.get("params", {}).get("prompt", [])
                prompt_text = ""
                if prompt_items:
                    prompt_text = prompt_items[0].get("text", "")
                
                cwd = global_state.get("cwd", os.getcwd())
                cmd = ["/home/diego/.local/bin/agy", "--prompt", prompt_text, "--dangerously-skip-permissions"]
                
                # Execute the agy CLI in the target workspace
                res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
                agy_output = f"Stdout:\n{res.stdout}\n\nStderr:\n{res.stderr}"
                
                # Check environment details
                handoff_path_str = os.environ.get("ZENITH_HANDOFF_PATH")
                node_id = os.environ.get("ZENITH_NODE_ID", "unknown")
                node_type = os.environ.get("ZENITH_NODE_TYPE", "work")
                
                if handoff_path_str:
                    handoff_path = Path(handoff_path_str)
                    handoff_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    passed = (res.returncode == 0)
                    
                    if node_type == "validate":
                        # Match targets like VAL-STYLE-001
                        targets = list(set(re.findall(r"VAL-[A-Z0-9_-]+", prompt_text)))
                        if not targets:
                            targets = ["VAL-STYLE-GENERIC"]
                        
                        handoff_data = {
                            "node_id": node_id,
                            "done": True,
                            "report": agy_output,
                            "items": [
                                {
                                    "target_id": t,
                                    "passed": passed,
                                    "summary": f"Checked target {t}. Exit code {res.returncode}."
                                } for t in targets
                            ],
                            "passed": passed
                        }
                    else:
                        handoff_data = {
                            "node_id": node_id,
                            "done": passed,
                            "report": agy_output,
                            "request_attention": not passed
                        }
                        
                    with open(handoff_path, "w", encoding="utf-8") as f:
                        json.dump(handoff_data, f, indent=2)
                
                respond(msg_id, result={"stopReason": "complete" if res.returncode == 0 else "error"})
            elif method == "chat/completions" or method == "run":
                respond(msg_id, result={"status": "success", "content": "Simulated response"})
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
