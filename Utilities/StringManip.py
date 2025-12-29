

def squash_string(s: str) -> str:
    return " ".join(line.strip() for line in s.strip().splitlines() if line.strip())