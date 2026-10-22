"""Gera os logos da Soul Fit em SVG vetorial (letras convertidas em caminhos).

Proporções medidas nos prints originais dos stories (@studio_soulfit).
Fonte: Liberation Sans (SIL OFL), métrica equivalente à Arial/Helvetica.
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FONTES = "/usr/share/fonts/truetype/liberation/"
BOLD = TTFont(FONTES + "LiberationSans-Bold.ttf")
REG = TTFont(FONTES + "LiberationSans-Regular.ttf")


def glifo(font, ch):
    gs = font.getGlyphSet()
    nome = font.getBestCmap()[ord(ch)]
    g = gs[nome]
    bp = BoundsPen(gs)
    g.draw(bp)
    return gs, g, bp.bounds, g.width


def cap(font):
    return font["OS/2"].sCapHeight


def linha_justificada(font, texto, x0, largura, topo, altura):
    """Desenha `texto` com as maiúsculas de `altura`, a primeira letra
    encostada em x0 e a última terminando em x0+largura (tracking uniforme)."""
    k = altura / cap(font)
    itens = [glifo(font, c) for c in texto]
    # largura natural: da borda esquerda do 1º glifo à borda direita do último
    avancos = [w * k for (_, _, _, w) in itens]
    b0 = itens[0][2]
    bn = itens[-1][2]
    natural = sum(avancos[:-1]) - b0[0] * k + bn[2] * k
    t = (largura - natural) / (len(itens) - 1)
    x = x0 - b0[0] * k
    base = topo + altura
    partes = []
    for (gs, g, b, w), ch in zip(itens, texto):
        if ch != " ":
            pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
            g.draw(TransformPen(pen, (k, 0, 0, -k, x, base)))
            partes.append(pen.getCommands())
        x += w * k + t
    return " ".join(partes)


def fit_espalhado(font, x0, largura, topo, altura, centro_i=0.5):
    """F encostado à esquerda, T encostado à direita, I no centro."""
    k = altura / cap(font)
    base = topo + altura
    partes = []
    for ch, alvo in (("F", "esq"), ("I", "meio"), ("T", "dir")):
        gs, g, b, w = glifo(font, ch)
        if alvo == "esq":
            x = x0 - b[0] * k
        elif alvo == "dir":
            x = x0 + largura - b[2] * k
        else:
            x = x0 + largura * centro_i - (b[0] + b[2]) / 2 * k
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        g.draw(TransformPen(pen, (k, 0, 0, -k, x, base)))
        partes.append(pen.getCommands())
    return " ".join(partes)


def montar(spec):
    """`peso` engrossa as letras de SOUL/FIT com um contorno da mesma cor
    (a Liberation Regular fica com o traço médio do logo original).
    O contorno cresce para fora, então desenhamos dentro da caixa."""
    W = spec["largura"]
    H = spec["altura"]
    e = spec.get("peso", 0)
    m = e / 2
    soul = linha_justificada(spec["fonte_soul"], "SOUL", m, W - e, spec["soul_topo"] + m, spec["cap"] - e)
    fe = spec.get("peso_fit", e)
    mf = fe / 2
    fit = fit_espalhado(spec["fonte_fit"], mf, W - fe, spec["fit_topo"] + mf, spec["cap"] - fe)
    sub = linha_justificada(spec["fonte_sub"], spec["sub"], 0, W, spec["sub_topo"], spec["sub_cap"])
    return dict(W=W, H=H, soul=soul, fit=fit, sub=sub, peso=e, peso_fit=fe,
                linha=(0, spec["linha_topo"], W, spec["linha_esp"]))


# Medidas em "pixels do print" multiplicadas por 10 para trabalhar com inteiros.
ACADEMIA = montar(dict(
    largura=1630, altura=1310, cap=450, peso=26,
    fonte_soul=REG, fonte_fit=REG, fonte_sub=REG,
    soul_topo=0, fit_topo=570,
    linha_topo=1095, linha_esp=18,
    sub="ACADEMIA", sub_topo=1180, sub_cap=130,
))

STUDIO = montar(dict(
    largura=800, altura=650, cap=220, peso=20, peso_fit=0,
    fonte_soul=REG, fonte_fit=REG, fonte_sub=BOLD,
    soul_topo=0, fit_topo=300,
    linha_topo=556, linha_esp=10,
    sub="PERSONAL  STUDIO", sub_topo=600, sub_cap=50,
))


def letras(logo, fill, stroke):
    def p(d, e):
        if not e:
            return f'<path {fill} d="{d}"/>'
        return f'<path {fill} {stroke} stroke-width="{e}" stroke-linejoin="miter" d="{d}"/>'
    return p(logo["soul"], logo["peso"]) + p(logo["fit"], logo["peso_fit"])


def arquivo(logo, titulo, cor_letras, cor_linha, cor_sub):
    x, y, w, h = logo["linha"]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {logo["W"]} {logo["H"]}" '
        f'role="img" aria-label="{titulo}">\n'
        f'  <title>{titulo}</title>\n'
        + letras(logo, f'fill="{cor_letras}"', f'stroke="{cor_letras}"') +
        f'  <rect fill="{cor_linha}" x="{x}" y="{y}" width="{w}" height="{h}"/>\n'
        f'  <path fill="{cor_sub}" d="{logo["sub"]}"/>\n'
        f'</svg>\n'
    )


def simbolo(logo, id_, titulo):
    """<symbol> para usar inline: as cores vêm do CSS (currentColor e variáveis)."""
    x, y, w, h = logo["linha"]
    return (
        f'<symbol id="{id_}" viewBox="0 0 {logo["W"]} {logo["H"]}">'
        f'<title>{titulo}</title>'
        + letras(logo, 'fill="currentColor"', 'stroke="currentColor"') +
        f'<rect style="fill:var(--logo-linha, currentColor)" x="{x}" y="{y}" width="{w}" height="{h}"/>'
        f'<path style="fill:var(--logo-sub, currentColor)" d="{logo["sub"]}"/>'
        f'</symbol>'
    )


if __name__ == "__main__":
    destino = sys.argv[1]
    VERDE, BRANCO, PRETO, CINZA = "#8EDB00", "#F4F5F6", "#111214", "#C9CCD1"
    saidas = {
        "logo-academia.svg": arquivo(ACADEMIA, "Soul Fit Academia", VERDE, VERDE, VERDE),
        "logo-academia-branco.svg": arquivo(ACADEMIA, "Soul Fit Academia", BRANCO, VERDE, BRANCO),
        "logo-studio.svg": arquivo(STUDIO, "Soul Fit Personal Studio", BRANCO, VERDE, CINZA),
        "logo-studio-escuro.svg": arquivo(STUDIO, "Soul Fit Personal Studio", PRETO, VERDE, PRETO),
    }
    for nome, svg in saidas.items():
        open(f"{destino}/{nome}", "w", encoding="utf-8").write(svg)
    sprite = (
        '<svg width="0" height="0" style="position:absolute" aria-hidden="true">'
        + simbolo(ACADEMIA, "logo-academia", "Soul Fit Academia")
        + simbolo(STUDIO, "logo-studio", "Soul Fit Personal Studio")
        + "</svg>"
    )
    open(f"{destino}/_sprite.html", "w", encoding="utf-8").write(sprite)
    print("ok", list(saidas), len(sprite), "bytes de sprite")
