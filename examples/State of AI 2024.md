# Nathan Benaich - 🪩The @stateofaireport 2024 has landed! 🪩  Our seventh installment is our biggest and most comprehensive yet, covering everything you *need* to know about research, industry, safety and politics.  As ever, here's my director’s cut (+ video tutorial!) 🧵

https://x.com/nathanbenaich/status/1844263448831758767

## Nathan Benaich introduces 2024 State of AI report

 Hey everyone, I'm Nathan Benaich, founder and general partner of Airstream Capital, investing in AI-first companies. And today, I'm just really thrilled to bring you the annual State of AI report for 2024. So this report analyzes AI research, industry, politics and safety over the last 12 months. And our goal with it is really to inform conversation around AI and its implications for the future. I invite you to go online at stateof.ai, where you can read and find a copy today to download. 

This report, as every year, is reviewed by a number of key contributors from big tech companies, startups and universities, to make sure that the information and opinions that we provide you are honest and correct. 

Okay, so I'm going to walk through a couple of slides, give you an editor's cut, and I'll start with research. 

## Model trends and performances Update

So until a few weeks ago, the traditional OpenAI versus everyone else split had seemingly come to an end. We had Anthropic, OpenAI, XAI that were reporting near identical scores across most benchmarks, with subtle variations, probably down to a few implementation details. However, the long-rumored Strawberry, now dubbed 01, put OpenAI back into the lead again, and its standout performance, particularly on complex, multi-layered math, science tasks, was really impressive. While none of the techniques that they employed were in and of themselves new, it kind of demonstrated that OpenAI had been quicker to spot their potential. For example, Google DeepMind had published their work on scaling inference time compute over the summer, but clearly OpenAI had probably been working on it earlier. In last year's report, and a few others, open source language models were often highly capable, but, you know, a meaningful performance gap was seen between them and their closed proprietary peers. However, with LAMA 3.1, Meta has finally closed that gap, particularly their 405b model looks competitive with Claude and GPT 4.0 across reasoning, math, multilingual, and long context tasks. And more recently, with LAMA 3.2 that they released just a couple of weeks ago, this family of models became multimodal. 

A key trend that we've seen over the last kind of year or so is that smaller models have really good performance, as labs use various techniques to make training much more efficient. In particular, distillation, where you take a large model to refine and synthesize training data for a smaller model has emerged as a popular technique. Indeed, it's been employed by Google for Gemini and Gemma, their open source model, and it's likely also been used by Anthropik for Claude and NVIDIA to produce the Minitron. These smaller models combine with techniques like quantization, reduced memory footprint, and demonstrate the potential for on-device deployment. 

Meanwhile, US sanctions have not stopped Chinese labs from achieving state-of-air performance. Particularly model builders have been prioritizing computational efficiency to compensate for constraints around GPU access. Indeed, Chinese labs have been very lively contributors on open source competitions and model databases, with Quen and MiniCPM winning fans for their vision capabilities. 

and COGX video being quite competitive for text-to-video generation. 

Image and scene understanding has gone from highly challenging in 2018, when we first started profiling it, to pretty much business as usual. Every frontier model company now has vision capabilities out of the box. Interestingly enough, we found VLM's vision language models, their performance doesn't seem to really follow the LLM-style scaling laws, meaning that smaller models can actually achieve remarkable results. For example, Allen Institute's open source Malmo can hold its own against the larger proprietary GPT-4O. 

## Biological Editors, AI Chips, & Industry Trends

Over in biology, language models are learning to design human genome editors. CRISPRs, as they're known, are potentially transformative medicines, but, you know, historically researchers have shied away from them due to high R&D costs and various IP issues. Having said that, the first CRISPR medicines have actually been approved in the US and the UK this past year. A ProFluent, a Berkeley-based company, has used their CRISPR-Cas Atlas to fine-tune a language model pre-trained on natural protein sequences, such that it can generate functional genome editors with novel features and novel sequences. Their kind of most popular hit from a recent screen, it's called OpenCRISPR-1, exhibited up to 95% editing efficiency across various human cell types, with a low off-target rate and compatibility with base editing. And they've made this genome editor open access for researchers to use. 

When we started compiling the report, now 2018 feels like ages ago, robotics was usually peripheral. Led by various groups, including DeepMind, we've now seen the field come to life. Both language models and vision language models have demonstrated their potential to help resolve bottleneck issues around data and long-standing robustness hurdles where task-specific models had previously been the norm. NVIDIA, for example, has recently established their own embodied AI lab, while OpenAI has revived their own robotics team after having disbanded it a few years ago. 

Now let's go into industry. It's no secret, of course, that NVIDIA continues to grow and grow, despite a small chorus of skeptics, probably becoming even smaller over the years. And it's established competitors like AMD and Intel have just failed to leave a scratch on it, while newer challengers like Grok and Cerebrus still can't match it for scale and ease of use. We started tracking the size of GPU clusters and growth in these large-scale clusters continues to be driven by H100s, with Meta, XAI, Tesla leading the way. Startups, too, actually have built up around 10,000 GPU-worth clusters for H100s. We're starting to see the first GB200 clusters go live, such as the 10k1 at the Swiss National Supercomputing Center. It'll be interesting to see more come online in the next year. 

We continue to track the most popular AI chips used in research papers each year. And while the data trends you see in this graph for NVIDIA, TPUs, ASICs, FPGAs, Huawei, Apple, and a variety of startups looks close on first glance, this is actually a log scale that we've had to use because NVIDIA hardware is used 11 times more than all peers combined in AI research. Their closest competitor is the TPU, which has seen pretty substantial growth in research, up 522% year-on-year. 

NVIDIA hardware once again demonstrates its longevity in AI research. Researchers are just so keen to get hold of it that they're even going to settle for legacy chips in research, such as the V100, the 3090, and the 4090. The very capable A100, in fact, despite being four years old, is still growing in popularity. Combined, all the chip challengers were used in fewer than 500 research papers this year, while the Cerebrus has begun to pull ahead of the pack. 

Some of these businesses have effectively abandoned trying to compete with NVIDIA by combining software and hardware and selling both in favor of offering APIs to their own clouds. Now, despite early skepticism, there's now pretty clear evidence that big model builders are driving serious revenue, although they carry pretty steep revenue multiples. 

Meanwhile, some buzzier applications are still yet to persuade people to pay up beyond the trial period. However, open AI's billions in revenues are yet to translate into a profitable business model. As training runs begin to cost hundreds, if not billions of dollars, there's kind of no path to profitability in sight. 

Having said all of that, perhaps it's vibes that matter, after all. One way of turning your share price around is to just ditch metaverse investments, pivot hard into open source AI, and effectively become the face of the American industrial renaissance. In fact, the popularity of Lama-based models, which have been downloaded almost half a billion times on Hugging Face, has been central to the corporate turnaround story of the past two years. We're, of course, talking about meta. Inference prices, once deemed to have been exorbitant, have been collapsing, although it's less clear whether this is a product of efficiency gains or if users are the lucky beneficiaries of a price war or both. Competitions are, of course, driving an arms race on the product side, too. Interactive coding assistants like Claude Artifact, which bring the ability to bring static code snippets to life or emerging as a developer favorite. And even open AI is rushing to imitate this with Canvas. 

But not everybody is a winner, as anger builds among creators and artists. Big tech companies are attempting to buy off their deepest secret, their deepest pocketed critics via licensing agreements, and there's been an avalanche of lawsuits. But courts are yet to reach a verdict on fair use arguments that big model builders use, and this will take a long time to materialize. 

## Self-Driving Wins and AI Growth

Historically, we've profiled self-driving car companies, promising breakthrough after breakthrough and much under delivering. But having said that, in the last year or so, we're starting to see some winners. Waymo has scaled across a number of US cities and secured another $5 billion investment from Alphabet, and it's now providing almost 100,000 paid rides in the US. And over in the UK, Wave has raised over a billion this year and secured critical legislation change. 

Based on transaction data from RAMP, companies are purchasing AI products more and more. In fact, the retention curves look interesting. The cohort from 2022 turned by 59%, but the latest cohort from last year improved its retention rate to 63% by the end of the year, and billings are growing. 

Using Stripe data, we've seen that AI-first companies founded after 2020 are scaling significantly faster. In fact, those that hit over $30 million in revenue a year took 20 months for AI companies versus 65 months for traditional SaaS. 

Texas Beach is growing, and I think we've clearly crossed the uncanny valley. Startups like Eleven Labs seem to have the field for themselves. And other use cases like call-centered dialogue systems produced by companies like PolyAI are really convincing people that they're much better than brittle features created by incumbents. 

## Recursion and Excientia deal

In the world of biotech, we've seen the first landmark deal where two public companies are coming together. On the one side, Recursion, on the other side, Excientia, in a deal worth $700 million. This creates the first company that's fully end-to-end design discovery with the largest GPU cluster in biopharma. 

## Video gen heating up; exits cold

Video generation is really heating up as players like Runway, Pika, and Luma are trying to create longer form complex videos. Of course, compute and data collection continues to be an issue, and it's not that cheap to run. And they have to compete with Chinese offerings like Kwaishu Kling and Video COGX. 

Consumer hardware is a little bit iffy. On the one side, meta AI-powered Ray-Bans are a smash success. On the other hand, Rabbit R1 and Humane Pin feel like solutions in search of a problem. 

US private markets on the venture side continue to rip with annual closing volumes around $100 billion. Mega rounds continue to be quite popular, particularly post-2023. And of course, AI has been a boon for public companies as they reach almost $9 trillion in value. 

On the exit side, it's quite frigid and continues to be so since COVID. And the new season has really seen the emergence of these pseudo-acquisitions where teams get acquired for a licensing cost and shell companies are left to fend for themselves. 

## AI regulation struggles; power impacts tech

Meanwhile, in politics, we've seen non-binding assurances that big AI labs post the executive order, but there's a bit of lack of consensus around potential legislation. As Europe really continues to press ahead on regulation, US labs struggle to adapt. CLOD actually isn't available in the EU until May of this year, and OpenAI has no plans to make advanced voice mode available in the EU. Model builders are scouring for more data. 

Indeed, policies are coming under scrutiny from regulators. Meta, for example, granted users an opt-out in the EU and hasn't received go-ahead from UK regulators. 

Power is a big issue, too. That's really jeopardizing tech companies' net zero commitments as they start to fire up new and old nuclear reactors to meet GPU demands. 

## AI safety shift, real-world harms, predictive insights

Over in safety, there's been a massive vibe shift where existential risk has now moved towards the center and companies to commercialize. In fact, in a recent AGI piece, Sam Altman didn't even mention existential risk. Researchers have attempted to beef up their model security, while jailbreakers have made pretty easy work of all these approaches. And technical communities are discussing these technical exploits, but much of the real-world harms that result from Gen.AI usually stem from pretty unsophisticated use of off-the-shelf products. Now, over in predictions, last year we made about 10 or 12 predictions, and we got right the fact that the FTC would investigate Microsoft and OpenAI, that there'd be limited progress on global governance. We didn't get right the fact that self-improving agents would crush soda or the tech IPO markets would unthaw. This year, we think that a $10 billion investment from a sovereign state into a US large AI lab will invoke national security reviews, and that would see a Blockbuster app created just with no coding abilities. 

So I hope that you enjoyed our editor's cut here that I ran through of the 2024 State of the AI report. I invite you to read it at stateof.ai and drop us your thoughts. And most importantly, thank you to the whole community for Blockbuster U and AI. It's been a real pleasure to create this analytical narrative of all your achievements. Thanks for your attention and enjoy yourself.