"""Run scoring once (no Kafka). Usage: JD from stdin or --jd file, resume from --resume path or S3 URL."""
import argparse
import json
import sys
from pathlib import Path

from scorer import score_resume_vs_jd
from s3_resume_loader import get_resume_text_from_s3, _pdf_to_text


def main():
    parser = argparse.ArgumentParser(description="Score resume vs JD once (no Kafka)")
    parser.add_argument("--jd", type=str, help="Job description text or path to file")
    parser.add_argument("--resume", type=str, required=True, help="Resume: file path or s3:// URL")
    parser.add_argument("--json", action="store_true", help="Output only JSON")
    args = parser.parse_args()

    if args.jd:
        jd = args.jd
        if len(jd) < 500 and not jd.strip().startswith("{") and "\n" not in jd:
            try:
                with open(args.jd) as f:
                    jd = f.read()
            except FileNotFoundError:
                pass
    else:
        jd = sys.stdin.read().strip()
    if not jd:
        print("Error: provide --jd or pipe job description on stdin", file=sys.stderr)
        sys.exit(1)

    if args.resume.startswith("s3://") or "s3." in args.resume or ".s3." in args.resume:
        resume_text = get_resume_text_from_s3(args.resume)
    else:
        path = Path(args.resume)
        if not path.exists():
            print(f"Error: resume file not found: {path}", file=sys.stderr)
            sys.exit(1)
        if path.suffix.lower() == ".pdf":
            data = path.read_bytes()
            resume_text = _pdf_to_text(data)
        else:
            # Text-like files
            with open(path, encoding="utf-8", errors="replace") as f:
                resume_text = f.read()

    result = score_resume_vs_jd(jd, resume_text)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Overall:", result.get("overall_score", 0), "/ 100")
        print("Matched skills:", result.get("matched_skills", []))
        print("Missing skills:", result.get("missing_skills", []))
        print("Explanation:", result.get("explanation", "")[:500])


if __name__ == "__main__":
    main()
