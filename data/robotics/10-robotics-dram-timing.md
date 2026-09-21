Yes. These fit the bottleneck thesis extremely well, but they sit on two different branches of it.

The framework we built was essentially: **AI makes cognition/design progressively cheaper → value migrates into whatever physical resource is hardest to scale next**. We had the migration roughly as cognition → verification → experimentation → manufacturing → packaging/interconnect → energy, with companies like LPKF/SUSS/Nynomic appearing because physical validation and precision become scarce after software intelligence becomes abundant. The robotics extension is now obvious: **intelligence → embodiment → reliable motion**, and that creates a new node I would explicitly add:

**Physical intelligence → motors → reducers + encoders + bearings + torque sensing.**

Meanwhile, on the compute branch:

**accelerators → HBM/DRAM capacity → packaging → optical I/O → power.**

That makes these four unusually relevant.

| Name         | Bottleneck exposure                                           |      Thesis fit | Convexity |        Valuation concern | My view                         |
| ------------ | ------------------------------------------------------------- | --------------: | --------: | -----------------------: | ------------------------------- |
| **ALNT**     | motors + encoders + gearing + controls + data-center power    |      **9.5/10** |  **9/10** |                     High | **Most interesting**            |
| **TKR**      | harmonic/cycloidal reducers + encoders + bearings             |      **9.5/10** |      7/10 |                 Moderate | **Best risk/reward**            |
| **NOVT**     | precision encoders + torque sensing + motors + motion control |        **9/10** |    7.5/10 |            **Very high** | Exceptional business, expensive |
| **DRAM ETF** | DRAM/HBM/NAND/storage                                         | **10/10 today** |      7/10 | Cycle already recognized | Excellent thesis basket         |

### ALNT — this one jumps out

Allient is much more interesting than I initially expected.

It effectively builds the nervous system + muscle/control layer of machines: nano-precision positioning, servo systems, motors, drives, gearing, **absolute and incremental optical encoders**, controllers and integrated actuators. Allient itself describes integrated products containing motors, gearboxes, encoders and motor drivers. ([SEC][1])

And look at its description of a modern robot joint: frameless torque motor + high-ratio zero-backlash gear + absolute encoder, frequently with another precision encoder on the output side to measure errors introduced by the gearbox. ([Allient, Inc.][2])

That is practically our thesis written by the company.

The financial inflection is also real. Q2 2026 revenue was $153.8M, +10% YoY; gross margin reached a record 34.9%; adjusted EBITDA margin reached 15.4%. More importantly, orders hit **$201.3M, +49%**, book-to-bill was **1.31×**, and backlog reached $298M, +26%. ([FinancialContent][3])

And ALNT unexpectedly gives us another bottleneck simultaneously: **data-center power quality**. Data-center/infrastructure revenue reached $16.3M in Q2, 10.6% of company revenue and +60% YoY; TTM was $57.1M, +69%. They provide harmonic filters, line reactors and electrical power-quality systems. ([MarketBeat][4])

So ALNT actually sits here:

**AI compute growth**
→ data center electricity gets nasty
→ ALNT power-quality equipment

and

**AI intelligence improves**
→ robots become economically useful
→ physical motion becomes bottleneck
→ ALNT motors/encoders/controllers/actuators.

That's unusually good thesis topology.

The catch is that the market has noticed. Around September 8, ALNT was ~$95.63, ~$1.63B market cap, versus only ~$575M TTM revenue. That's ~2.8× sales, ~31× forward earnings and ~23× EV/EBITDA. Its market cap has more than doubled in a year. ([StockAnalysis.com][5])

So I love the **company/thesis fit significantly more than the valuation**. At $40–60 this would have been extraordinary. At ~$95 it needs the robotics/data-center acceleration to actually occur.

### TKR — potentially the sleeper

TKR is fascinating precisely because most screens describe it as an old industrial bearing company.

Underneath Timken they've assembled:

**Cone Drive → harmonic strain-wave reducers**
**SPINEA → precision cycloidal reducers**
**CGI → precision micro-gearing**
**Timken → precision bearings + encoders**
**Rollon → robot linear motion / seventh-axis systems**

Timken now explicitly markets this entire portfolio for humanoids, describing getting humanoid motion architecture right as a central engineering challenge. ([The Timken Company][6])

Even better, SPINEA isn't some generic gearbox operation. Timken says it is the only European precision cycloidal gearing producer and one of only two suppliers capable of covering all six axes of small/low/medium-payload robots. ([The Timken Company][7])

That is exactly the kind of **hidden physical chokepoint** we've been trying to identify.

Suppose an advanced AI model makes the robot's "brain" essentially software. The physical robot may still need 20–40+ highly controlled joints. Each joint needs some combination of:

motor → bearing → reducer → encoder → controller → torque/force feedback.

Inference cost falling does absolutely nothing to solve backlash, torque density, bearing life, manufacturing tolerances or micron-level position measurement.

That's the bottleneck migration mechanism.

And TKR's Industrial Motion segment appears to be accelerating already: Q2 2026 sales were **$453.9M, +14.6%**, while adjusted EBITDA rose to $105.6M and margin jumped from 18.3% to **23.3%**. ([Timken News][8])

Yet TKR around September 9 was only ~18× forward earnings and ~12.3× EV/EBITDA. ([StockAnalysis.com][9])

That's the attraction.

The downside is **purity**. Timken is an $8B+ industrial company, and reducers/robot encoders constitute only a fraction of total revenue. Massive humanoid adoption won't make TKR a 20× stock.

But this may be one of the better examples we've found of:

> boring incumbent owns several technologies that suddenly become strategic bottlenecks.

For **risk-adjusted** exposure, I currently prefer TKR to NOVT.

### NOVT — extremely good embodiment technology

NOVT is the highest-quality "encoder" exposure of these three.

Celera Motion/Novanta has optical encoders capable of resolutions down to the nanometer scale and makes optical, inductive and force/torque sensing systems. Applications already include surgical robotics, semiconductor equipment, robotic end effectors and precision photonics. ([Novanta][10])

But Novanta has gone beyond components. Its new **Motion Stack** combines:

frameless motors

* optical/inductive encoders
* force/torque sensing
* servo drives
* control.

([Novanta][11])

That looks very strategically positioned for the transition from "robotics research project" to scalable machine platforms.

Their encoder technology also has genuine high-end differentiation. Novanta claims up to **1.2 nm resolution** in its optical encoder portfolio; its Aura platform is specifically designed for applications including surgical robotics and semiconductor manufacturing. ([Novanta][12])

And Novanta isn't only robotics. It has precision laser beam-steering technology used for micron-level manufacturing, which reconnects NOVT to our **AI → more sophisticated hardware → precision manufacturing** branch. ([Novanta][13])

Financial quality supports the story. Q2 revenue rose 10% to $265.8M. Automation Enabling Technologies generated $136.2M with a very attractive **52.6% GAAP gross margin**. ([Novanta Investors][14])

But NOVT is expensive: roughly $5.6B market cap on ~$1.03B TTM revenue, ~5.5× sales, ~38× forward earnings and ~29× EV/EBITDA. ([StockAnalysis.com][15])

So I'd characterize NOVT as:

**better business / stronger moat than ALNT, but considerably less obviously asymmetric at today's valuation.**

### And DRAM is basically our thesis turned into an ETF

This one made me laugh slightly because Roundhill's actual marketing language is essentially:

**memory is the bottleneck of the AI revolution.**

DRAM launched on April 2, 2026 with a 0.65% expense ratio and specifically targets global HBM/DRAM/NAND/storage companies. ([Roundhill Investments][16])

And the current bottleneck is very real. Recent reporting describes AI-driven HBM demand pulling manufacturing capacity away from traditional DRAM, with memory supply expected to remain tight into 2027 and potentially beyond because meaningful new fab capacity takes years to construct. ([The Verge][17])

This is an excellent example of bottleneck migration:

**GPUs scarce**
→ GPU production expands
→ each accelerator wants enormous bandwidth
→ **HBM becomes scarce**

Then:

**HBM capacity increases**
→ manufacturers convert conventional DRAM capacity to HBM
→ **ordinary DRAM becomes scarce**

Then:

more inference + agents + generated data
→ more storage
→ **enterprise NAND / SSD / HDD demand rises**

Roundhill's deck explicitly identifies this whole cascade. ([Roundhill Investments][18])

And DRAM isn't simply Micron. September holdings show major exposure to Samsung, SK Hynix and Micron, followed by SanDisk, Seagate, CXMT exposure through a swap, Western Digital, Kioxia, Nanya, Winbond, Phison and others. ([StockAnalysis.com][19])

One thing to understand: the weird Treasury holdings and >100% gross percentages come from the ETF using **total-return swaps with Treasury/cash collateral**. So don't interpret the T-bill weighting as DRAM putting ~25% of your economic exposure into a Treasury bet. ([Roundhill Investments][16])

The three giants dominate the effective exposure. Combining direct stock and swap positions, roughly **three-quarters of the core exposure is Samsung + SK Hynix + Micron**.

That's probably exactly what you want for the broad memory thesis.

But there's an important distinction relative to LPKF/LEU/etc.:

**memory is already demonstrably the bottleneck.**

Therefore this is less "discovering the next bottleneck" and more "buying the existing bottleneck."

Our biggest alpha should come from identifying **n+1**, not n.

And I think **reducers + encoders may genuinely be one of those n+1 bottlenecks**.

The progression I'm increasingly interested in is:

**2024–26:** accelerators
→ **2025–27:** HBM / memory
→ **2025–28:** advanced packaging / optical interconnect / power
→ **2027–32?: physical AI manufacturing**
→ **precision reducers / encoders / bearings / motors / force sensors**

And this makes **ALNT + TKR much more conceptually exciting to me than simply adding another semiconductor stock**.

My current ranking for this exact thesis would therefore be **ALNT ≈ TKR > NOVT** on the robotics branch. ALNT has the most upside convexity and remarkable cross-exposure to data-center power, while TKR has the best combination of hidden reducer exposure, scale and valuation. NOVT may be the technically best asset but is priced accordingly.

For the compute branch, **DRAM belongs in our canonical bottleneck basket**, but I would now use it almost as an *indicator*: if memory is n, Feedify should be searching upstream/downstream for **n+1 before Wall Street names an ETF after it**. That is exactly what our LPKF/SUSS/Nynomic search was trying to do.

[1]: https://www.sec.gov/Archives/edgar/data/46129/000110465926091098/alnt-20260630x10q.htm "ALLIENT INC_June 30, 2026"
[2]: https://allient.com/blogs/how-to-select-a-motor-for-a-robot-joint/?utm_source=chatgpt.com "How to Select a Motor for a Robot Joint - Allient, Inc."
[3]: https://www.financialcontent.com/article/bizwire-2026-8-5-allient-delivers-doubledigit-revenue-growth-record-gross-margin-and-strong-orders-in-second-quarter-2026?utm_source=chatgpt.com "Allient Delivers Double‑Digit Revenue Growth, Record Gross Margin and Strong Orders in Second Quarter 2026 | FinancialContent"
[4]: https://www.marketbeat.com/earnings/reports/2026-8-5-allient-inc-stock/?utm_source=chatgpt.com "ALNT Q2 2026 Earnings Report on 8/5/2026"
[5]: https://stockanalysis.com/stocks/alnt/statistics/?utm_source=chatgpt.com "Allient (ALNT) Statistics & Valuation"
[6]: https://www.timken.com/markets/automation-robotics-industrial-solutions/?utm_source=chatgpt.com "Automation, Robotics & Industrial Machinery - The Timken Company"
[7]: https://www.timken.com/timken-world/leading-precision-drive-selection-and-expertise/?utm_source=chatgpt.com "Leading Precision Drive Selection and Expertise - The Timken Company"
[8]: https://news.timken.com/2026-08-04-Timken-Reports-Second-Quarter-2026-Results?utm_source=chatgpt.com "Timken Reports Second-Quarter 2026 Results - Aug 4, 2026"
[9]: https://stockanalysis.com/stocks/tkr/?utm_source=chatgpt.com "The Timken Company (TKR) Stock Price & Overview"
[10]: https://novanta.com/robotics-automation/optical-encoders/?utm_source=chatgpt.com "Optical Encoders | Celera Motion"
[11]: https://novanta.com/robotics-automation/products-motion-stack/?utm_source=chatgpt.com "Products / Motion StackProducts - Robotics & Automation"
[12]: https://novanta.com/robotics-automation/products/optical-encoders/?utm_source=chatgpt.com "Optical Encoders - Robotics & Automation"
[13]: https://novanta.com/precision-manufacturing/laser-beam-steering/?utm_source=chatgpt.com "Laser Beam Steering | Novanta"
[14]: https://investors.novanta.com/news/news-details/2026/Novanta-Announces-Financial-Results-for-the-Second-Quarter-2026/default.aspx?utm_source=chatgpt.com "Novanta Inc. - Novanta Announces Financial Results for the Second Quarter 2026"
[15]: https://stockanalysis.com/stocks/novt/?utm_source=chatgpt.com "Novanta (NOVT) Stock Price & Overview"
[16]: https://www.roundhillinvestments.com/etf/dram/?utm_source=chatgpt.com "Memory ETF | Invest in Memory Stocks with DRAM | Roundhill Investments"
[17]: https://www.theverge.com/tech/988225/ram-shortage-supply-chain-micron-apple-iphone?utm_source=chatgpt.com "The real reason your phone is getting more expensive"
[18]: https://www.roundhillinvestments.com/assets/pdfs/dram_deck.pdf?utm_source=chatgpt.com "DRAM Investor Deck -  Retail"
[19]: https://stockanalysis.com/etf/dram/holdings/?utm_source=chatgpt.com "DRAM Holdings List - Roundhill Memory ETF" is it too late to buy dram etf? i think this is a simple problem right ? all u do is identify the bottlenecks to agi then rebalance based on which is most prevalent, then when agi can solve it or theres a shift then u allocate more to the higher order bottleneck.. like e.g. liets say the bottleneck right now is memory, what is the bottlenceck on memory.. or maybe chatgpt8 develops a system where u dont need memory at all, then overnight memory collapses. i think the nature of stocks are about to become more reactive and volatile right, like heres the interesting thing - ai pumps an industry beyond belief - step change, ai no longer needs the industry  -- this is the sort of thing i want to be able to know from our system.. think of it as like a bottleneck dependency graph where the primary thesis is ai limitations fueling capital allocation across the economy , if we can model that well we can forecast and buy the right tickers
