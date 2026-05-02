import time
from typing import Dict, Optional

class Process:
    def __init__(self, pid: int, name: str, required_memory: int):
        self.pid = pid
        self.name = name
        self.required_memory = required_memory # In bytes
        self.page_table: Dict[int, int] = {} # logical page -> physical frame
        self.state = "RUNNING"
        self.domain = f"domain_{pid}"

class MemoryManager:
    def __init__(self, total_memory: int = 16384, frame_size: int = 256):
        self.total_memory = total_memory
        self.frame_size = frame_size
        self.num_frames = total_memory // frame_size
        # 0 = free, non-zero = pid
        self.frames = [0] * self.num_frames 
        
    def allocate(self, process: Process) -> bool:
        num_pages = (process.required_memory + self.frame_size - 1) // self.frame_size
        free_frames = [i for i, f in enumerate(self.frames) if f == 0]
        
        if len(free_frames) < num_pages:
            return False 
            
        for i in range(num_pages):
            frame_idx = free_frames[i]
            self.frames[frame_idx] = process.pid
            process.page_table[i] = frame_idx
            
        return True

    def deallocate(self, process: Process):
        for logical_page, frame_idx in process.page_table.items():
            self.frames[frame_idx] = 0
        process.page_table.clear()

class SecurityEnforcer:
    def __init__(self):
        self.access_matrix: Dict[str, Dict[int, str]] = {}
        
    def grant_access(self, domain: str, frame_idx: int, permission: str):
        if domain not in self.access_matrix:
            self.access_matrix[domain] = {}
        self.access_matrix[domain][frame_idx] = permission
        
    def revoke_access(self, domain: str, frame_idx: int):
        if domain in self.access_matrix and frame_idx in self.access_matrix[domain]:
            del self.access_matrix[domain][frame_idx]

    def check_access(self, domain: str, frame_idx: int, operation: str) -> bool:
        if domain not in self.access_matrix:
            return False
        perms = self.access_matrix[domain].get(frame_idx, "")
        if operation == "READ" and "R" in perms:
            return True
        if operation == "WRITE" and "W" in perms:
            return True
        return False

class OSEngine:
    def __init__(self):
        self.memory = MemoryManager()
        self.security = SecurityEnforcer()
        self.processes: Dict[int, Process] = {}
        self.next_pid = 1
        self.logs = []
        
    def add_log(self, level: str, message: str):
        self.logs.append({"time": time.time(), "level": level, "message": message})
        
    def create_process(self, name: str, memory_size: int) -> Optional[Process]:
        p = Process(self.next_pid, name, memory_size)
        self.next_pid += 1
        
        if self.memory.allocate(p):
            self.processes[p.pid] = p
            for page, frame in p.page_table.items():
                self.security.grant_access(p.domain, frame, "RW")
            self.add_log("INFO", f"Process {p.name} (PID {p.pid}) created with {len(p.page_table)} pages.")
            return p
        else:
            self.add_log("ERROR", f"Failed to allocate memory for {p.name}.")
            return None
            
    def terminate_process(self, pid: int):
        if pid in self.processes:
            p = self.processes[pid]
            for page, frame in p.page_table.items():
                self.security.revoke_access(p.domain, frame)
            self.memory.deallocate(p)
            del self.processes[pid]
            self.add_log("INFO", f"Process PID {pid} terminated.")
            
    def simulate_memory_access(self, pid: int, logical_page: int, operation: str):
        if pid not in self.processes:
            self.add_log("ERROR", f"Invalid PID {pid} for memory access.")
            return False
            
        p = self.processes[pid]
        
        if logical_page not in p.page_table:
            self.add_log("WARNING", f"PAGE FAULT: PID {pid} accessed unmapped page {logical_page}.")
            return False
            
        frame = p.page_table[logical_page]
        
        if self.security.check_access(p.domain, frame, operation):
            self.add_log("SUCCESS", f"PID {pid} successfully {operation} frame {frame}.")
            return True
        else:
            self.add_log("CRITICAL", f"SIGSEGV: PID {pid} unauthorized {operation} on frame {frame}.")
            self.terminate_process(pid)
            return False

    def simulate_buffer_overflow(self, pid: int):
        if pid not in self.processes:
            return False
        
        p = self.processes[pid]
        if not p.page_table:
            return False
            
        max_page = max(p.page_table.keys())
        overflow_page = max_page + 1 
        
        self.add_log("CRITICAL", f"Buffer Overflow attempt by PID {pid} on logical page {overflow_page}.")
        return self.simulate_memory_access(pid, overflow_page, "WRITE")
        
    def simulate_unauthorized_access(self, source_pid: int, target_pid: int):
        if source_pid not in self.processes or target_pid not in self.processes:
             return False
             
        p_target = self.processes[target_pid]
        if not p_target.page_table:
             return False
             
        target_frame = list(p_target.page_table.values())[0]
        self.add_log("CRITICAL", f"Illegal Access attempt by PID {source_pid} targeting frame {target_frame} (owned by PID {target_pid}).")
        
        p_source = self.processes[source_pid]
        if self.security.check_access(p_source.domain, target_frame, "READ"):
            self.add_log("SUCCESS", f"PID {source_pid} accessed shared frame {target_frame}.")
            return True
        else:
            self.add_log("CRITICAL", f"SIGSEGV: PID {source_pid} denied access to frame {target_frame}.")
            self.terminate_process(source_pid)
            return False
            
    def setup_shared_memory(self, pid1: int, pid2: int):
         if pid1 not in self.processes or pid2 not in self.processes:
             return False
         p1 = self.processes[pid1]
         p2 = self.processes[pid2]
         
         if not p1.page_table:
             return False
             
         shared_frame = list(p1.page_table.values())[0]
         next_logical = max(p2.page_table.keys()) + 1 if p2.page_table else 0
         p2.page_table[next_logical] = shared_frame
         
         self.security.grant_access(p2.domain, shared_frame, "RW")
         self.add_log("INFO", f"Shared memory established between PID {pid1} and {pid2} on frame {shared_frame}.")
         return True

    def get_state(self):
        return {
            "frames": self.memory.frames,
            "processes": {pid: {"pid": p.pid, "name": p.name, "state": p.state, "pages": p.page_table} for pid, p in self.processes.items()},
            "logs": self.logs[-50:]
        }
