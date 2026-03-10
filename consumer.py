"""Kafka consumer: read JD + resume S3 URL, score with LLM, produce result to output topic."""
import json
import logging
import traceback

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

from config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_GROUP_ID,
    KAFKA_INPUT_TOPIC,
    KAFKA_OUTPUT_TOPIC,
)
from scorer import score_resume_vs_jd
from s3_resume_loader import get_resume_text_from_s3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Expected input message (JSON): { "job_description": "...", "resume_s3_url": "s3://bucket/key" }
# Optional: "message_id", "correlation_id" for tracing
# Output: same ids + "score_result": { ... from scorer }, "error": null or string


def run_consumer():
    consumer = KafkaConsumer(
        KAFKA_INPUT_TOPIC,
        
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(","),
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")) if m else None,
    )
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(","),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    logger.info("Consuming from %s, producing to %s", KAFKA_INPUT_TOPIC, KAFKA_OUTPUT_TOPIC)

    for message in consumer:
        try:
            payload = message.value
            logger.info("Consumed message from %s: %s", KAFKA_INPUT_TOPIC, payload)
            if not payload:
                continue
            jd = payload.get("job_description") or payload.get("jd") or ""
            resume_s3_url = payload.get("resume_s3_url") or payload.get("resume_url") or ""
            message_id = payload.get("message_id") or payload.get("id")
            correlation_id = payload.get("correlation_id")

            if not resume_s3_url:
                out = {
                    "message_id": message_id,
                    "correlation_id": correlation_id,
                    "score_result": None,
                    "error": "missing resume_s3_url",
                }
                producer.send(KAFKA_OUTPUT_TOPIC, value=out)
                producer.flush()
                continue

            resume_text = get_resume_text_from_s3(resume_s3_url)
            score_result = score_resume_vs_jd(jd, resume_text)

            out = {
                "message_id": message_id,
                "correlation_id": correlation_id,
                "score_result": score_result,
                "error": None,
            }
            producer.send(KAFKA_OUTPUT_TOPIC, value=out)
            producer.flush()
            logger.info("Scored message_id=%s overall_score=%s", message_id, score_result.get("overall_score"))

        except KafkaError as e:
            logger.exception("Kafka error: %s", e)
            _send_error(producer, payload, str(e))
        except Exception as e:
            logger.exception("Processing error: %s", e)
            _send_error(producer, payload, f"{e}\n{traceback.format_exc()}")


def _send_error(producer, payload: dict | None, error_msg: str):
    try:
        out = {
            "message_id": (payload or {}).get("message_id") or (payload or {}).get("id"),
            "correlation_id": (payload or {}).get("correlation_id"),
            "score_result": None,
            "error": error_msg,
        }
        producer.send(KAFKA_OUTPUT_TOPIC, value=out)
        producer.flush()
    except Exception as e:
        logger.exception("Failed to send error reply: %s", e)


if __name__ == "__main__":
    run_consumer()
