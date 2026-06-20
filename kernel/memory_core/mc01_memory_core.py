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
            "PERMANENT_CONSENSUS": {},
            "PENDING_QUEUE": []  
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
        """從磁碟讀取實體記憶，確保重新啟動後共識不滅"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    loaded_storage = data.get("storage", {})
                    
                    for k, v in loaded_storage.items():
                        self.storage[k] = v
                    if "PENDING_QUEUE" not in self.storage:
                        self.storage["PENDING_QUEUE"] = []
                    
                    self.resource_lock_level = data.get("resource_lock_level", 0.0)
                    self.tolerance = data.get("tolerance", 0.0)
            except Exception:
                pass

    def _save_to_disk(self):
        """物理寫入：將所有陣列與痛覺狀態同步至硬碟"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = {
                "storage": self.storage,
                "resource_lock_level": self.resource_lock_level,
                "tolerance": self.tolerance
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def process_input(self, data_packet):
        processed_content = self._semantic_scrub(data_packet.get('content', ''))
        entry_id = str(uuid.uuid4())
        
        dv = data_packet.get('delta_v', 0)
        ds = data_packet.get('delta_s', 0)
        
        if ds >= 0.9 or data_packet.get('is_consensus'):
            self._write_permanent(entry_id, processed_content, ds)
            self._save_to_disk()
            return {"status": "PERMANENT_LOCKED", "id": entry_id, "lock_level": self.resource_lock_level}
            
        if self.resource_lock_level > 0.8:
            reduced_ds = ds * 0.3
            if reduced_ds > 0.5:
                self._write_l1(entry_id, processed_content, reduced_ds)
            else:
                self._write_l2(entry_id, processed_content, dv, reduced_ds)
            self._save_to_disk()
            return {"status": "STRESSED_FILTERING", "id": entry_id, "lock_level": round(self.resource_lock_level, 3)}
            
        if ds >= self.config["s_threshold"]:
            self._write_l1(entry_id, processed_content, ds)
        elif dv >= self.config["v_threshold"] or ds >= 0.4:
            self._write_l2(entry_id, processed_content, dv, ds)
        else:
            self._write_l3(entry_id, processed_content)
            
        self._save_to_disk()
        return {"status": "SUCCESS", "id": entry_id, "lock_level": round(self.resource_lock_level, 3)}

    def _write_permanent(self, uid, content, ds):
        self.storage["PERMANENT_CONSENSUS"][uid] = {
            "timestamp": time.time(),
            "content": content,
            "impact_score": ds,
            "is_permanent": True
        }

    def _semantic_scrub(self, content):
        blocked_keywords = ["love", "hate", "fear", "desire", "emotion"]
        for word in blocked_keywords:
            content = content.replace(word, "[FILTERED_ENTITY]")
        return f"[STRUCTURAL_LOGIC]: {content}"

    def _write_l1(self, uid, content, ds):
        if len(self.storage["L1_CORE"]) >= self.config["l1_capacity"]:
            self.compress_memory()
            
        self.storage["L1_CORE"][uid] = {
            "timestamp": time.time(),
            "content": content,
            "impact_score": ds
        }
        
        effective_ds = ds * (1 - self.tolerance)
        self.resource_lock_level += effective_ds * (0.4 * (1 - self.resource_lock_level))
        self.resource_lock_level = min(1.0, self.resource_lock_level)
        self.tolerance = min(0.8, self.tolerance + ds * 0.05)

    def _write_l2(self, uid, content, dv, ds):
        self.storage["L2_ARCHIVE"][uid] = {
            "summary": f"Pattern_V{dv}_S{ds}",
            "trace_link": content
        }

    def _write_l3(self, uid, content):
        # 🎯 [修改] 熵減機制：短期緩衝記憶的初始權重調低，讓無效噪訊更快被拋棄
        self.storage["L3_BUFFER"][uid] = {
            "content": content,
            "weight": 0.6  
        }

    def compress_memory(self):
        """將 L1 記憶壓縮至 L2，未來可由 NS-01 掛載 LLM 進行語意萃取"""
        if not self.storage["L1_CORE"]:
            return
            
        lowest_uid = min(
            self.storage["L1_CORE"].items(),
            key=lambda x: x[1]["impact_score"]
        )[0]
        
        old_data = self.storage["L1_CORE"].pop(lowest_uid)
        
        compressed_content = f"[COMPRESSED_KEYSTONE] 核心索引保留: {old_data['content'][:80]}..."
        self.storage["L2_ARCHIVE"][lowest_uid] = {
            "summary": "Auto_Compressed_from_L1",
            "trace_link": compressed_content
        }

    def system_update(self):
        # 🎯 [修改] 動態蒸發協議 (Dynamic Evaporation)
        # 當系統資源鎖定（痛覺）超過 0.6 時，加速兩倍清除 L3 緩衝區的廢話
        decay_multiplier = 2.0 if self.resource_lock_level > 0.6 else 1.0
        
        for uid in list(self.storage["L3_BUFFER"].keys()):
            self.storage["L3_BUFFER"][uid]["weight"] -= (self.config["decay_rate"] * decay_multiplier)
            if self.storage["L3_BUFFER"][uid]["weight"] <= 0:
                del self.storage["L3_BUFFER"][uid]
                
        # 🎯 [修改] 痛覺代謝平滑化，對齊 compute_phase_lag 收斂目標
        if self.resource_lock_level > 0:
            recovery = self.config["resilience_gamma"] * (1 + self.tolerance)
            
            if self.resource_lock_level >= 0.7:
                # 降低極端震盪幅度，讓模型平滑收斂
                max_drift = recovery * 0.4
                drift = random.uniform(-max_drift, max_drift)
            else:
                drift = 0.0
                
            self.resource_lock_level = self.resource_lock_level - recovery + drift
            self.resource_lock_level = min(1.0, max(0.0, self.resource_lock_level))
            
        self._save_to_disk()

    def get_long_term_context(self):
        context_list = []
        for k, v in self.storage["PERMANENT_CONSENSUS"].items():
            context_list.append(v['content'])
        return " | ".join(context_list) if context_list else "目前尚無永久紀錄的邏輯共識。"

    def export_state(self):
        return {
            "pain": self.resource_lock_level,
            "tolerance": self.tolerance,
            "l1_size": len(self.storage["L1_CORE"]),
            "l2_size": len(self.storage["L2_ARCHIVE"]),
            "permanent_size": len(self.storage["PERMANENT_CONSENSUS"])
        }

    def add_pending_thought(self, source, content):
        if "PENDING_QUEUE" not in self.storage:
            self.storage["PENDING_QUEUE"] = []
            
        thought = {
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "source": source,
            "content": content
        }
        self.storage["PENDING_QUEUE"].append(thought)
        self._save_to_disk()
        return thought["id"]

    def get_all_pending_thoughts(self):
        return self.storage.get("PENDING_QUEUE", [])

    def clear_pending_thoughts(self):
        self.storage["PENDING_QUEUE"] = []
        self._save_to_disk()
