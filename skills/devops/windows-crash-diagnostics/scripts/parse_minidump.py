#!/usr/bin/env python3
"""免 WinDbg 依赖的 Windows 64-bit Minidump (DUMP_HEADER64) 快速解析器。"""

import glob
import os
import struct
import sys
from pathlib import Path

BUGCHECK_NAMES = {
    0x0000000A: "IRQL_NOT_LESS_OR_EQUAL (通常为高 IRQL 下非法内存访问；高频原因：CPU/Cache 激进欠压或驱动冲突)",
    0x0000001E: "KMODE_EXCEPTION_NOT_HANDLED (内核模式未处理异常，如 0xC0000005 访问违规)",
    0x0000003B: "SYSTEM_SERVICE_EXCEPTION (系统服务异常，多见于显卡/GUI 驱动栈)",
    0x00000050: "PAGE_FAULT_IN_NONPAGED_AREA (引用非分页内存池中的无效地址)",
    0x0000007E: "SYSTEM_THREAD_EXCEPTION_NOT_HANDLED (系统线程未捕获异常)",
    0x0000009F: "DRIVER_POWER_STATE_FAILURE (驱动程序电源状态转换挂起/超时)",
    0x000000D1: "DRIVER_IRQL_NOT_LESS_OR_EQUAL (驱动程序在高 IRQL 访问可分页内存)",
    0x00000116: "VIDEO_TDR_FAILURE (GPU 超时检测与恢复失败，显卡驱动卡死)",
    0x00000124: "WHEA_UNCORRECTABLE_ERROR (不可纠正的硬件总线/CPU/PCIe 架构错误)",
    0x00000133: "DPC_WATCHDOG_VIOLATION (DPC 看门狗超时，单驱动占用单核时间过长)",
    0x00000139: "KERNEL_SECURITY_CHECK_FAILURE (内核安全检测失败，如链表破坏/缓冲区溢出)",
    0x00000192: "KERNEL_AUTO_BOOST_LOCK_ACQUISITION_WITH_RAISED_IRQL (锁竞争异常)",
}

def analyze_dump(dump_path: str):
    p = Path(dump_path)
    if not p.is_file():
        print(f"[错误] 文件不存在: {dump_path}")
        return

    size = p.stat().st_size
    with open(p, "rb") as f:
        header = f.read(0x1000)

    if len(header) < 0x80:
        print(f"[错误] 文件头损坏或过短 ({len(header)} bytes)")
        return

    sig, valid = struct.unpack_from("<4s4s", header, 0)
    sig_str = sig.decode("ascii", "replace")
    valid_str = valid.decode("ascii", "replace")

    print(f"==================================================")
    print(f"转储文件: {p.resolve()} ({size / 1024:.1f} KB)")
    print(f"转储签名: {sig_str} / {valid_str}")

    if sig == b"PAGE" and valid in (b"DU64", b"SD64"):
        # 64-bit Kernel Dump / Minidump
        bc = struct.unpack_from("<I", header, 0x38)[0]
        p1, p2, p3, p4 = struct.unpack_from("<4Q", header, 0x40)
        ps_loaded = struct.unpack_from("<Q", header, 0x20)[0]
        bc_name = BUGCHECK_NAMES.get(bc, "UNKNOWN_BUGCHECK")

        print(f"BugCheck: 0x{bc:08X} - {bc_name}")
        print(f"  Param 1: 0x{p1:016X} (引用地址 / 异常代码)")
        print(f"  Param 2: 0x{p2:016X} (中断级别 IRQL / 状态码)")
        print(f"  Param 3: 0x{p3:016X} (读写标志 0=Read, 1=Write, 8=Execute)")
        print(f"  Param 4: 0x{p4:016X} (故障指令地址 RIP)")
        print(f"  PsLoadedModuleList: 0x{ps_loaded:016X}")

        if bc == 0x0A:
            print("\n[诊断建议]")
            if p2 == 0xFF:
                print("  -> Param2 为 0xFF (HIGH_LEVEL)，CPU 在最高中断级别尝试读取无效地址 0x%016X。" % p1)
                print("  -> 极高概率是 CPU 核心或缓存降压（Undervolt）过激，导致微小位翻转（欠压寻址错误）。")
                print("  -> 检查是否有 ThrottleStop、XTU 等后台调压工具，回调 30%~50% 电压余量。")
            else:
                print("  -> 在 IRQL %d 下访问无效内存，请排查近期更新的硬件驱动程序。" % p2)
    else:
        print("[提示] 该转储不是标准的 64 位 PAGE/DU64 格式（可能为 MDMP 或其他格式）")
    print(f"==================================================")

def main():
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        default_dir = r"C:\Windows\Minidump"
        dumps = sorted(glob.glob(os.path.join(default_dir, "*.dmp")), key=os.path.getmtime)
        if not dumps:
            print(f"[提示] 默认目录 {default_dir} 下未发现 .dmp 转储文件。")
            print("用法: python parse_minidump.py <path_to_dump.dmp>")
            return
        target = dumps[-1]
        print(f"[自动选中最新转储文件]: {target}")

    analyze_dump(target)

if __name__ == "__main__":
    main()
