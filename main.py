"""Entry point for the Recruitech ATS scoring agent. Run the Kafka consumer by default."""
from consumer import run_consumer

if __name__ == "__main__":
    run_consumer()
