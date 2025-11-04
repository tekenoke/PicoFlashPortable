import subprocess
import os
import sys

print("=== RP2040 / RP2350 Auto Programming (Standalone version) ===")

# === 基本パス設定 ===
base_dir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
openocd_exe = os.path.join(base_dir, "openocd.exe").replace("\\", "/")
scripts_dir = os.path.join(base_dir, "scripts").replace("\\", "/")
firmware_path = os.path.join(base_dir, "firmware.elf").replace("\\", "/")

# === 確認 ===
if not os.path.isfile(openocd_exe):
    print(f"❌ openocd.exe が見つかりません: {openocd_exe}")
    sys.exit(1)

if not os.path.isdir(scripts_dir):
    print(f"❌ scripts フォルダが見つかりません: {scripts_dir}")
    sys.exit(1)

if not os.path.isfile(firmware_path):
    print(f"❌ firmware.elf が見つかりません: {firmware_path}")
    sys.exit(1)

# === 自動チップ検出 ===
def detect_chip():
    print("\n🔍 デバイス自動検出中...")
    cfg_list = [("RP2040", "target/rp2040.cfg"), ("RP2350", "target/rp2350.cfg")]
    for name, cfg in cfg_list:
        cmd = [
            openocd_exe,
            "-s", scripts_dir,
            "-f", "interface/cmsis-dap.cfg",
            "-f", cfg,
            "-c", "adapter speed 5000",
            "-c", "init; shutdown"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {name} デバイスを検出しました（正常応答）。")
            return cfg
        else:
            print(f"ℹ️ {name} では応答なし（returncode={result.returncode}）")
    print("⚠️ 自動判定に失敗しました。RP2040 として続行します。")
    return "target/rp2040.cfg"

target_cfg = detect_chip()

# === 書き込み速度設定 ===
speed = 20000

# === OpenOCDコマンド構築 ===
cmd_write = [
    openocd_exe,
    "-s", scripts_dir,
    "-f", "interface/cmsis-dap.cfg",
    "-f", target_cfg,
    "-c", f"adapter speed {speed}",
    "-c", f'init; program "{firmware_path}" verify; reset init; resume; shutdown'
]

print(f"\n=== Programming ({target_cfg.split('/')[-1].replace('.cfg','')}) @ {speed}kHz ===")
print(" ".join(cmd_write))

# === 実行 ===
result = subprocess.run(cmd_write)

# === 結果判定 ===
if result.returncode == 0:
    print(f"✅ 書き込み＋自動再起動完了！（{target_cfg}）")
else:
    print("⚠️ 書き込みに失敗しました。")
    sys.exit(result.returncode)

sys.exit(result.returncode)
