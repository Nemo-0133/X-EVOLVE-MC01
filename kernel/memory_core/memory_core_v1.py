import time
import uuid

class IEMemoryCore:
    def __init__(self, l1_capacity=100):
        # 1. 分層存儲架構
        self.storage = {
            "L1_CORE": {},     # 核心創傷/自檢紀錄 (具備容量限制)
            "L2_ARCHIVE": {},  # 模式存檔 (可回溯索引)
            "L3_BUFFER": {}    # 短期觀測 (高衰減)
        }
        
        # 2. 系統配置
        self.config = {
            "l1_capacity": l1_capacity,
            "decay_rate": 0.05,       # L3 遺忘速度
            "resilience_gamma": 0.02, # 痛覺修復速度
            "s_threshold": 0.8,       # L1 寫入門檻
            "v_threshold": 0.6        # L2 寫入門檻
        }
        
        # 3. 系統狀態（痛覺）
        self.resource_lock_level = 0.0

    def process_input(self, data_packet):
        """
        data_packet: { "content": str, "delta_v": float, "delta_s": float }
        """
        # 過載保護（痛覺觸發）
        if self.resource_lock_level > 0.8:
            return {"status": "REJECTED", "reason": "SYSTEM_OVERLOAD_PAIN"}

        processed_content = self._semantic_scrub(data_packet['content'])
        entry_id = str(uuid.uuid4())
        
        dv = data_packet['delta_v']
        ds = data_packet['delta_s']
        
        if ds >= self.config["s_threshold"]:
            self._write_l1(entry_id, processed_content, ds)
        elif dv >= self.config["v_threshold"] or ds >= 0.4:
            self._write_l2(entry_id, processed_content, dv, ds)
        else:
            self._write_l3(entry_id, processed_content)

        return {
            "status": "SUCCESS",
            "id": entry_id,
            "lock_level": self.resource_lock_level
        }

    def _semantic_scrub(self, content):
        """語義隔離"""
        blocked_keywords = ["love", "hate", "fear", "desire", "emotion"]
        for word in blocked_keywords:
            content = content.replace(word, "[FILTERED_ENTITY]")
        return f"[STRUCTURAL_LOGIC]: {content}"

    def _write_l1(self, uid, content, ds):
        """寫入 L1（含容量控制）"""
        if len(self.storage["L1_CORE"]) >= self.config["l1_capacity"]:
            lowest_uid = min(
                self.storage["L1_CORE"].items(),
                key=lambda x: x[1]["impact_score"]
            )[0]
            del self.storage["L1_CORE"][lowest_uid]

        self.storage["L1_CORE"][uid] = {
            "timestamp": time.time(),
            "content": content,
            "impact_score": ds
        }

        self.resource_lock_level = min(1.0, self.resource_lock_level + (ds * 0.4))

    def _write_l2(self, uid, content, dv, ds):
        """寫入 L2"""
        self.storage["L2_ARCHIVE"][uid] = {
            "summary": f"Pattern_V{dv}_S{ds}",
            "trace_link": content
        }

    def _write_l3(self, uid, content):
        """寫入 L3"""
        self.storage["L3_BUFFER"][uid] = {
            "content": content,
            "weight": 1.0
        }

    def system_update(self):
        """遺忘與修復"""
        for uid in list(self.storage["L3_BUFFER"].keys()):
            self.storage["L3_BUFFER"][uid]["weight"] -= self.config["decay_rate"]
            if self.storage["L3_BUFFER"][uid]["weight"] <= 0:
                del self.storage["L3_BUFFER"][uid]

        if self.resource_lock_level > 0:
            self.resource_lock_level = max(
                0,
                self.resource_lock_level - self.config["resilience_gamma"]
            )

    def debug_snapshot(self):
        """觀測層"""
        return {
            "L1_USE": f"{len(self.storage['L1_CORE'])}/{self.config['l1_capacity']}",
            "L2_SIZE": len(self.storage["L2_ARCHIVE"]),
            "L3_SIZE": len(self.storage["L3_BUFFER"]),
            "PAIN_LEVEL": round(self.resource_lock_level, 3),
            "STATUS": "ACTIVE" if self.resource_lock_level < 0.8 else "STUNNED"
        }
