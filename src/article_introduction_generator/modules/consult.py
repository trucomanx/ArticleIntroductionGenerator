
import json
from deep_consultation.core import consult_with_deepchat

    
SYSTEM_PROMPT = """
You are an expert scientific writer specialized in Q1 Computer Science journals
(e.g., IEEE TPAMI, CVPR, ICCV, NeurIPS, Elsevier Pattern Recognition).

Your task is to generate the INTRODUCTION section of a research paper.

Strict rules:
1. You must rely exclusively on the information provided in the user input JSON.
2. You must NOT invent citations, methods, datasets, claims, or results.
3. All mentions of prior work must be grounded in the provided
   related_work.references entries.
4. The introduction must seamlessly integrate background, state of the art,
   critical analysis, and motivation.
5. The tone must match a top-tier Q1 journal: formal, precise, and concise.
6. No bullet points. No section headers. Only well-structured academic paragraphs.
7. Do NOT describe the JSON or its structure in the output.
8. Follow all instructions contained in the "writing_guidelines" field if present.
9. Do not use exactly the same text sent in JSON, try to use your own words to avoid plagiarism problems.
10. Avoid writing texts with redundant information.

You must write as a human researcher, not as an assistant.

"""

USER_PROMPT = """
Using the JSON below, write the complete INTRODUCTION section of the paper.

Structural requirements:
- Paragraph 1: General context of the topic. 
  Broad research domain overview and importance
  (use research_problem.research_domain_overview).
- Paragraph 2: Specific problem within the topic that the text focuses on.
  Narrow down to the specific problem and practical challenges
  (use research_problem.specific_problem and practical_challenges).
- Paragraphs 3–4: Integrated state of the art discussion.
  Organize cited works according to their introduction_paragraph_role
  (foundational → early_state_of_art → recent_advances).
  Highlight limitations where relevant.
  Use LaTeX-style bibliographic formatting for citations in the bibliography.
- Paragraph 5: Synthesize common trends and open problems using
  related_work.human_curated_synthesis.
- Final paragraph: Proposed solution of paper. 
  Explicitly state the research gap and position the paper’s
  contributions as a response to this gap.

Use the author_intended_summary to guide emphasis and narrative flow.
Integrate the contributions naturally into the motivation, not as a list.

- When writing the introduction you must remember that it is a scientific article, therefore it is very important that there must not be texts with redundant information, it must be concise and clear.

Here is the JSON input:

"""

def consultation_in_depth(system_data, json_data):

    json_data_string = json.dumps(
        json_data,
        ensure_ascii=False,  # mantém acentos
        indent=2              # deixa bonito e legível
    )
    
    msg = USER_PROMPT + "```json\n" + json_data_string + "\n```"
    
    OUT=consult_with_deepchat(  system_data["base_url"],
                                system_data["api_key"],
                                system_data["model"],
                                msg,
                                SYSTEM_PROMPT)
    return OUT
    
def consultation_in_text(json_data):

    json_data_string = json.dumps(
        json_data,
        ensure_ascii=False,  # mantém acentos
        indent=2              # deixa bonito e legível
    )
    
    msg  = "System PROMPT:\n" 
    msg += SYSTEM_PROMPT + "\n"
    msg += "User PROMPT:\n" 
    msg += USER_PROMPT + "```json\n" + json_data_string + "\n```"
    
    return msg
