# Sources and lineage

Groundcraft is an original synthesis. It adopts ideas, not copied prompt text.

## Agent methods and tools

- [Matt Pocock Skills 1.1.0](https://github.com/mattpocock/skills/releases/tag/v1.1.0): small composable skills, progressive disclosure, falsifiable debugging, fresh-context review, and completion criteria. MIT.
- [GSD Core 1.6.1](https://github.com/open-gsd/gsd-core/releases/tag/v1.6.1): context engineering, durable state, strong/weak evidence, phase loops, and fresh-context execution. MIT.
- [BMAD Method 6.10.0](https://github.com/bmad-code-org/BMAD-METHOD/releases/tag/v6.10.0): just-in-time files, explicit contracts, adversarial review, and halt states. MIT with trademark terms.
- [Superpowers 6.1.1](https://github.com/obra/superpowers/releases/tag/v6.1.1): design gates, native worktree isolation, test-first practice, independent review, and evidence before completion. MIT.
- [Ponytail 4.8.4](https://github.com/DietrichGebert/ponytail/releases/tag/v4.8.4): YAGNI, reuse, native-first design, complexity review, and repeated comparative evals. MIT.
- [gstack 1.60.1.0](https://github.com/garrytan/gstack/blob/main/VERSION): browser QA, completion states, scope-drift review, release discipline, and a caution against prompt duplication. MIT.
- [OpenSpec 1.6.0](https://github.com/Fission-AI/OpenSpec/releases/tag/v1.6.0): lightweight brownfield change agreements, delta specifications, and completeness/correctness/coherence verification. MIT.
- [GitHub Spec Kit 0.12.11](https://github.com/github/spec-kit/releases/tag/v0.12.11): constitutions, requirement quality checks, executable planning artifacts, and workflow gates. MIT.
- [Nanostack 1.1.1](https://github.com/garagon/nanostack/releases/tag/v1.1.1): capability honesty, artifact-first coordination, harness manifests, and local orchestration. Apache-2.0.
- [Compound Engineering 3.19.0](https://github.com/EveryInc/compound-engineering-plugin/releases/tag/compound-engineering-v3.19.0): blinded prompt comparisons, discriminating fixtures, restraint negatives, and grader sabotage tests. MIT.
- [Harbor 0.18.0](https://github.com/harbor-framework/harbor/releases/tag/v0.18.0) and [mini-swe-agent 2.4.5](https://github.com/SWE-agent/mini-swe-agent/releases/tag/v2.4.5): task, trial, grader, outcome, and transcript vocabulary plus transparent minimal runners. Apache-2.0 and MIT.

These projects informed mechanisms, not a merged command catalog. Groundcraft deliberately rejects mandatory roleplay, duplicated persistent state, prompt-heavy preambles, and universal planning artifacts when they do not improve the outcome.

## Engineering evidence

- [DORA 2025](https://dora.dev/research/2025/dora-report/): AI amplifies the surrounding delivery system.
- [DORA metrics](https://dora.dev/guides/dora-metrics/), [working in small batches](https://dora.dev/capabilities/working-in-small-batches/), and [trunk-based development](https://dora.dev/capabilities/trunk-based-development/): system-level flow, stability, feedback, and integration practices. DORA metrics are not a score for an individual agent or change.
- [Google Engineering Practices](https://google.github.io/eng-practices/) and [what to look for in review](https://google.github.io/eng-practices/review/reviewer/looking-for.html): small changes, review standards, test adequacy, complexity, and review communication.
- [Google SRE: Canarying Releases](https://sre.google/workbook/canarying-releases/): controlled rollout and operational evidence.
- [Google SRE: Embracing Risk](https://sre.google/sre-book/embracing-risk/): SLOs and error budgets as operational release constraints.
- [Parnas, 1972](https://doi.org/10.1145/361598.361623): information hiding and module boundaries.
- [NIST SSDF](https://csrc.nist.gov/projects/ssdf), [NIST SP 800-218A](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218A.pdf), and [SLSA 1.2](https://slsa.dev/spec/v1.2/): secure development, verification, and artifact provenance. SLSA attests origin and process, not functional correctness.
- [NIST AI RMF](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/): risk-aware human oversight.
- [AQuA Book](https://www.gov.uk/guidance/the-aqua-book): proportional analytical quality assurance and fitness for purpose.

## Agents, evaluation, and context

- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents): begin with the simplest composition that works and add agentic complexity only for measured value.
- [OpenAI subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents#why-subagent-workflows-help): move independent read-heavy exploration, testing, triage, and summarization off the main thread while keeping write-heavy coordination controlled.
- [Towards a Science of Scaling Agent Systems](https://arxiv.org/abs/2512.08296) and [MAST](https://arxiv.org/abs/2503.13657): multi-agent gains depend on decomposability and central verification; sequential planning and weak coordination can amplify errors. Both are preprints, not universal thresholds.
- [Rational Metareasoning for Large Language Models](https://arxiv.org/abs/2410.05563): select extra reasoning by expected value of computation rather than spending a fixed budget on every task.
- [ReAct](https://openreview.net/forum?id=WE_vluYUL-X): interleave reasoning, action, and observation so plans update when evidence changes.
- [STORM](https://aclanthology.org/2024.naacl-long.347/) and [ALCE](https://aclanthology.org/2023.emnlp-main.398/): research benefits from distinct perspectives, claim-based synthesis, and separate citation correctness and completeness checks.
- [LongMemEval](https://arxiv.org/abs/2410.10813): retrieve memory by relevance and time; long raw histories and over-compression can both damage answer support.
- [PlanBench](https://arxiv.org/abs/2206.10498) and [Tree of Thoughts](https://openreview.net/forum?id=5Xc1ecxO1h): fluent plans are not reliable proof, while branching is useful only for genuinely difficult decisions where its extra cost pays.
- [τ-bench](https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b126cc38b8638e07bef37e7b2bb72bf-Abstract-Conference.html): evaluate observable end state, policy compliance, and repeated consistency rather than transcript confidence alone.
- [Anthropic: Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): high-signal context, just-in-time retrieval, and progressive disclosure.
- [Anthropic agent evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents): capability and regression evaluation design.
- [OpenAI eval best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices): task-specific datasets, typical, edge, and adversarial cases, and human calibration.
- [OpenAI on SWE-bench Verified](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/): benchmark contamination and grader quality limits.
- [NIST CAISI on agent evaluation cheating](https://www.nist.gov/caisi/cheating-ai-agent-evaluations): observed grader gaming and contamination failure modes.
- [NIST AI 800-2 initial draft](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf): evaluation objectives, versioning, isolation, traces, multiple trials, uncertainty, and qualified claims. It is a draft, not a final standard.
- [The oracle problem in software testing](https://discovery.ucl.ac.uk/id/eprint/1471263/): limits of deciding whether observed behavior is correct.
- [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/) and [Chroma Context Rot](https://research.trychroma.com/context-rot): task-dependent degradation and positional sensitivity in long contexts.
- [Intrinsic self-correction limitations](https://proceedings.iclr.cc/paper_files/paper/2024/hash/8b4add8b0aa8749d80a34ca5d941c355-Abstract-Conference.html) and [LLM-as-a-judge biases](https://proceedings.neurips.cc/paper_files/paper/2023/file/91f18a1287b398d378ef22505bf41832-Paper-Datasets_and_Benchmarks.pdf): why self-review and model grading are not independent proof.

## Platform behavior

- [OpenAI Skills](https://developers.openai.com/codex/concepts/customization#skills): implicit matching, focused descriptions, and progressive disclosure.
- [OpenAI Hooks](https://developers.openai.com/codex/hooks): plugin hook discovery, trust, supported command hooks, and targeted lifecycle injection; Groundcraft keeps only `SubagentStart`, whose output is injected when a subagent starts.
- [OpenAI AGENTS guidance](https://developers.openai.com/codex/concepts/customization#agents-guidance): keep guidance small, route close to the relevant code, and pair recurring rules with executable checks.

Community discussions were used to discover failure modes such as context bloat, command fatigue, document drift, unnecessary questions, and self-review bias. A representative [practitioner discussion about spec-driven frameworks](https://www.reddit.com/r/ClaudeCode/comments/1t2mym5/are_specdriven_frameworks_like_agent_os_bmad/) informed cases, not normative claims. Normative technical claims remain grounded in primary sources. Vendor sources are useful operational evidence but carry commercial incentives; Groundcraft prefers convergence with standards, peer-reviewed work, source code, and direct tests.

Rules such as the two-identical-failures stop, the exact completion-state vocabulary, the worktree threshold, and the Groundcraft task taxonomy are local design invariants synthesized from these sources and forward-tests; they are not quoted standards or universal empirical thresholds. This source review is decision-oriented, not a systematic literature review.
