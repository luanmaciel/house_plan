# house_plan

Orquestrador multiagente para projeto de interiores com raciocínio espacial. A planta baixa entra como PDF vetorial, DWG ou imagem. Saem caixas úteis por cômodo em metros, produtos reais que cabem nessas caixas, um layout validado por regra de circulação e documentos HTML/PDF com plantas em SVG.

Os dados do apartamento de exemplo (plantas, fotos, saídas geradas) não acompanham o repositório.

## O que faz

Lê uma planta e devolve, para cada cômodo, o retângulo interno e os retângulos onde um móvel pode ficar sem invadir a varredura da porta, a faixa da janela ou o corredor mínimo de 0,60 m. Em cima disso, busca produtos reais com medida do fabricante, posiciona cada peça em metros, prova a circulação com um simulador e escreve o memorial. Os desenhos são SVG gerados por código, nunca à mão. O caso de uso original foi a reforma de um apartamento para um casal 60+, então as regras ergonômicas (NBR 9050 como referência, frente de armário, altura de uso) estão embutidas nas checagens.

## Arquitetura

O orquestrador é o Claude na sessão do Claude Code. Ele chama os co-agentes em sequência, passa JSON de um para o outro e escreve o projeto final. Nenhum agente vê a saída do outro sem passar pelo orquestrador. Existem dois conjuntos de agentes.

### Pipeline de projeto (agents.md e system_prompts.md)

Agente 1, Espacial. Lê paredes, portas com sentido de abertura, janelas e cotas. Devolve o contrato `01_espacial` (JSON por cômodo com `interior`, `portas`, `janelas`, `existente` e `usable_bounding_boxes`). Tem duas interfaces. A interface A é `tools/espacial_from_geo.py`: sem IA, converte os vetores já medidos do PDF. A interface B é `tools/gemini_vision.py`: manda a imagem da planta ao Gemini 2.5 Pro pela API REST, com o prompt da seção 1 de `system_prompts.md`, e imprime o JSON. A precisão da B é de 5 cm na melhor hipótese, então toda cota crítica é conferida contra a cota escrita.

Agente 2, Mercado. Para cada móvel pedido, com a dimensão máxima vinda do passo 1, acha dois ou três produtos reais em e-commerce brasileiro com link, preço e medida do fabricante. Roda pelo MCP do Perplexity (`perplexity_search` e `perplexity_ask`) já conectado à sessão, uma chamada por móvel, com o prompt da seção 2 de `system_prompts.md`. Não há código Python para este agente; o orquestrador faz a chamada. Regra: medida do fabricante menor ou igual à caixa permitida, sem arredondar; sem medida na página, descarta.

Agente 3, Síntese. É o próprio orquestrador. Escolhe um produto por móvel, posiciona em metros relativos ao canto superior esquerdo interno do cômodo, roda `tools/simulador.py` até todas as checagens saírem OK e escreve `outputs/03_projeto/<projeto>.md` com conceito estético e memorial descritivo. A checklist está na seção 3 de `system_prompts.md`.

### Funil de reforma (.claude/agents)

Três subagentes do Claude Code, usados em ordem fixa quando chega uma planta nova ou uma demanda de obra.

`engenheiro-restricoes` (modelo opus). Analisa a planta ou foto e lista impedimentos estruturais, hidráulicos e elétricos, indo à causa raiz de cada um e dizendo qual verificação destrava. Não propõe layout. Entrega o bloco `[Matriz Técnica]`.

`arquiteto-usabilidade` (modelo sonnet). Recebe a matriz e desenvolve o layout para a rotina 60+ (fluxo, segurança, iluminação, ergonomia), respeitando cada restrição. Escreve as posições em metros, roda `tools/simulador.py` e só entrega quando todas as checagens passam. Entrega o bloco `[Proposta Funcional]`.

`planejador-pcp` (modelo sonnet). Recebe a proposta e monta o sequenciamento da obra, a lista de compras com lead time (porcelanato, vidro temperado, metais, MDF) e as escolhas de custo-benefício. Entrega o bloco `[Plano de Ataque]`.

Os três leem `docs/manual-plantas-layout.md` antes de começar: convenções de leitura de planta, regras de circulação com fonte e o fluxo de trabalho. O pipeline de projeto alimenta o `arquiteto-usabilidade` com produtos reais; não o substitui.

### Ferramentas (tools/)

`gemini_vision.py` imagem ou PDF da planta para JSON espacial via Gemini.
`espacial_from_geo.py` geo.json (vetores) para o contrato 01_espacial, sem IA.
`dwg_facts.py` extrai linhas, arcos de porta, textos, cotas e blocos de um DWG com ezdwg, já em metros.
`simulador.py` lê o PDF vetorial com PyMuPDF, sobrepõe o mobiliário em metros e imprime o relatório de circulação e varredura de porta; grava SVG por cômodo.
`prancheta.py` gera uma página HTML onde os móveis se arrastam dentro do cômodo, com as mesmas checagens em JavaScript e um botão que copia o layout em metros.
`plantas.py` duas plantas do apartamento inteiro em SVG (só medidas; medidas mais móveis) e PDF.
`propostas.py` mapa de fluxo, três propostas de layout validadas, proposta de elétrica com circuitos, mapa de iluminação por lux, lista de compras e tabelas de preço; página HTML e PDF.
`documento.py` monta o documento do plano de reforma a partir dos SVGs de `plantas.py` e `simulador.py`.
`estudo_acabamento.py` segundo estudo, só acabamento: geometria pelas cotas escritas da planta do prédio, proposta de cozinha planejada, quantitativos e preços.
`banheiro_foto.py` edita fotos de banheiro por máscara (numpy e Pillow) para simular piso, gabinete e espelho novos.
`banheiro_nano.py` mesma edição, mas por modelo de imagem do Gemini.

`templates/base_head.html` é o cabeçalho compartilhado (fontes e CSS) que `documento.py`, `propostas.py` e `estudo_acabamento.py` usam. `templates/banheiro_3d.html` é um visualizador Three.js das versões do banheiro.

## Como os agentes passam o trabalho

O pipeline troca arquivos JSON com contrato fixo. O agente 1 grava `outputs/01_espacial/<projeto>.json`. O orquestrador lê esse arquivo, multiplica `w_max` e `h_max` de cada caixa por 100 e preenche os placeholders `L_MAX` e `P_MAX` do prompt do agente 2; `A_MAX` vem do próprio orquestrador. A resposta do agente 2 vira `outputs/02_mercado/<projeto>.json`, uma lista de produtos por chave `comodo.uso`. O agente 3 lê os dois arquivos, posiciona, roda o simulador e escreve o `.md` final. Os dois contratos estão escritos em `agents.md`.

O funil de reforma troca blocos de texto com nome fixo. O engenheiro entrega `[Matriz Técnica]`, o arquiteto só pode projetar dentro dela e entrega `[Proposta Funcional]`, o planejador recebe a proposta e entrega `[Plano de Ataque]`. O orquestrador despacha na ordem, consolida e publica; não redesenha nada por conta própria. Cada agente pode disparar subagentes pequenos (Explore, general-purpose) para tarefas mecânicas, mas o formato de saída é sempre dele.

## Instalação e variáveis de ambiente

Python 3.11 ou mais novo (desenvolvido com 3.13).

```
pip install -r requirements.txt
copy .env.example .env
```

`GEMINI_API_KEY` é a única chave no código. É lida do ambiente ou do `.env` na raiz por `gemini_vision.py` e `banheiro_nano.py`. O Perplexity entra pelo MCP do Claude Code, sem chave no repositório.

Duas variáveis opcionais, só pelo ambiente: `HOUSE_PLAN_GEO` (caminho do geo.json da prancheta; padrão `inputs/geo.json`) e `HOUSE_PLAN_PDF` (caminho do PDF vetorial do simulador; padrão `inputs/plantas/planta.pdf`).

A conversão de HTML para PDF em `propostas.py` e `estudo_acabamento.py` usa o Edge em modo headless se ele estiver instalado no caminho padrão do Windows; sem ele, só o HTML é gerado.

## Uso

Com uma imagem da planta:

```
python tools/gemini_vision.py inputs/plantas/minha_planta.png --projeto minha_planta --usos "q1: cama_casal, criado x2"
```

Com os vetores já medidos:

```
python tools/espacial_from_geo.py inputs/geo.json --projeto minha_planta
python tools/simulador.py todos
python tools/prancheta.py
python tools/plantas.py
python tools/propostas.py
python tools/documento.py
```

Com um DWG do CAD:

```
python tools/dwg_facts.py caminho/para/planta.dwg
```

### Formato do geo.json

É o arquivo que `prancheta.py`, `plantas.py`, `propostas.py` e `espacial_from_geo.py` leem. Tudo em metros, origem no canto superior esquerdo da planta, x para a direita e y para baixo.

`W` e `H` são a largura e a altura totais. `rooms` mapeia o id do cômodo para `[x, y, largura, altura]` do interior. `doors` é uma lista de portas de abrir, cada uma com `room`, a dobradiça `hx` e `hy`, a folha `r` e o quadrante da varredura `sx` e `sy` (cada um +1 ou -1). `lines` são as paredes, `[x1, y1, x2, y2]`. `sliders` são portas de correr no mesmo formato, opcional. `projeto` e `escala_base` são opcionais e vão direto para o contrato.

Um exemplo sintético pequeno: um retângulo de 6,00 por 4,00 m com dois cômodos, uma sala de 3,60 por 4,00 à esquerda e um quarto de 2,25 por 4,00 à direita, separados por uma parede de 0,15. O quarto tem uma porta de 0,70 na parede divisória, dobradiça no canto inferior, abrindo para dentro e para cima.

```
{
  "projeto": "exemplo",
  "W": 6.0, "H": 4.0,
  "rooms": {"sala": [0.0, 0.0, 3.6, 4.0], "q1": [3.75, 0.0, 2.25, 4.0]},
  "doors": [{"room": "q1", "hx": 3.75, "hy": 4.0, "r": 0.7, "sx": 1, "sy": -1}],
  "lines": [[0, 0, 6, 0], [6, 0, 6, 4], [6, 4, 0, 4], [0, 4, 0, 0], [3.6, 0, 3.6, 4], [3.75, 0, 3.75, 3.3]],
  "sliders": []
}
```

Rodando `espacial_from_geo.py` sobre esse arquivo, o quarto sai com a porta na parede oeste, varredura de 0,70 por 0,70 no canto inferior esquerdo e uma caixa útil de 2,25 por 3,30 acima dela.

A lista de móveis de `prancheta.py` e os ids de cômodo em `plantas.py` e `propostas.py` são os do apartamento de exemplo (`banho`, `nicho`, `q1`, `q1alc`, `q2`, `sala_top`, `sala_bot`, `hall`, `entrada`, `cozinha`, `lavanderia`, `lavabo`, `escritorio`, `varanda`). Para outra planta, troque a lista `items` e os dicionários de nomes. Os retângulos de cômodo em `simulador.py` estão em pontos do PDF e precisam ser remedidos nos vetores de cada planta nova.

## Saída

`outputs/01_espacial/<projeto>.json`, `outputs/02_mercado/<projeto>.json` e `outputs/03_projeto/<projeto>.md` são os três estágios do pipeline. A pasta `out/` recebe os SVGs por cômodo, as plantas do apartamento inteiro, `prancheta.html`, `propostas.html`, `plano.html`, `acabamento.html` e os PDFs correspondentes. As duas pastas estão no `.gitignore`.

O relatório do simulador sai no terminal, uma linha por checagem, no formato `[OK ] nome: valor m (mín. x)` ou `[ATENÇÃO]` quando o mínimo não é atendido.

## Limitações

A leitura por imagem (Gemini) erra 5 cm ou mais e não substitui a cota escrita. Os vetores do PDF não trazem o sentido de abertura das portas quando a planta não desenha o arco; esse dado vem do levantamento no local. `espacial_from_geo.py` gera uma caixa útil única por cômodo e ainda ignora janelas; o refinamento por uso fica no orquestrador com o simulador. As posições, os ids de cômodo e as checagens em `simulador.py`, `prancheta.py` e `propostas.py` são específicos da planta de exemplo e precisam ser reescritos para outra planta. O Perplexity depende de MCP conectado na sessão do Claude Code. Os preços nas tabelas foram pesquisados na web em datas fixas e envelhecem. Nada aqui substitui o responsável técnico da obra.

## Licença

MIT. Veja `LICENSE`.
