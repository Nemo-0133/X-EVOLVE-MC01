from kernel.memory_core.memory_core_v1 import IEMemoryCore

core = IEMemoryCore()

# === 測試 1：高壓創傷輸入 ===
for i in range(120):
    result = core.process_input({
        "content": f"test_event_{i}",
        "delta_v": 0.9,
        "delta_s": 0.9
    })
    print(result)

# === 查看當前狀態 ===
print("\n=== SNAPSHOT ===")
print(core.debug_snapshot())

# === 測試 2：系統恢復 ===
for _ in range(50):
    core.system_update()

print("\n=== AFTER RECOVERY ===")
print(core.debug_snapshot())
