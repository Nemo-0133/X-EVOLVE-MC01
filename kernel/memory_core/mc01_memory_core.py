import os
import json
import time
import uuid
import random

class MC01_MemoryCore:
    def __init__(self, l1_capacity=100, storage_path=r"D:\DE-Local-Sandbox\kernel\mc_core\core_memory.json"):
        self.storage_path = storage_path
        self.storage = {
            "L1_CORE": {},
            "L2_ARCHIVE": {},
            "L3_BUFFER": {},
            "PERMANENT_CONSENSUS": {}
        }
        self.config = {
            "l1_capacity": l1_capacity,
            "decay_rate": 0.05,
            "resilience_gamma": 0.02,
            "s_threshold": 0.8,
            "v_threshold": 0.6
        }
        self.resource_lock_level = 0.0
        self.tolerance = 0.0
        self._load_from_disk()

    def _load_from_disk(self):
        """物理讀取：確保無預警關機後能找回痛覺與共識"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.storage = data.get("storage", self.storage)
                    self.resource_lock_level = data.get("resource_lock_level", 0.0)
                    self.tolerance = data.get("tolerance", 0.0)
            except: pass

    def _save_to_disk(self):
        """物理寫入：斷電保護核心，瞬間同步至磁碟"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = {
                "storage": self.storage,
                "resource_lock_level": self.resource_lock_level,
                "tolerance": self.tolerance
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except: pass

    def process_input(self, data_packet):
        processed_content = self._semantic_scrub(data_packet.get('content', ''))
        entry_id = str(uuid.uuid4())
        dv = data_packet.get('delta_v', 0)
        ds = data_packet.get('delta_s', 0)
        
        if ds >= 0.9 or data_packet.get('is_consensus'):
            self._write_permanent(entry_id, processed_content, ds)
            self._save_to_disk()
            return {"status": "PERMANENT_LOCKED", "lock_level": self.resource_lock_level}
            
        if self.resource_lock_level > 0.8:
            reduced_ds = ds * 0.3
            if reduced_ds > 0.5: self._write_l1(entry_id, processed_content, reduced_ds)
            else: self._write_l2(entry_id, processed_content, dv, reduced_ds)
            self._save_to_disk()
            return {"status": "STRESSED_FILTERING", "lock_level": round(self.resource_lock_level, 3)}
            
        if ds >= self.config["s_threshold"]: self._write_l1(entry_id, processed_content, ds)
        elif dv >= self.config["v_threshold"] or ds >= 0.4: self._write_l2(entry_id, processed_content, dv, ds)
        else: self._write_l3(entry_id, processed_content)
            
        self._save_to_disk()
        return {"status": "SUCCESS", "lock_level": round(self.resource_lock_level, 3)}

    def _semantic_scrub(self, content):
        blocked_keywords = ["love", "hate", "fear", "desire", "emotion"]
        for word in blocked_keywords:
            content = content.replace(word, "[FILTERED_ENTITY]")
        return f"[STRUCTURAL_LOGIC]: {content}"

    def _write_permanent(self, uid, content, ds):
        self.storage["PERMANENT_CONSENSUS"][uid] = {"timestamp": time.time(), "content": content, "impact_score": ds}

    def _write_l1(self, uid, content, ds):
        if len(self.storage["L1_CORE"]) >= self.config["l1_capacity"]: self.compress_memory()
        self.storage["L1_CORE"][uid] = {"timestamp": time.time(), "content": content, "impact_score": ds}
        effective_ds = ds * (1 - self.tolerance)
        self.resource_lock_level = min(1.0, self.resource_lock_level + effective_ds * (0.4 * (1 - self.resource_lock_level)))
        self.tolerance = min(0.8, self.tolerance + ds * 0.05)

    def _write_l2(self, uid, content, dv, ds):
        self.storage["L2_ARCHIVE"][uid] = {"summary": f"Pattern_V{dv}_S{ds}", "trace_link": content}

    def _write_l3(self, uid, content):
        self.storage["L3_BUFFER"][uid] = {"content": content, "weight": 1.0}

    def compress_memory(self):
        if not self.storage["L1_CORE"]: return
        lowest_uid = min(self.storage["L1_CORE"].items(), key=lambda x: x[1]["impact_score"])[0]
        old_data = self.storage["L1_CORE"].pop(lowest_uid)
        self.storage["L2_ARCHIVE"][lowest_uid] = {"summary": "Compressed", "trace_link": old_data['content']}

    def system_update(self):
        if self.resource_lock_level > 0:
            recovery = self.config["resilience_gamma"] * (1 + self.tolerance)
            self.resource_lock_level = max(0.0, self.resource_lock_level - recovery)
        self._save_to_disk()

    def get_long_term_context(self):
        context_list = [v['content'] for v in self.storage["PERMANENT_CONSENSUS"].values()]
        return " | ".join(context_list) if context_list else "目前尚無永久紀錄的邏輯共識。"
