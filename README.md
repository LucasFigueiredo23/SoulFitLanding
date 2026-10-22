# Soul Fit · landing page

Site da Soul Fit (Castanhal, PA), com as duas unidades: **Studio** (personal só seu) e **Academia** (personais no salão).
HTML, CSS e JS puros, sem build. Hospedado no Cloudflare como site estático (Workers Static Assets).

## Estrutura

```
soulfit-site/
├── public/                  ← tudo que vai para o ar
│   ├── index.html           ← página inteira (HTML + CSS + JS)
│   ├── 404.html             ← página de endereço não encontrado
│   ├── _headers             ← cache e cabeçalhos de segurança (lido pelo Cloudflare)
│   ├── robots.txt
│   └── assets/              ← logos SVG e fotos
├── ferramentas/
│   └── gerar_logos.py       ← gera os logos SVG (Python + fontTools)
├── wrangler.jsonc           ← configuração do Cloudflare
├── package.json             ← scripts e versão do Wrangler
└── .gitignore
```

## Rodar e publicar

Precisa de Node.js 18 ou mais novo.

```bash
npm install            # instala o Wrangler
npx wrangler login     # abre o navegador para entrar na conta Cloudflare (só na primeira vez)
npm run dev            # site local em http://localhost:8787
npm run check          # confere a configuração sem publicar
npm run deploy         # publica
```

Depois do primeiro `deploy`, o site fica em `https://soulfit.<sua-conta>.workers.dev`.
Para usar um domínio próprio: painel do Cloudflare → Workers & Pages → soulfit → Settings → Domains & Routes.

### Publicar a cada push no GitHub (opcional)

1. Suba esta pasta para um repositório no GitHub.
2. No painel do Cloudflare: Workers & Pages → Create → Import a repository.
3. Deploy command: `npx wrangler deploy`. Build command: deixe vazio.

## Onde mexer

| O quê | Onde |
| --- | --- |
| Número e mensagens do WhatsApp | fim do `public/index.html`: `var WHATSAPP` e `MENSAGENS` |
| Cores e fontes | bloco `:root` no início do `<style>` |
| Fotos do hero | `<div class="foto">` dentro de `.u-studio` e `.u-academia` |
| Enquadramento da foto do Studio | `.u-studio .foto img { object-position }` |
| Logos | `<symbol>` no começo do `<body>`; cores via `color`, `--logo-linha` e `--logo-sub` |
| Pendências (endereço da Academia, dias, aula experimental) | procure por `class="pendente"` |

## Logos

Recriados em SVG a partir dos prints dos stories, com a fonte Liberation Sans (licença SIL OFL, proporções da Arial/Helvetica).
Arquivos em `public/assets/`: `logo-academia.svg`, `logo-academia-branco.svg`, `logo-studio.svg`, `logo-studio-escuro.svg`.

Para gerar de novo:

```bash
pip install fonttools
python ferramentas/gerar_logos.py ferramentas/saida
```

Depois copie os `.svg` de `ferramentas/saida/` para `public/assets/`. O `_sprite.html` gerado junto é o bloco `<symbol>` para colar no `index.html`.

O script usa as fontes em `/usr/share/fonts/truetype/liberation/` (Linux). Em outro sistema, ajuste a variável `FONTES` no começo do arquivo.
Se o cliente tiver o arquivo original do logo, substitua pelos oficiais.

## Antes da versão final

- [ ] Endereço e dias de funcionamento da Academia
- [ ] Aula experimental: existe ou não
- [ ] Fotos originais em alta resolução (as atuais vieram de print)
- [ ] Tags de pré-visualização (Open Graph) quando o domínio final estiver definido
- [ ] Testar todos os botões de WhatsApp no celular
