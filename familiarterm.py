#!/usr/bin/env python3
"""familiarterm - a colorful ASCII creature that lives in your terminal."""
import os, sys, time, random, subprocess, termios, tty, select, shutil, re

ESC = "\033["
RESET = ESC + "0m"
def rgb(r,g,b): return f"{ESC}38;2;{r};{g};{b}m"
def fg(n): return f"{ESC}38;5;{n}m"

GRAD = [(255,176,58),(255,108,158),(167,108,255),(82,196,255),(108,255,176),(255,176,58)]
def grad(t):
    t = t % 1.0
    n = len(GRAD)-1
    seg = t*n; i = int(seg); f = seg-i
    a=GRAD[i]; b=GRAD[i+1] if i+1<len(GRAD) else GRAD[0]
    return (int(a[0]+(b[0]-a[0])*f), int(a[1]+(b[1]-a[1])*f), int(a[2]+(b[2]-a[2])*f))

# ---------- creature ----------
FACES = {
    "idle":    [("o","o","~")],
    "happy":   [("^","^","v")],
    "excited": [(">","<","O"), ("<",">","O")],
    "sleep":   [("-","-","."), ("z","z",".")],
    "tired":   [("-","-","_"), (".",".","_")],
    "love":    [("^","^","<3")],
    "dance":   [("o","O","~"), ("O","o","~")],
    "sad":     [("T","T","/\\")],
}

SPEECH = {
    "idle": ["...", "hmm", "what's up", "bored", "hi"],
    "happy": ["yay!", ":)", "nice!", "keep going", "cool"],
    "excited": ["WOOO!", ":D", "AAAA", "FASTER!", "LET'S GO"],
    "sleep": ["zzz...", "mmh...", "5 more min", "*snore*"],
    "tired": ["ugh", "so tired", "need coffee", "hmm.."],
    "love": ["<3", "uwu", "you rock", "nice one"],
    "dance": ["~music~", "beat!", "vibe~", "bumpin'", "\\o/"],
    "sad": [":(", "aww", "why..", "hmm."],
}

def vlen(s): return len(re.sub(r"\x1b\[[0-9;]*[A-Za-z]","",s))

def colorize_line(line, phase):
    out = ""
    n = len(line) or 1
    for i,ch in enumerate(line):
        if ch == " ": out += ch
        else:
            c = rgb(*grad((phase + i/n*0.4) % 1.0))
            out += c + ch
    return out + RESET

INNER = 19
def build_body(el, er, m):
    # row 1: eyes
    r1 = list(" " * INNER)
    r1[2] = el
    r1[8] = er
    # mouth: center-ish
    for i,ch in enumerate(m):
        if 13 + i < INNER: r1[13 + i] = ch
    # row 2: blank
    r2 = [" "] * INNER
    # assemble
    return [
        "\u256d" + "\u2500" * INNER + "\u256e",
        "\u2502" + "".join(r1) + "\u2502",
        "\u2502" + "".join(r2) + "\u2502",
        "\u2570" + "\u252c" + "\u2500" * (INNER//2 - 1) + "\u2534" + "\u2500" * (INNER - INNER//2 - 1) + "\u252c" + "\u256f",
        "   \u2502" + " " * (INNER - 4) + "\u2502   ",
        "  \u2571 \u2572" + " " * (INNER - 4) + "\u2571 \u2572  ",
    ]

def draw(state, name, phase):
    face = FACES.get(state, FACES["idle"])
    idx = int(time.time()*1.5) % len(face)
    el, er, m = face[idx]
    body = build_body(el, er, m)
    out = [colorize_line(ln, phase) for ln in body]
    lbl = f"~ {name} ~"
    c = rgb(*grad((phase+0.5)%1.0))
    out.append("")
    out.append(" " * max(0, (INNER - len(lbl))//2) + c + lbl + RESET)
    return out

# ---------- sensors ----------
def cpu_pct(prev):
    try:
        with open("/proc/stat") as f:
            v = [int(x) for x in f.readline().split()[1:]]
        idle, total = v[3]+v[4], sum(v)
        if prev:
            dp = 100*(1-(idle-prev[0])/(total-prev[1]))
            return max(0,min(100,dp)), (idle,total)
        return 0, (idle,total)
    except: return 0, None

def now_playing():
    try:
        st = subprocess.check_output(["playerctl","metadata","--format","{{status}}|{{artist}} - {{title}}"],
                stderr=subprocess.DEVNULL, timeout=0.3).decode().strip()
        if "|" in st:
            status, meta = st.split("|",1)
            if status.lower()=="playing":
                return True, meta[:40]
        return False, ""
    except: return False, ""

def uptime_of_proc(t0):
    s = int(time.time() - t0)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {s}s" if h else f"{m}m {s}s"

# ---------- main ----------
def main():
    name = os.environ.get("USER","blip")
    if len(sys.argv) > 1: name = sys.argv[1]

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    prev_cpu = None
    last_keys = time.time()
    key_count = 0
    last_song_check = 0
    playing, song = False, ""
    speech = ""
    speech_until = 0
    t0 = time.time()

    try:
        tty.setcbreak(fd)
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
        while True:
            r,_,_ = select.select([fd],[],[],0.05)
            if r:
                ch = os.read(fd,1)
                if ch in (b"q", b"\x03"): break
                key_count += 1
                last_keys = time.time()

            pct, prev_cpu = cpu_pct(prev_cpu)
            now = time.time()
            if now - last_song_check > 2:
                playing, song = now_playing()
                last_song_check = now

            since_key = now - last_keys
            hour = time.localtime().tm_hour

            if playing:                state = "dance"
            elif pct > 60:             state = "excited"
            elif since_key < 0.5:      state = "happy"
            elif hour >= 22 or hour < 6: state = "sleep"
            elif since_key > 45:       state = "tired"
            else:                      state = "idle"

            if since_key < 0.2:
                state = random.choice(["happy","excited","love"])

            # speech bubble
            if now > speech_until:
                speech = random.choice(SPEECH.get(state, SPEECH["idle"]))
                speech_until = now + random.uniform(3.0, 6.0)

            cols, rows = shutil.get_terminal_size((60,20))
            phase = (now * 0.02) % 1.0
            body = draw(state, name, phase)
            bubble = f"{fg(245)}\u256d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e{RESET}"
            bubble2 = f"{fg(245)}\u2502 {speech:<5} \u2502{RESET}"
            bubble3 = f"{fg(245)}\u2570\u2500\u2500\u256f{RESET}"

            # stats
            mood_c = rgb(*grad(phase))
            cpu_bar_w = 12
            fill = int(pct/100*cpu_bar_w)
            cpu_bar = f"{mood_c}{'█'*fill}{fg(238)}{'░'*(cpu_bar_w-fill)}{RESET}"
            song_line = f"{fg(214)}\u266b {song}{RESET}" if playing else ""
            stats = [
                f"  {mood_c}state{RESET}  {state:<8}  {mood_c}key{RESET} {key_count}",
                f"  {mood_c}cpu{RESET}    {pct:5.1f}%  {cpu_bar}",
                f"  {mood_c}up{RESET}     {uptime_of_proc(t0)}",
            ]
            if song_line: stats.append(f"  {song_line}")

            screen = []
            for i in range(3):
                screen.append(body[i])
            screen.append("")
            screen.append("   " + bubble)
            screen.append("   " + bubble2)
            screen.append("   " + bubble3)
            for i in range(3, len(body)):
                screen.append(body[i])
            screen.append("")
            screen += stats
            screen.append("")
            screen.append(f"  {fg(240)}q quit{RESET}")

            out = "\033[H\033[2J" + "\n".join(screen)
            sys.stdout.write(out)
            sys.stdout.flush()
            time.sleep(0.20)
    except KeyboardInterrupt: pass
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, old)
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
