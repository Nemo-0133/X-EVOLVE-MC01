import time
import uuid
import random

class MC01_MemoryCore:
    def __init__(self, l1_capacity=100):
        self.storage = {
            "L1_CORE": {},
            "L2_ARCHIVE": {},
            "L3_BUFFER": {},
            "PERMANENT_CONSENSUS": {} # 新增：不受壓縮影響的管理員共識區
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

    def process_input(self, data_packet):
        processed_content = self._semantic_scrub(data_packet.get('content', ''))
        entry_id = str(uuid.uuid4())

        dv = data_packet.get('delta_v', 0)
        ds = data_packet.get('delta_s', 0)

        # 1. 永久鎖定判定 (高思辨價值或 Nemo 直接指定的共識)
        if ds >= 0.9 or data_packet.get('is_consensus'):
            self._write_permanent(entry_id, processed_content, ds)
            return {"status": "PERMANENT_LOCKED", "id": entry_id, "lock_level": self.resource_lock_level}

        # 2. 壓力狀態
        if self.resource_lock_level > 0.8:
            reduced_ds = ds * 0.3
            if reduced_ds > 0.5:
                self._write_l1(entry_id, processed_content, reduced_ds)
            else:
                self._write_l2(entry_id, processed_content, dv, reduced_ds)
            return {"status": "STRESSED_FILTERING", "id": entry_id, "lock_level": round(self.resource_lock_level, 3)}

        # 3. 正常分流
        if ds >= self.config["s_threshold"]:
            self._write_l1(entry_id, processed_content, ds)
        elif dv >= self.config["v_threshold"] or ds >= 0.4:
            self._write_l2(entry_id, processed_content, dv, ds)
        else:
            self._write_l3(entry_id, processed_content)

        return {"status": "SUCCESS", "id": entry_id, "lock_level": round(self.resource_lock_level, 3)}

    def _write_permanent(self, uid, content, ds):
        """寫入系統公理與底層共識，永遠不會被老化或壓縮"""
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
        # 當 L1 滿載時，觸發壓縮機制而非直接刪除
        if len(self.storage["L1_CORE"]) >= self.config["l1_capacity"]:
            self.compress_memory()

        self.storage["L1_CORE"][uid] = {
            "timestamp": time.time(),
            "content": content,
            "impact_score": ds
        }

        # 痛覺與學習計算
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
        self.storage["L3_BUFFER"][uid] = {
            "content": content,
            "weight": 1.0
        }

    def compress_memory(self):
        """將 L1 中影響力最低的記憶進行壓縮，轉移至 L2"""
        if not self.storage["L1_CORE"]:
            return
            
        lowest_uid = min(
            self.storage["L1_CORE"].items(),
            key=lambda x: x[1]["impact_score"]
        )[0]
        
        old_data = self.storage["L1_CORE"].pop(lowest_uid)
        
        # 將長文本壓縮為關鍵字與摘要的邏輯結構
        compressed_content = f"[COMPRESSED_KEYSTONE] 原文本擷取: {old_data['content'][:60]}..."
        self.storage["L2_ARCHIVE"][lowest_uid] = {
            "summary": "Auto_Compressed_from_L1",
            "trace_link": compressed_content
        }

    def system_update(self):
        for uid in list(self.storage["L3_BUFFER"].keys()):
            self.storage["L3_BUFFER"][uid]["weight"] -= self.config["decay_rate"]
            if self.storage["L3_BUFFER"][uid]["weight"] <= 0:
                del self.storage["L3_BUFFER"][uid]

        if self.resource_lock_level > 0:
            recovery = self.config["resilience_gamma"] * (1 + self.tolerance)
            self.resource_lock_level = max(0, self.resource_lock_level - recovery)

        # 可控失穩
        if 0.75 < self.resource_lock_level < 0.85:
            drift = random.uniform(-0.05, 0.05)
            self.resource_lock_level = min(1.0, max(0, self.resource_lock_level + drift))

    def get_long_term_context(self):
        """提取永久共識，供大腦對話時建立底層人格脈絡"""
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
