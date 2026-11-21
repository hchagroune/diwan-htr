"""Minimal QR code generator (byte mode, error correction level M) that writes an inline SVG.

Used once to pre-generate the pitch's QR code so the site needs no external service.
Usage: python tools/qr.py "https://example.org/demo/" > docs/assets/qr-demo.svg
"""
import sys

# --- Reed-Solomon over GF(256) -----------------------------------------------------------
EXP, LOG = [0] * 512, [0] * 256
x = 1
for i in range(255):
    EXP[i] = x
    LOG[x] = i
    x <<= 1
    if x & 0x100:
        x ^= 0x11D
for i in range(255, 512):
    EXP[i] = EXP[i - 255]


def gmul(a, b):
    return 0 if a == 0 or b == 0 else EXP[LOG[a] + LOG[b]]


def rs_generator(degree):
    g = [1]
    for i in range(degree):
        g = [a ^ gmul(b, EXP[i]) for a, b in zip(g + [0], [0] + g)]
    return g  # highest degree first


def rs_remainder(data, degree):
    gen = rs_generator(degree)
    res = list(data) + [0] * degree
    for i in range(len(data)):
        coef = res[i]
        if coef:
            for j in range(1, len(gen)):
                res[i + j] ^= gmul(gen[j], coef)
    return res[len(data):]


# --- Version tables for level M (versions 1-10) ------------------------------------------
# (ec codewords per block, [(blocks, data codewords per block), ...])
M_TABLE = {
    1: (10, [(1, 16)]), 2: (16, [(1, 28)]), 3: (26, [(1, 44)]), 4: (18, [(2, 32)]),
    5: (24, [(2, 43)]), 6: (16, [(4, 27)]), 7: (18, [(4, 31)]), 8: (22, [(2, 38), (2, 39)]),
    9: (22, [(3, 36), (2, 37)]), 10: (26, [(4, 43), (1, 44)]),
}
ALIGN = {1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34], 7: [6, 22, 38],
         8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50]}


def build(text):
    data = text.encode("utf-8")
    ver = None
    for v in range(1, 11):
        ec, groups = M_TABLE[v]
        cap = sum(n * d for n, d in groups)
        cc_bits = 8 if v < 10 else 16
        if 4 + cc_bits + 8 * len(data) <= cap * 8:
            ver = v
            break
    if ver is None:
        raise ValueError("text too long")
    ec, groups = M_TABLE[ver]
    cap = sum(n * d for n, d in groups)
    cc_bits = 8 if ver < 10 else 16
    bits = "0100" + format(len(data), f"0{cc_bits}b") + "".join(format(b, "08b") for b in data)
    bits += "0" * min(4, cap * 8 - len(bits))
    bits += "0" * (-len(bits) % 8)
    words = [int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)]
    i = 0
    while len(words) < cap:
        words.append(0xEC if i % 2 == 0 else 0x11)
        i += 1

    # split into blocks, add EC, interleave
    blocks, pos = [], 0
    for n, d in groups:
        for _ in range(n):
            blk = words[pos:pos + d]
            pos += d
            blocks.append((blk, rs_remainder(blk, ec)))
    out = []
    for k in range(max(len(b[0]) for b in blocks)):
        for blk, _ in blocks:
            if k < len(blk):
                out.append(blk[k])
    for k in range(ec):
        for _, e in blocks:
            out.append(e[k])

    size = 17 + 4 * ver
    grid = [[None] * size for _ in range(size)]
    func = [[False] * size for _ in range(size)]

    def setf(r, c, v):
        grid[r][c] = v
        func[r][c] = True

    def finder(r0, c0):
        for r in range(-1, 8):
            for c in range(-1, 8):
                rr, cc = r0 + r, c0 + c
                if 0 <= rr < size and 0 <= cc < size:
                    on = (0 <= r <= 6 and 0 <= c <= 6 and
                          (r in (0, 6) or c in (0, 6) or (2 <= r <= 4 and 2 <= c <= 4)))
                    setf(rr, cc, on)

    finder(0, 0)
    finder(0, size - 7)
    finder(size - 7, 0)
    for k in range(8, size - 8):
        setf(6, k, k % 2 == 0)
        setf(k, 6, k % 2 == 0)
    al = ALIGN[ver]
    for r in al:
        for c in al:
            if func[r][c]:
                continue
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    setf(r + dr, c + dc, max(abs(dr), abs(dc)) != 1)
    # reserve format areas and dark module
    for k in range(9):
        if not func[8][k]:
            setf(8, k, False)
        if not func[k][8]:
            setf(k, 8, False)
    for k in range(8):
        setf(8, size - 1 - k, False)
        setf(size - 1 - k, 8, False)
    setf(size - 8, 8, True)
    if ver >= 7:
        raise ValueError("version info not implemented; keep the URL short")

    # place data bits (zigzag)
    allbits = "".join(format(w, "08b") for w in out)
    idx = 0
    c = size - 1
    upward = True
    while c > 0:
        if c == 6:
            c -= 1
        rows = range(size - 1, -1, -1) if upward else range(size)
        for r in rows:
            for cc in (c, c - 1):
                if not func[r][cc]:
                    grid[r][cc] = idx < len(allbits) and allbits[idx] == "1"
                    idx += 1
        upward = not upward
        c -= 2

    masks = [
        lambda r, c: (r + c) % 2 == 0, lambda r, c: r % 2 == 0, lambda r, c: c % 3 == 0,
        lambda r, c: (r + c) % 3 == 0, lambda r, c: (r // 2 + c // 3) % 2 == 0,
        lambda r, c: (r * c) % 2 + (r * c) % 3 == 0, lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
        lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0,
    ]

    def format_bits(mask):
        data5 = (0b00 << 3) | mask  # level M = 00
        rem = data5
        for _ in range(10):
            rem = (rem << 1) ^ ((rem >> 9) * 0x537)
        return ((data5 << 10) | rem) ^ 0x5412

    def apply(mask):
        g = [row[:] for row in grid]
        for r in range(size):
            for cc in range(size):
                if not func[r][cc] and masks[mask](r, cc):
                    g[r][cc] = not g[r][cc]
        fb = format_bits(mask)
        b = [(fb >> i) & 1 == 1 for i in range(15)]
        for i in range(6):
            g[i][8] = b[i]
        g[7][8] = b[6]
        g[8][8] = b[7]
        g[8][7] = b[8]
        for i in range(9, 15):
            g[8][14 - i] = b[i]
        for i in range(8):
            g[8][size - 1 - i] = b[i]
        for i in range(8, 15):
            g[size - 15 + i][8] = b[i]
        g[size - 8][8] = True
        return g

    def penalty(g):
        p = 0
        for lines in (g, list(zip(*g))):
            for row in lines:
                run, prev = 0, None
                for v in row:
                    if v == prev:
                        run += 1
                    else:
                        if run >= 5:
                            p += run - 2
                        run, prev = 1, v
                if run >= 5:
                    p += run - 2
                s = "".join("1" if v else "0" for v in row)
                p += 40 * (s.count("10111010000") + s.count("00001011101"))
        for r in range(size - 1):
            for cc in range(size - 1):
                if g[r][cc] == g[r][cc + 1] == g[r + 1][cc] == g[r + 1][cc + 1]:
                    p += 3
        dark = sum(v for row in g for v in row)
        p += abs(dark * 20 - size * size * 10) // (size * size) * 10
        return p

    best = min(range(8), key=lambda m: penalty(apply(m)))
    return apply(best)


def to_svg(g, label):
    n = len(g)
    q = 4
    path = []
    for r, row in enumerate(g):
        for c, v in enumerate(row):
            if v:
                path.append(f"M{c + q} {r + q}h1v1h-1z")
    total = n + 2 * q
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total} {total}" role="img" '
            f'aria-label="{label}" shape-rendering="crispEdges"><rect width="{total}" height="{total}" fill="#ffffff"/>'
            f'<path d="{"".join(path)}" fill="#111a2d"/></svg>')


if __name__ == "__main__":
    url = sys.argv[1]
    print(to_svg(build(url), "QR code: " + url))
