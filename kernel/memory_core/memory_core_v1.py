import time
import uuid
import random

class IEMemoryCore:
    def __init__(self, l1_capacity=100):
        # 1. 分層存儲架構
        self.storage = {
            "L1_CORE": {},
            "L2_ARCHIVE": {},
            "L3_BUFFER": {}
        }
        
        # 2. 系統配置
        self.config = {
            "l1_capacity": l1_capacity,
            "decay_rate": 0.05,
            "resilience_gamma": 0.02,
            "s_threshold": 0.8,
            "v_threshold": 0.6
        }
        
        # 3. 系統狀態
        self.resource_lock_level = 0.0
        self.tolerance = 0.0

    def process_input(self, data_packet):
        """
        data_packet: { "content": str, "delta_v": float, "delta_s": float }
        """

        processed_content = self._semantic_scrub(data_packet['content'])
        entry_id = str(uuid.uuid4())
        
        dv = data_packet['delta_v']
        ds = data_packet['delta_s']

        # 🔥 壓力狀態：學習 + 分流
        if self.resource_lock_level > 0.8:
            reduced_ds = ds * 0.3

            if reduced_ds > 0.5:
                self._write_l1(entry_id, processed_content, reduced_ds)
            else:
                self._write_l2(entry_id, processed_content, dv, reduced_ds)

            return {
                "status": "STRESSED_FILTERING",
                "id": entry_id,
                "lock_level": round(self.resource_lock_level, 3),
                "tolerance": round(self.tolerance, 3)
            }
        
        # 正常分流
        if ds >= self.config["s_threshold"]:
            self._write_l1(entry_id, processed_content, ds)
        elif dv >= self.config["v_threshold"] or ds >= 0.4:
            self._write_l2(entry_id, processed_content, dv, ds)
        else:
            self._write_l3(entry_id, processed_content)

        return {
            "status": "SUCCESS",
            "id": entry_id,
            "lock_level": round(self.resource_lock_level, 3),
            "tolerance": round(self.tolerance, 3)
        }

    def _semantic_scrub(self, content):
        blocked_keywords = ["love", "hate", "fear", "desire", "emotion"]
        for word in blocked_keywords:
            content = content.replace(word, "[FILTERED_ENTITY]")
        return f"[STRUCTURAL_LOGIC]: {content}"

    def _write_l1(self, uid, content, ds):
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

        # 🔥 非線性痛覺
        effective_ds = ds * (1 - self.tolerance)
        self.resource_lock_level += effective_ds * (0.4 * (1 - self.resource_lock_level))
        self.resource_lock_level = min(1.0, self.resource_lock_level)

        # 🔥 抗壓學習
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

    def system_update(self):
        # L3 衰減
        for uid in list(self.storage["L3_BUFFER"].keys()):
            self.storage["L3_BUFFER"][uid]["weight"] -= self.config["decay_rate"]
            if self.storage["L3_BUFFER"][uid]["weight"] <= 0:
                del self.storage["L3_BUFFER"][uid]

        # 🔥 適應性恢復
        if self.resource_lock_level > 0:
            recovery = self.config["resilience_gamma"] * (1 + self.tolerance)
            self.resource_lock_level = max(
                0,
                self.resource_lock_level - recovery
            )

        # 🔥🔥🔥 核心：可控失穩（打破停滯）
        if 0.75 < self.resource_lock_level < 0.85:
            drift = random.uniform(-0.05, 0.05)
            self.resource_lock_level = min(
                1.0,
                max(0, self.resource_lock_level + drift)
            )

    def debug_snapshot(self):
        return {
            "L1_USE": f"{len(self.storage['L1_CORE'])}/{self.config['l1_capacity']}",
            "L2_SIZE": len(self.storage["L2_ARCHIVE"]),
            "L3_SIZE": len(self.storage["L3_BUFFER"]),
            "PAIN_LEVEL": round(self.resource_lock_level, 3),
            "TOLERANCE": round(self.tolerance, 3),
            "STATUS": "ACTIVE" if self.resource_lock_level < 0.8 else "STRESSED"
        }
