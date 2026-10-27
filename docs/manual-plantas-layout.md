# Manual: ler a planta e propor layout (reforma residencial)

Leitura obrigatória para os agentes `engenheiro-restricoes`, `arquiteto-usabilidade` e `planejador-pcp` antes de qualquer análise ou desenho.

## 1. Regra zero: nunca redesenhar paredes de cabeça

**Fonte oficial: o PDF vetorial da planta medida no local, folha limpa** (desenho em CAD na escala 1:20, 141,73 pt/m, sem calibração); a folha cotada traz as medidas. Vetores extraídos com PyMuPDF (`page.get_drawings()`): linhas = paredes; aberturas (portas/janelas) aparecem como linhas tracejadas curtas, sem arco, então o sentido de abertura vem do levantamento no local. O CAD da construtora (PDF/DWG, 31,49 pt/m) fica como referência secundária. Desenho de proposta é sempre `python tools/simulador.py`, que sobrepõe mobiliário em metros sobre a planta real e imprime a validação de circulação. Se um cômodo ainda não estiver no simulador, primeiro medem-se seus limites internos nos vetores (interior = face interna das paredes) e só depois se posiciona móvel.

## 2. Como ler os símbolos (convenções)

- **Paredes**: duas linhas paralelas; a face interna é o limite útil do cômodo. Internas em geral com 0,15 a 0,20 m (aqui 0,20).
- **Portas**: vão na parede + arco de um quarto de círculo. O arco mostra o sentido e o lado de abertura: o centro do arco é a dobradiça; a folha aberta encosta na parede que sai da dobradiça. **Tudo o que estiver dentro do quarto de círculo é varrido pela porta.** Portas de correr têm símbolo próprio (folha paralela à parede, sem arco).
- **Janelas**: linhas finas interrompendo a parede (aqui, retângulo hachurado em vermelho). Não recebem móvel alto na frente.
- Sequência de leitura: contorno externo → paredes internas → portas (com sentido) → janelas → circulação que sobra.
- Fontes: [Planner 5D, simbologia de planta baixa](https://planner5d.com/blog/pt/simbologia-de-planta-baixa/); [Pormade, guia de símbolos e posicionamento de portas](https://blog.pormade.com.br/2026/05/25/planta-baixa-guia-completo-com-simbolos/); [EdrawMax, símbolos de planta](https://edraw.wondershare.com.br/floor-plan-symbols.html).

## 3. Fatos fixos do apartamento (medidos nos vetores)

Tabela por cômodo com interior (m), porta (vão, parede, dobradiça e sentido), janela e observações. A tabela do apartamento de exemplo fica fora deste repositório; preencha a da sua planta antes de rodar o simulador.

## 4. Regras de layout (mínimos, com fonte)

**Dormitórios** ([Dicas de Arquitetura](https://dicasdearquitetura.com.br/medidas-ideais-no-quarto/), [Blog Inusual](https://blog.inusual.com.br/circulacao-dormitorios/), [Galeria da Arquitetura](https://blog.galeriadaarquitetura.com.br/2024/08/09/medidas-ideais-quarto/)):
- Circulação mínima: **0,60 m** (uma unidade de passagem); confortável 0,60 a 0,80.
- Laterais da cama: ≥ 0,60 de cada lado; pé da cama até parede: ≥ 0,60.
- Frente de armário: **0,65 (portas de correr)**, **0,80 (portas de abrir)**.
- Nada de móvel dentro da varredura da porta; a folha aberta precisa encostar na parede.
- Camas: solteiro 0,88 × 1,88; casal 1,38 × 1,88; queen 1,58 × 1,98.
- Bicama (cama com auxiliar retrátil embaixo): precisa de um lado longo livre de ≥ 0,90 para puxar a auxiliar; nada fixo nesse lado (criado vira prateleira suspensa). Mesa de computador: 1,00 a 1,20 × 0,55 a 0,60, com 0,75 a 0,90 livres para a cadeira.
- Não colocar mesa/apoio no meio da circulação. Móvel solto só encostado em parede e fora dos fluxos porta → cama → armário.

**Banheiro para 60+** (referência [NBR 9050 resumo UFPR](https://exatas.ufpr.br/degraf_arabella/wp-content/uploads/sites/28/2016/03/NBR-9050_2015.pdf), [BHG Engenharia](https://www.bhgengenharia.com/banheiro-acessivel-nbr-9050/), [O2 Multi](https://o2multi.com.br/banheiro-nbr-9050/)):
- Bacia: assento a 0,44 a 0,46 m; barras laterais de 0,80 a 0,75 m de altura; barra traseira a 0,89 m. Área ideal de transferência 0,80 × 1,20 (quando não cabe, a meta realista é boca ≥ 0,80 com barras dos dois lados).
- Box: mínimo 0,90 × 0,95 com banco; ideal aberto (walk-in) ou com porta de vidro larga; barras dentro do box; piso R10+.
- Porta: vão livre ≥ 0,80 na norma; se a existente for menor, registrar a limitação (porta de correr ou abrindo para fora é a mitigação).
- Giro de 1,50 m não cabe: registrar como limite, não fingir que atende.

**Ergonomia 60+ (marcenaria e cozinha)**: zona de conforto 0,40 a 1,40 m; cabideiro ≤ 1,60 ou puxa-cabide; gavetões telescópicos; nada de uso diário acima do ombro ou abaixo do joelho; LED com sensor; contraste entre planos.

## 5. Fluxo de trabalho para uma planta nova

1. `engenheiro-restricoes`: extrair vetores, calibrar escala, listar cômodos com interior, portas (dobradiça + sentido), janelas, prumadas prováveis (paredes molhadas). Entregar `[Matriz Técnica]`.
2. `arquiteto-usabilidade`: propor layout em metros relativos ao canto interno de cada cômodo; rodar `tools/simulador.py`; corrigir até todas as checagens ficarem OK; anexar o relatório à `[Proposta Funcional]`.
3. `planejador-pcp`: sequenciar e comprar a partir do layout validado. Entregar `[Plano de Ataque]`.
4. Orquestrador (Claude): despacha na ordem, consolida e publica; não redesenha nada por conta própria.

## 6. Fonte preferencial de geometria: o DWG (ezdwg)

`pip install ezdwg` lê o DWG do CAD (AC1032) diretamente, **já em metros**, sem calibrar escala. `python tools/dwg_facts.py <planta.dwg>` exporta para `out/dwg_facts.json`: linhas (paredes), arcos de porta (centro = dobradiça, raio = folha, ângulos = sentido), textos dos cômodos, cotas reais (`actual_measurement`) e blocos (bacia, janela 1200, bancada, cadeira). O DWG de exemplo não tinha camadas nomeadas (tudo na camada 0), então a leitura é por geometria e blocos, não por layer. Próximo passo natural do simulador é ler daqui em vez do PDF.

## 7. Ferramentas externas avaliadas (02/09/2026)

| Ferramenta | O que faz | Veredito para este projeto |
|---|---|---|
| [ezdwg](https://github.com/monozukuri-ai/ezdwg) (PyPI) | Lê DWG R14 a R2018 em Python | **Adotada**: lê nosso DWG em metros, com arcos de porta, cotas e blocos |
| [ezdxf](https://ezdxf.readthedocs.io/) | Lê/escreve DXF, renderiza | Útil se alguém exportar DXF; ezdwg já cobre o DWG |
| [qcad-mcp](https://github.com/sandraschi/qcad-mcp) | MCP com parsing DXF/DWG, detecção de cômodos, portas e janelas (núcleo grátis via ezdxf; QCAD Pro opcional) | Candidato para automatizar a leitura da planta inteira; pré-release, exige Python 3.13 + uv |
| [aiblueprint-mcp](https://github.com/thebossnow/aiblueprint-mcp) | MCP que **gera** DXF (ezdxf + LibreCAD) | Não lê planta existente; serve só para desenhar o projeto executivo no fim |
| [AutoCAD_MCP](https://github.com/ahmetcemkaraca/AutoCAD_MCP), [multiCAD-mcp](https://github.com/AnCode666/multiCAD-mcp), [CAD-MCP](https://github.com/daobataotie/CAD-MCP) | MCPs que controlam software CAD instalado | Dependem de AutoCAD/CAD licenciado; fora do escopo |
| [interior-design-expert](https://github.com/curiositech/some_claude_skills/blob/main/.claude/skills/interior-design-expert/SKILL.md) (skill) | Regras de circulação (900-1200 primária, 600-900 secundária, 450 mínimo), folgas de mobiliário, iluminação por lux e temperatura de cor | **Regras absorvidas** neste manual; instalar a skill é opcional |
| [skills-for-architects](https://github.com/AlpacaLabsLLC/skills-for-architects) | Skills de escritório de arquitetura (programa, especificações, FF&E; foco NYC/corporativo) | Não cobre residencial/acessibilidade; não adotar |
| [homemaker](https://github.com/bayllama/homemaker) | Casa em 3D navegável com Claude Code, editor de planta a partir de imagem 2D, 500+ móveis | Opcional para os moradores "passearem" pelo projeto; não substitui a validação em planta |
| Floor-plan skills de marketplace (DrawIO stencils, each::sense API) | Geram plantas genéricas | Não partem da planta real; não adotar |

Regras extra absorvidas da skill interior-design-expert: circulação primária 0,90 a 1,20, secundária 0,60 a 0,90, aperto mínimo 0,45; iluminação de tarefa 300 a 500 lux (leitura/mesa), dormitório 50 a 150 lux ambiente, 2700 a 3000 K à noite.
