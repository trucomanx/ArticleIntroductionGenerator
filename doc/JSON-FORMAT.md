# 1. Recommended JSON Structure

High level fields

```json
{
  "paper_profile": { ... },
  "research_problem": { ... },
  "contributions": [ ... ],
  "related_work": { ... },
  "writing_guidelines": { ... }
}
```

## 1.1 paper_profile -- Who is YOUR article

This serves as the narrative anchor of the introduction.

```json
"paper_profile": {
  "title": "...",
  "domain": "Computer Vision / Machine Learning / Systems / etc",
  "target_journal": "IEEE T-PAMI / Elsevier PR / etc",
  "keywords": ["...", "..."],
  "author_intended_summary": "Short paragraph explaining what the paper does and why."
}
```

💡 author_intended_summary is key: it guides tone and focus.

## 1.2 research_problem -- The problem space

Help with writing paragraphs 1 and 2 of the introduction.

```json
"research_problem": {
  "research_domain_overview": "General description of the field and its importance.",
  "specific_problem": "Precise description of the problem tackled.",
  "practical_challenges": [
    "Scalability",
    "Data scarcity",
    "Real-time constraints"
  ],
  "why_existing_solutions_are_insufficient": "High-level explanation without citing specific papers."
}
```

## 1.3 contributions – What do you deliver

Used for the contributions paragraph.

"contributions": [
  "We propose a novel ...",
  "We introduce a new benchmark ...",
  "We demonstrate state-of-the-art performance on ..."
]

## 1.4 related_work.
### 1.4.1 related_work.references -- Structured state of the art

Here is the anti-ai-hallucination heart.

```
"related_work": {
  "references": {
    "smith2022deep": {
      "bibtex": "@article{smith2022deep, ...}",
      "abstract": "This paper proposes...",
      "methodological_category": "deep_learning",
      "central_technical_idea": "Introduces a CNN-based approach for...",
      "author_reported_strengths": [
        "High accuracy",
        "Robust to noise"
      ],
      "reported_limitations": [
        "High computational cost",
        "Requires large labeled datasets"
      ],
      "relevance_to_our_work": "Addresses the same task but assumes fully supervised data.",
      "introduction_paragraph_role": "early_state_of_art"
    }
  }
}
```

| Field                         | Why                                        |
| ----------------------------- | ------------------------------------------ |
| `methodological_category`     | What kind of technical solution is this?   |
| `central_technical_idea`      | Main technical idea introduced by this work|
| `reported_limitations`        | Feeds the critical paragraph               |
| `relevance_to_our_work`       | Avoids generic comparisons                 |
| `introduction_paragraph_role` | Controls where to cite                     |

Exemplos de methodological_category:

* classical_optimization
* probabilistic_model
* deep_learning
* transformer_based
* graph_based
* heuristic_rule_based
* hybrid_model

Exemplos de introduction_paragraph_role:

* foundational
* early_state_of_art
* recent_advances
* limitations_discussion
* contrast_with_our_work

## 1.4.2 related_work.human_curated_synthesis -- Your human reading

This is gold for Q1 text.

"human_curated_synthesis": {
  "common_trends": [
    "Shift towards data-driven approaches",
    "Increasing model complexity"
  ],
  "open_problems": [
    "Generalization to unseen domains",
    "High computational requirements"
  ],
  "explicit_research_gap": "Despite recent progress, existing methods fail to..."
}

# 1.5 writing_guidelines -- Fine text control

Write here all the indications you want to give to LLM

```
"writing_guidelines": "Some important orders to be followed by the LLM"
```


# 2.
```json
{
  "paper_profile": {
    "title": "Efficient X under Y Constraints",
    "domain": "Computer Vision",
    "author_intended_summary": "This paper proposes a lightweight method for X that operates under Y constraints."
  },
  "research_problem": {
    "research_domain_overview": "X has become a core task in modern vision systems.",
    "specific_problem": "However, performing X under Y remains challenging.",
    "practical_challenges": ["Latency", "Memory usage"]
  },
  "contributions": [
    "A novel lightweight architecture",
    "Extensive evaluation on benchmark datasets"
  ],
  "related_work": {
    "references": {
      "doe2023method": {
        "bibtex": "@inproceedings{doe2023method,...}",
        "abstract": "We propose...",
        "methodological_category": "deep_learning",
        "reported_limitations": ["High latency"],
        "relevance_to_our_work": "Does not consider Y constraints.",
        "introduction_paragraph_role": "recent_advances"
      }
    },
    "human_curated_synthesis": {
      "explicit_research_gap": "Existing methods do not jointly address X and Y."
    }
  },
  "writing_guidelines": "Some important orders to be followed by the LLM"
}

```
