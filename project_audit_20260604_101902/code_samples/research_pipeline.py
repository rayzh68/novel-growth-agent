import argparse
import subprocess
import sys


def run(cmd):
    print()
    print("=" * 88)
    print("RUN:", " ".join(cmd))
    print("=" * 88)
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True)
    parser.add_argument("--max-queries", type=int, default=0)
    args = parser.parse_args()

    cmd = [sys.executable, "-m", "research.batch_runner", "--book", args.book]
    if args.max_queries and args.max_queries > 0:
        cmd.extend(["--max-queries", str(args.max_queries)])

    run(cmd)
    run([sys.executable, "-m", "research.cleaner", "--book", args.book])
    run([sys.executable, "-m", "research.analyzer", "--book", args.book])

    print()
    print("=" * 88)
    print("RESEARCH PIPELINE COMPLETED")
    print("=" * 88)


if __name__ == "__main__":
    main()
