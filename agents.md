# Orquestração: design de interiores com raciocínio espacial

Claude (esta sessão) é o orquestrador. Ele chama os co-agentes em sequência, passa JSON de um para o outro e escreve o projeto final. Nenhum agente vê o output do outro sem passar pelo orquestrador.

```
imagem/PDF da planta
   │
   ▼
[1] ESPACIAL ──► outputs/01_espacial/<projeto>.json   (usable_bounding_boxes)
   │              vetores (tools/espacial_from_geo.py) quando há PDF/DWG
   │              Gemini Vision (tools/gemini_vision.py) quando só há imagem
   ▼
[2] MERCADO ───► outputs/02_mercado/<projeto>.json     (2-3 produtos reais por móvel)
   │              Perplexity via MCP (perplexity_search / perplexity_ask)
   ▼
[3] SÍNTESE ───► outputs/03_projeto/<projeto>.md       (conceito + memorial)
                  Claude; valida circulação com tools/simulador.py
```

## Agente 1: Espacial (Gemini ou vetores)

| | |
|---|---|
| Papel | Ler paredes, portas (com sentido de abertura), janelas e cotas; devolver, por cômodo, o retângulo interno em metros e as caixas onde um móvel pode ficar sem invadir varredura de porta, janela ou circulação de 0,60 m. |
| Interface A (preferida) | `python tools/espacial_from_geo.py` (grava `outputs/01_espacial/<projeto>.json`). Sem IA, sem erro de leitura: usa os vetores do PDF já medidos. |
| Interface B | `python tools/gemini_vision.py inputs/plantas/x.png > outputs/01_espacial/x.json`. REST `generativelanguage.googleapis.com`, modelo `gemini-2.5-pro`, prompt em `system_prompts.md`. |
| Variáveis | `GEMINI_API_KEY` (só a interface B). Coloque em `.env` (ignorado pelo git). |
| Limitação | O conector MCP `consultar_gemini` é texto puro; imagem só pela interface B. A precisão da B é de ±5 cm na melhor hipótese: toda cota crítica (porta, box, cama) deve ser conferida contra a cota escrita na planta antes de ir para o passo 2. |

## Agente 2: Mercado (Perplexity)

| | |
|---|---|
| Papel | Para cada móvel pedido, com dimensão máxima em L×P×A vinda do passo 1, achar 2 a 3 produtos reais em e-commerce brasileiro com link, preço e medidas do fabricante. |
| Interface | MCP já conectado nesta sessão: `perplexity_search` (lista de URLs) e `perplexity_ask` (resposta com citações). Uma chamada por móvel, prompt em `system_prompts.md`. |
| Variáveis | Nenhuma extra (o MCP já está autenticado). |
| Regra | Medida do fabricante ≤ caixa permitida, sem arredondar. Sem medida na página do produto = descartar. Preço e link sempre da mesma página. |

## Agente 3: Síntese (Claude)

| | |
|---|---|
| Papel | Escolher um produto por móvel, posicionar em metros (canto superior esquerdo interno do cômodo), rodar `tools/simulador.py` para provar circulação e varredura de porta, e escrever o `.md` final. |
| Entradas | `outputs/01_espacial/*.json` + `outputs/02_mercado/*.json` + `docs/manual-plantas-layout.md` (mínimos ergonômicos com fonte). |
| Saída | `outputs/03_projeto/<projeto>.md` com: conceito estético (paleta, texturas, estilo) e memorial descritivo (para cada móvel: onde fica, produto, link, preço, justificativa de ergonomia, funcionalidade e estética). SVG de layout em `out/`. |

## Contratos de dados

**01_espacial** (saída do agente 1, entrada do 2):
```json
{
  "projeto": "exemplo", "unidade": "m", "escala_confianca": "vetorial|estimada",
  "rooms": {
    "q1": {
      "interior": {"x": 9.509, "y": 0.265, "w": 3.634, "h": 2.778},
      "portas": [{"parede": "oeste", "vao": 0.7, "abre_para": "dentro", "varredura": {"x":..,"y":..,"w":..,"h":..}}],
      "janelas": [{"parede": "leste", "vao": 1.2}],
      "existente": [{"nome": "armario", "x":..,"y":..,"w":..,"h":..}],
      "usable_bounding_boxes": [
        {"uso": "cama_casal", "x":..,"y":..,"w_max":1.6,"h_max":2.0, "encosta": "norte"}
      ]
    }
  }
}
```

**02_mercado** (saída do agente 2, entrada do 3):
```json
{
  "q1.cama_casal": [
    {"produto": "...", "loja": "...", "url": "https://...", "preco_brl": 1899.0,
     "medidas_cm": {"l": 158, "p": 203, "a": 110}, "cabe": true, "observacao": "..."}
  ]
}
```

## Agentes locais já existentes (.claude/agents)

`engenheiro-restricoes` → `arquiteto-usabilidade` → `planejador-pcp` continuam valendo para o funil de reforma (restrições de obra, rotina 60+, sequenciamento). O pipeline acima alimenta o `arquiteto-usabilidade` com produtos reais; não o substitui.

## Estudo de acabamento

`python tools/estudo_acabamento.py` gera um segundo documento a partir das cotas escritas da planta do prédio (planta de medidas, proposta da cozinha, quantitativos, HTML e PDF). Escopo só de acabamento; o pipeline acima e os três agentes continuam disponíveis, com o estudo anterior marcado como histórico.
