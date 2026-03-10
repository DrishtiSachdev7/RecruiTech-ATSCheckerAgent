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

