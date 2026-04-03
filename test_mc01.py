from kernel.memory_core.memory_core_v1 import IEMemoryCore

core = IEMemoryCore()

print("=== START TEST ===")

for i in range(120):
    result = core.process_input({
        "content": f"test_event_{i}",
        "delta_v": 0.9,
        "delta_s": 0.9
    })

    if i % 10 == 0:
        print(f"[{i}] {result}")

print("\n=== SNAPSHOT ===")
print(core.debug_snapshot())

for _ in range(50):
    core.system_update()

print("\n=== AFTER RECOVERY ===")
print(core.debug_snapshot())
