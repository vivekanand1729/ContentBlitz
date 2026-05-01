import re


def calculate_seo_score(content: str, keyword: str) -> float:
    """Score SEO quality 0-100 based on common optimization factors."""
    score = 0.0
    text_lower = content.lower()
    keyword_lower = keyword.lower()
    words = content.split()
    word_count = len(words)

    # Word count (target 800+)
    if word_count >= 800:
        score += 20
    elif word_count >= 500:
        score += 12
    elif word_count >= 300:
        score += 6

    # Keyword in title/H1
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h1_match and keyword_lower in h1_match.group(1).lower():
        score += 15

    # Has meta description
    if "meta description" in text_lower:
        score += 10

    # Keyword density (1-3% is ideal)
    keyword_count = text_lower.count(keyword_lower)
    if word_count > 0:
        density = keyword_count / word_count
        if 0.01 <= density <= 0.03:
            score += 15
        elif 0.005 <= density < 0.01:
            score += 8

    # Has H2 subheadings
    h2_count = len(re.findall(r"^##\s+", content, re.MULTILINE))
    if h2_count >= 3:
        score += 10
    elif h2_count >= 1:
        score += 5

    # Has H3 subheadings
    if re.search(r"^###\s+", content, re.MULTILINE):
        score += 5

    # Has bullet lists
    if re.search(r"^[-*]\s+", content, re.MULTILINE):
        score += 5

    # Has call to action
    cta_phrases = ["contact us", "learn more", "get started", "sign up", "download", "click here", "subscribe"]
    if any(phrase in text_lower for phrase in cta_phrases):
        score += 10

    # Has numbers/statistics
    if re.search(r"\d+%|\$\d+|\d+ million|\d+ billion", content):
        score += 10

    return min(round(score, 1), 100.0)


def calculate_readability(content: str) -> float:
    """Estimate Flesch Reading Ease score (0-100, higher = easier to read)."""
    sentences = re.split(r"[.!?]+", content)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = content.split()

    if not sentences or not words:
        return 0.0

    avg_sentence_length = len(words) / len(sentences)
    # Approximate syllable count: count vowel groups
    syllables = sum(max(1, len(re.findall(r"[aeiouAEIOU]+", word))) for word in words)
    avg_syllables_per_word = syllables / len(words) if words else 1

    flesch = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    return round(max(0.0, min(100.0, flesch)), 1)


def extract_hashtags(content: str) -> list[str]:
    """Extract hashtags from content."""
    return re.findall(r"#\w+", content)


def generate_meta_description(content: str) -> str:
    """Extract or generate a meta description from content."""
    meta_match = re.search(r"\*\*Meta Description:\*\*\s*(.+?)(?:\n|$)", content)
    if meta_match:
        return meta_match.group(1).strip()[:160]

    # Fall back to first non-heading paragraph
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and not p.startswith("#")]
    if paragraphs:
        return paragraphs[0][:160]
    return ""
