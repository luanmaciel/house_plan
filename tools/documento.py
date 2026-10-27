"""Gera out/plano.html: documento do plano de reforma sobre os SVGs de plantas.py e simulador.py."""
import os, re
here = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(here), "out")
head = open(os.path.join(os.path.dirname(here), "templates", "base_head.html"), encoding="utf-8").read()

def svg(name):
    s = open(os.path.join(OUT, name), encoding="utf-8").read()
    return s.replace('<svg xmlns="http://www.w3.org/2000/svg"', '<svg xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;border-radius:10px;"')

hidr_path = os.path.join(OUT, "hidraulica.html")
hidr = open(hidr_path, encoding="utf-8").read() if os.path.exists(hidr_path) else \
    '<p class="muted">Leitura do projeto hidráulico do prédio pendente. Esta seção é preenchida por out/hidraulica.html quando a rota do esgoto estiver confirmada.</p>'

html = f'''<title>Plano de reforma</title>
{head}
<style>
  @page {{ size: A4; margin: 14mm 12mm; }}
  @media print {{
    body {{ background: #fff; padding: 0; font-size: 12.5px; }}
    .wrap {{ max-width: none; }}
    header {{ padding-top: 0; }}
    section {{ margin-top: 28px; }}
    .schema, .fase, .callout, .check, .ficha div, .sw {{ break-inside: avoid; }}
    .schema svg {{ max-height: 150mm; width: auto; max-width: 100%; margin: 0 auto; }}
    .ficha .cota {{ white-space: normal; }}
    .ficha div, .fase, .check, .sw, .opt {{ box-shadow: none; }}
    a {{ color: inherit; text-decoration: none; }}
  }}
</style>

<div class="wrap">

<header>
  <p class="eyebrow">Plano de reforma · rev. 05/09/2026</p>
  <h1>Plano de reforma</h1>
  <p class="standfirst">Plano da reforma sobre a planta medida no local (SolidWorks, escala 1:20), com foco no que vai ser feito primeiro: banheiro e os dois quartos. Os desenhos saem de uma ferramenta que lê os vetores da planta e valida circulação por regra. Os móveis de todos os cômodos estão nas posições escolhidas na prancheta interativa (<code>out/prancheta.html</code>, dá para arrastar e testar).</p>
</header>

<section id="ficha">
  <hr class="rule">
  <p class="eyebrow">O apartamento em números</p>
  <h2>Medidas da planta</h2>
  <div class="ficha">
    <div><b>Sala (em L) · 17,4 m²</b><span class="cota">3,75 × 5,60 · 2,73 no fundo</span></div>
    <div><b>Entrada · 1,3 m²</b><span class="cota">1,50 × 0,88</span></div>
    <div><b>Cozinha · 8,7 m²</b><span class="cota">2,36 × 3,69</span></div>
    <div><b>Lavanderia · 4,9 m²</b><span class="cota">2,36 × 2,08</span></div>
    <div><b>Lavabo · 1,6 m²</b><span class="cota">1,66 × 0,98</span></div>
    <div><b>Quarto/escritório · 4,9 m²</b><span class="cota">1,66 × 2,97</span></div>
    <div><b>Varanda · 3,0 m²</b><span class="cota">2,73 × 1,10</span></div>
    <div><b>Banheiro · 3,5 m²</b><span class="cota">1,66 × 1,71 + nicho 0,70 × 1,00</span></div>
    <div><b>Quarto 1 · 11,7 m²</b><span class="cota">3,63 × 2,78 + alcova do armário 0,86 × 1,87</span></div>
    <div><b>Quarto 2 · 10,1 m²</b><span class="cota">3,63 × 2,78 · armário 0,50 na parede do hall</span></div>
    <div><b>Portas de abrir</b><span class="cota">banheiro 0,80 · quartos 0,70 · escritório e lavabo 0,60 · entrada 0,83</span></div>
    <div><b>Portas de correr</b><span class="cota">cozinha 0,70 e 1,50 · varanda 1,40</span></div>
    <div><b>Área interna total</b><span class="cota">67,2 m² (soma dos cômodos, sem paredes e hall)</span></div>
    <div><b>Pé-direito*</b><span class="cota">2,45 m</span></div>
    <div><b>Elevador*</b><span class="cota">1,20×1,20 · porta 0,80 · alt. 2,20</span></div>
  </div>
  <p class="muted" style="margin-top:14px; font-size:.9rem;">Fonte: planta medida no local (folha 1 cotada, folha 2 limpa) e desenhada em SolidWorks. Os itens com * vêm do levantamento anterior. O CAD da construtora foi aposentado como fonte: divergia na porta e no nicho do banheiro e no lado da janela do quarto 2.</p>

  <div class="callout">
    <h3>Decisões fechadas</h3>
    <ul class="lista-solta">
      <li><strong>Fonte de medidas:</strong> a planta medida no local. Trena a laser só confere antes de fábrica e hidráulica.</li>
      <li><strong>Banheiro:</strong> box novo na faixa da janela e porta existente de 0,80 mantida. A posição do vaso (nicho ou canto do coletor) sai da vistoria do contrapiso, com as duas versões já desenhadas.</li>
      <li><strong>Chuveiro:</strong> elétrico. Circuito dedicado, disjuntor e DR entram na etapa de elétrica.</li>
      <li><strong>Quartos:</strong> queen no quarto 1, bicama com mesa de computador no quarto 2. Os armários existentes dos dois quartos (portas de correr) ficam; reforma só por dentro.</li>
      <li><strong>Portas:</strong> todas de abrir, com o raio de abertura livre de móveis, exceto a da cozinha (correr).</li>
      <li><strong>Ordem:</strong> fechar banheiro e quartos primeiro; os demais cômodos só depois que os moradores se sentirem seguros nesses dois.</li>
    </ul>
  </div>
</section>

<section id="geral">
  <hr class="rule">
  <p class="eyebrow">Planta 1</p>
  <h2>O apartamento só com as medidas</h2>
  <p>Paredes, portas e janelas são os vetores da planta. Cada cômodo traz a medida interna (largura × profundidade, em metros, de face a face de parede). Leques = raio de abertura das portas de abrir; tracejado verde = portas de correr (cozinha e varanda).</p>
  <figure class="schema">
    {svg("cotas.svg")}
    <figcaption>Gerado por <code>tools/plantas.py</code> a partir dos vetores da planta. Serve para conferir com a trena antes de comprar qualquer móvel.</figcaption>
  </figure>
</section>

<section id="mobiliado">
  <hr class="rule">
  <p class="eyebrow">Planta 2</p>
  <h2>O apartamento com os móveis planejados</h2>
  <p>Todos os cômodos, nas posições fechadas em 05/09 na prancheta e validadas pelo simulador (13 checagens de circulação, varredura de porta e frente de armário, todas aprovadas). Marrom = armários e bancada existentes; cinza-escuro = camas e sofá; contorno tracejado = cadeiras e a cama auxiliar puxada (só à noite).</p>
  <figure class="schema">
    {svg("mobiliado.svg")}
    <figcaption>Gerado por <code>tools/plantas.py</code> com as mesmas posições da prancheta. Cozinha: bancada existente na parede da sala, começando na parede da lavanderia; geladeira e mesa de café na parede oposta, com 1,06 m de corredor. Sala: sofá na parede da cozinha, rack e TV na parede do banheiro, mesa de jantar para 6 na parte da frente. Escritório: mesa na cabeceira da cama de solteiro, 0,77 m livres ao lado.</figcaption>
  </figure>
</section>

<section id="banheiro">
  <hr class="rule">
  <p class="eyebrow">Prioridade 1 · Banheiro</p>
  <h2>Box na janela; vaso no nicho ou junto ao coletor</h2>
  <p>O banheiro tem área principal de <span class="cota">1,66 × 1,71</span>, o nicho do box atual de <span class="cota">0,70 × 1,00</span> no canto da parede da sala (boca cheia, sem dentes), porta de <span class="cota">0,80</span> na parede do hall abrindo para dentro (dobradiça no batente da direita, folha na parede do quarto 2) e janela de <span class="cota">1,00</span> na parede externa. Hoje o vaso fica na parede da sala e o chuveiro no nicho, sem janela: o vapor fica preso e o box é apertado.</p>
  <h3>Versão 1 · vaso no nicho (proposta inicial)</h3>
  <p>Box novo de <span class="cota">1,66 × 0,90</span> na faixa da janela, chuveiro na ponta da parede da sala, ralo linear, banco e barra; porta de vidro de 0,80 na ponta do hall; vaso com caixa acoplada de <span class="cota">0,38 × 0,68</span> no nicho, com barras nas duas laterais; pia de <span class="cota">0,60 × 0,45</span> na parede da sala. Circulação validada: 0,81 entre o box e a parede do hall, 1,21 à frente da pia, varredura da porta livre. <strong>Condição:</strong> o contrapiso precisa ter altura para o tubo de 100 mm correr do nicho até o coletor com caimento de 2%.</p>
  <figure class="schema">
    {svg("banho.svg")}
    <figcaption>Versão 1, gerada por <code>tools/simulador.py</code> sobre a planta. Limite: a boca do nicho tem 0,70 (a NBR 9050 pede 0,80); confortável para uso autônomo com barras nos dois lados, não atende cadeira de rodas.</figcaption>
  </figure>
  <h3>Versão 2 · vaso fica junto ao coletor (hidráulica mínima)</h3>
  <p>Se a vistoria mostrar que não há altura para o caimento, o vaso permanece no canto entre a parede da sala e a janela, exatamente sobre o ponto de coleta, com a caixa acoplada encostada na parede da janela e <span class="cota">0,90</span> livres à frente. O box novo fica com <span class="cota">0,96 × 0,90</span> no restante da faixa da janela, separado do vaso por uma meia-parede de alvenaria (que segura a barra do lado do vaso; vidro não segura barra) e com porta de vidro de 0,68 voltada para a porta do banheiro. A pia vai para o nicho (<span class="cota">0,70 × 0,45</span>), que ganha espelho e iluminação de tarefa. Obra hidráulica: só a pia muda de lugar e o ralo do box aproveita o segundo ponto de piso existente.</p>
  <figure class="schema">
    {svg("banho_v2.svg")}
    <figcaption>Versão 2, gerada por <code>tools/simulador.py</code>. Checagens: box 0,96 × 0,90, 0,90 livres à frente do vaso, 0,81 de corredor, pia de 0,70 no nicho, varredura da porta livre. Limite: o box fica 5 cm abaixo dos 0,95 de profundidade que a NBR 9050 sugere com banco.</figcaption>
  </figure>

  <h3>Hidráulica: o que decide o custo</h3>
  <p>Pia e chuveiro usam tubos finos e mudam de lugar com facilidade. O vaso precisa de um tubo de 100 mm com caimento de 2% até a prumada do prédio, e é a única parte cara. O projeto hidráulico do edifício responde onde está essa prumada e por onde corre o ramal atual.</p>
  {hidr}
  <div class="check">
    <h3>Verificar antes de contratar (decide entre V1 e V2)</h3>
    <ol>
      <li><strong>Prancha original da hidráulica</strong> com o síndico, administradora ou construtora: PDF ou foto de 300 dpi só do detalhe A e da legenda. É lá que estão os diâmetros (Ø100/Ø75/Ø50/Ø40) e as siglas (TQ, CS, RS).</li>
      <li><strong>Abrir um ponto do contrapiso</strong> junto ao vaso atual: medir o enchimento disponível e a cota de topo do tubo de 100 mm existente. O trajeto até o nicho precisa de uns 12 a 15 cm; degrau no piso está vetado.</li>
      <li><strong>Localizar a prumada</strong> por percussão ou inspeção no canto da parede da sala junto à parede externa, e conferir se está embutida na alvenaria ou em shaft.</li>
      <li><strong>Trena a laser no nicho</strong> (confirmar 0,70 × 1,00) e percussão nas suas paredes: se for shaft, o vaso no nicho fica trivial.</li>
      <li><strong>Condomínio e NBR 16280:</strong> plano de reforma com responsável técnico (ART/RRT) e aviso ao síndico; intervenção em prumada coletiva exige janela de corte de água.</li>
      <li><strong>Impermeabilização</strong> refeita na área molhada inteira, com teste de estanqueidade de 72 h antes do revestimento.</li>
      <li><strong>Elétrica do chuveiro:</strong> circuito dedicado, disjuntor e DR; medir a reserva do quadro e a bitola do alimentador.</li>
    </ol>
  </div>

  <div class="callout">
    <h3>Kit 60+ que entra de qualquer jeito</h3>
    <ul class="lista-solta">
      <li>Barras de apoio no box e ao lado do vaso, fixadas em reforço (150 kg).</li>
      <li>Piso antiderrapante (R10 ou mais). Nada de tapete solto.</li>
      <li>Ducha manual em barra deslizante e misturador monocomando de alavanca.</li>
      <li>Banco no box; assento sanitário mais alto (borda em torno de 46 cm).</li>
      <li>Exaustor acionado junto com a luz; luz de vigília com sensor no hall dos quartos.</li>
      <li>Opcional: trocar a porta por correr ou abrindo para o hall, para facilitar socorro.</li>
    </ul>
  </div>
  <p><strong>Alternativa mínima</strong> se nem a versão 2 couber no orçamento: manter as louças onde estão, trocar o box por vidro até perto do teto com porta mais ampla, instalar exaustor e o kit 60+. Resolve vapor e segurança por uma fração do custo, mas o box continua com 0,70 e sem janela.</p>
</section>

<section id="quartos">
  <hr class="rule">
  <p class="eyebrow">Prioridade 2 · Quartos</p>
  <h2>Quarto 1 com queen, quarto 2 com bicama e mesa</h2>
  <h3>Quarto 1 · <span class="cota">3,63 × 2,78</span></h3>
  <p>O armário existente ocupa a alcova de <span class="cota">0,86 × 1,87</span> na parede do hall e fica (portas de correr; reforma só interna). A queen de <span class="cota">1,58 × 1,98</span> encosta a cabeceira na parede de cima, com criado dos dois lados, <span class="cota">1,03</span> de passagem do lado do armário, <span class="cota">1,02</span> do lado da janela e <span class="cota">0,80</span> no pé. A porta de 0,70 no canto de baixo da parede do hall abre para dentro com a folha na parede de baixo, longe de tudo.</p>
  <h3>Quarto 2 · <span class="cota">3,63 × 2,78</span></h3>
  <p>O armário existente (<span class="cota">0,50 × 1,90</span>, portas de correr) fica na parede do hall, logo abaixo da varredura da porta. A bicama de <span class="cota">1,88 × 0,88</span> corre pela parede de baixo, a <span class="cota">0,65</span> da frente do armário e a <span class="cota">0,60</span> da parede da janela; a cama auxiliar puxa para o meio do quarto, onde há <span class="cota">1,90</span> livres. A mesa de computador de <span class="cota">1,00 × 0,50</span> fica na parede de cima, no canto da janela, com <span class="cota">1,40</span> para a cadeira durante o dia; à noite, com a auxiliar puxada, a cadeira sobe para a mesa. Criado vira prateleira suspensa e luminária de parede na cabeceira.</p>
  <figure class="schema">
    {svg("quartos.svg")}
    <figcaption>Gerado por <code>tools/simulador.py</code> sobre a planta, com os armários existentes marcados no levantamento e as posições fechadas na prancheta. Todas as checagens de circulação e varredura de porta passaram.</figcaption>
  </figure>
  <div class="callout">
    <h3>Dentro dos armários (reforma interna, 60+)</h3>
    <ul class="lista-solta">
      <li>Roupa do dia a dia entre 0,40 e 1,40 m do chão: gavetões telescópicos e prateleiras nessa faixa.</li>
      <li>Cabideiro a no máximo 1,60 m ou puxa-cabide nas partes altas. Maleiro só para o raro.</li>
      <li>Puxadores de alça ou cava, LED com sensor dentro do armário.</li>
    </ul>
  </div>
</section>

<section id="demais">
  <hr class="rule">
  <p class="eyebrow">Próxima etapa</p>
  <h2>Demais cômodos</h2>
  <p>Cozinha (2,36 × 3,69: bancada existente com pia, fogão e exaustor na parede da sala; geladeira e mesa de café de 0,80 × 0,50 na parede oposta), lavanderia (tanque e máquina na parede do fundo), lavabo, quarto/escritório (1,66 × 2,97: mesa de 1,00 × 0,45 na cabeceira da cama de solteiro), sala (sofá de 2,10 na parede da cozinha, rack de 1,80 na parede do banheiro, mesa de jantar para 6 lugares de 1,60 × 0,90 na frente) e varanda (mesinha) já têm posição na planta 2, e entram na obra depois que o banheiro e os quartos estiverem fechados. A linha geral segue a mesma: manter caixaria existente e trocar só o que muda o uso diário (gavetões nos módulos baixos, micro-ondas na altura da bancada, LED sob os aéreos, torneira de alavanca), e nada de uso diário acima do ombro nem abaixo do joelho. Se quiserem mudar alguma posição, a prancheta continua aberta: arrastem, copiem o layout e rodem o simulador.</p>
</section>

<section id="fases">
  <hr class="rule">
  <p class="eyebrow">Estratégia</p>
  <h2>O que fazer, em que ordem</h2>
  <ol class="fases">
    <li class="fase"><span class="fase-num">0</span><div><h3>Papelada e orçamentos</h3><p>Plano de reforma (NBR 16280) com responsável técnico, autorização do condomínio, 2 a 3 orçamentos por serviço.</p><p class="por-que">Evita embargo e dá poder de negociação.</p></div></li>
    <li class="fase"><span class="fase-num">1</span><div><h3>Quebra-quebra antes da mudança</h3><p>Banheiro, pontos elétricos novos, exaustor, luz de vigília, pintura geral.</p><p class="por-que">Obra com apê vazio custa menos e ninguém vive na poeira.</p></div></li>
    <li class="fase"><span class="fase-num">2</span><div><h3>Mudança</h3><p>Com banheiro e pintura prontos, os armários existentes já servem.</p><p class="por-que">Morar antes da marcenaria é tranquilo; o contrário não.</p></div></li>
    <li class="fase"><span class="fase-num">3</span><div><h3>Marcenaria dos quartos</h3><p>Reforma interna dos armários existentes, cabeceiras, mesa do quarto 2. Medição final com a obra limpa.</p><p class="por-que">MDF não entra em ambiente com poeira e umidade de obra.</p></div></li>
    <li class="fase"><span class="fase-num">4</span><div><h3>Cozinha e demais cômodos</h3><p>Gavetões, nicho do micro-ondas, LED de bancada, frentes se sobrar verba.</p><p class="por-que">Tudo modular: dá para fazer em etapas.</p></div></li>
    <li class="fase"><span class="fase-num">5</span><div><h3>Decoração</h3><p>Painel verde em arco na sala (tinta + prateleira) e canto alemão terracota na área de jantar, feitos pela marcenaria parceira.</p><p class="por-que">A parte mais barata de adiar.</p></div></li>
  </ol>
</section>

<section id="logistica">
  <hr class="rule">
  <p class="eyebrow">Detalhe que salva a obra</p>
  <h2>O elevador é pequeno</h2>
  <div class="callout terra"><p>Cabine de <span class="cota">1,20 × 1,20</span>, porta de <span class="cota">0,80</span>, altura <span class="cota">2,20</span>. Chapa inteira de MDF não entra: tudo pré-cortado na oficina, módulos com no máximo ~2,10 m de altura. Vale para sofá e colchão: conferir a diagonal antes de comprar.</p></div>
</section>

<section id="paleta">
  <hr class="rule">
  <p class="eyebrow">Estilo</p>
  <h2>Paleta</h2>
  <div class="swatches">
    <figure class="sw"><div class="sw-chip" style="background:#8A6A4F"></div><figcaption><b>LOURO FREIJÓ</b>madeira · frentes e painéis</figcaption></figure>
    <figure class="sw"><div class="sw-chip" style="background:#A79A82"></div><figcaption><b>DUST</b>neutro quente · caixaria</figcaption></figure>
    <figure class="sw"><div class="sw-chip" style="background:#D6CDB4"></div><figcaption><b>NEVADA</b>claro · interiores</figcaption></figure>
    <figure class="sw"><div class="sw-chip" style="background:#9A9C9B"></div><figcaption><b>NIMBÓ</b>cinza · contraste</figcaption></figure>
    <figure class="sw"><div class="sw-chip" style="background:#6E7F62"></div><figcaption><b>VERDE DO PAINEL</b>tinta · parede da TV</figcaption></figure>
    <figure class="sw"><div class="sw-chip" style="background:#BC6A4A"></div><figcaption><b>TERRACOTA</b>tinta · canto alemão</figcaption></figure>
  </div>
  <p style="margin-top:18px;"><strong>Contraste é conforto</strong> para olhos 60+: bancada contrastando com o piso, puxador com a porta, assento do vaso com o piso do banheiro; luz quente (2700 a 3000 K) forte nas áreas de tarefa.</p>
</section>

<footer>
  Fonte de geometria: planta medida no local (SolidWorks, 1:20). Desenhos e validações por <code>tools/simulador.py</code> e <code>tools/plantas.py</code>; regras em <code>docs/manual-plantas-layout.md</code> (circulação mínima 0,60; frente de armário de correr 0,65; NBR 9050 como referência de acessibilidade). Faixas de custo são relativas; pedir sempre 2 a 3 orçamentos. Guia de conversa, não substitui o responsável técnico da obra.
</footer>

</div>
'''
out = os.path.join(OUT, "plano.html")
os.makedirs(OUT, exist_ok=True)
open(out, "w", encoding="utf-8").write(html)
print("plano.html:", len(html) // 1024, "KB")
