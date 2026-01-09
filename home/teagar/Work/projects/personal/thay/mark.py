#!/usr/bin/env python3
import sys
import time
import os

def main():
    intervals = []
    start = time.monotonic()
    last = start

    is_windows = os.name == 'nt'

    if is_windows:
        import msvcrt
        def kb_hit():
            return msvcrt.kbhit()
        def getch():
            b = msvcrt.getch()
            try:
                return b.decode('utf-8', errors='ignore')
            except:
                return ''
    else:
        import termios, tty, select
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        def kb_hit():
            return bool(select.select([sys.stdin], [], [], 0)[0])
        def getch():
            return sys.stdin.read(1)

    print("Cronômetro iniciado. [ESPAÇO] para salvar intervalo, [x] para sair.")
    try:
        while True:
            now = time.monotonic()
            elapsed_ms = int((now - start) * 1000)  # tempo em ms
            m = elapsed_ms // 60000
            s = (elapsed_ms % 60000) // 1000
            ms = elapsed_ms % 1000
            sys.stdout.write(f"\r{m:02d}:{s:02d}.{ms:03d}")
            sys.stdout.flush()

            if kb_hit():
                ch = getch()
                if ch == ' ':
                    interval_ms = int((now - last) * 1000)
                    intervals.append(interval_ms)
                    last = now
                    if is_windows:
                        sys.stdout.write(f"  (salvo {interval_ms}ms)")
                        sys.stdout.flush()
                        time.sleep(0.25)
                    else:
                        sys.stdout.write(f"  (salvo {interval_ms}ms)\n")
                        sys.stdout.flush()
                elif ch.lower() == 'x':
                    break
            time.sleep(0.08)
    except KeyboardInterrupt:
        pass
    finally:
        if not is_windows:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    print("\nIntervalos registrados (ms):")
    if intervals:
        print(" ".join(str(i) for i in intervals))
    else:
        print("(nenhum intervalo)")

if __name__ == '__main__':
    main()
