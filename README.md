# Recruitech ATS scoring agent

AI agent that scores how well a candidate’s resume matches a job description (ATS-style). It reads **job description** and **resume S3 URL** from Kafka, fetches the resume from S3, runs an LLM rubric, and writes the **score result** to an output Kafka topic.

## Where to start

1. **Environment**
   - Copy `.env.example` to `.env` and set at least:
     - `OPENAI_API_KEY`
     - Kafka: `KAFKA_BOOTSTRAP_SERVERS` (and topics if you change them)
     - AWS: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` (or IAM role if running on AWS)

2. **Install**
   ```bash
   cd /path/to/Recruitech-agent1
   pip install -r requirements.txt
   ```

3. **Run the agent**
   ```bash
   python main.py
   ```
   (Or `python consumer.py`.) Ensure Kafka is running and the input topic exists. Send a test message (see below), then check the output topic for the score payload.

4. **Test without Kafka (optional)**  
   Use the scorer and S3 loader directly from Python:
   ```python
   from s3_resume_loader import get_resume_text_from_s3
   from scorer import score_resume_vs_jd

   resume_text = get_resume_text_from_s3("s3://your-bucket/resume.pdf")
   result = score_resume_vs_jd("Your job description...", resume_text)
   print(result["overall_score"], result["matched_skills"], result["missing_skills"])
   ```

## Cost

`gpt-4o-mini` is cheap and good at structured JSON (~$0.15/1M input, ~$0.60/1M output). Keeping prompts concise and `LLM_MAX_TOKENS=1024` (or 512) helps minimize cost.

## Kafka message format

**Input** (topic: `KAFKA_INPUT_TOPIC`, default `recruitech.scoring.input`):

- `job_description` or `jd`: string
- `resume_s3_url` or `resume_url`: string (e.g. `s3://bucket/key` or presigned HTTPS URL)
- Optional: `message_id`, `correlation_id` for tracing

Example:
```json
{
  "job_description": "We need a Python developer with 3+ years...",
  "resume_s3_url": "s3://my-bucket/candidates/jane_resume.pdf",
  "message_id": "msg-123"
}
```

**Output** (topic: `KAFKA_OUTPUT_TOPIC`, default `recruitech.scoring.output`):

- `message_id`, `correlation_id`: echoed from input
- `score_result`: object with `skills_match_score`, `experience_score`, `projects_score`, `education_score`, `overall_score`, `matched_skills`, `missing_skills`, `strengths`, `weaknesses`, `explanation`
- `error`: `null` or error string if something failed

## Project layout

- `main.py` — entry point (runs the Kafka consumer)
- `config.py` — settings from env (LLM, Kafka, AWS)
- `s3_resume_loader.py` — fetch object from S3, extract text (PDF or .txt)
- `scorer.py` — LLM scoring with the ATS rubric, returns JSON
- `consumer.py` — Kafka consumer: read input → load resume → score → produce output
- `.env.example` — template for `.env`

## Scoring rubric (in prompt)

- Skills Match: 0–40  
- Experience Relevance: 0–30  
- Projects: 0–20  
- Education: 0–10  
- **Total: 0–100**

The model returns only JSON in the shape above; the consumer forwards it in `score_result`.
