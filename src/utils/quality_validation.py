import re


def validate_blog_post(content: str) -> dict:
    """Validate blog post quality and return issues + score."""
    issues = []
    score = 100.0
    words = content.split()

    if len(words) < 500:
        issues.append(f"Too short: {len(words)} words (minimum 500)")
        score -= 20

    if not re.search(r"^#\s+.+", content, re.MULTILINE):
        issues.append("Missing H1 title")
        score -= 15

    if not re.search(r"^##\s+.+", content, re.MULTILINE):
        issues.append("Missing H2 subheadings")
        score -= 10

    if "meta description" not in content.lower():
        issues.append("Missing meta description")
        score -= 10

    return {
        "is_valid": score >= 60,
        "score": max(0, score),
        "issues": issues,
        "word_count": len(words),
    }


def validate_linkedin_post(content: str) -> dict:
    """Validate LinkedIn post quality."""
    issues = []
    score = 100.0
    char_count = len(content)
    hashtags = re.findall(r"#\w+", content)

    if char_count < 500:
        issues.append(f"Too short: {char_count} chars (recommended 1200+)")
        score -= 20
    elif char_count > 3000:
        issues.append(f"Too long: {char_count} chars (LinkedIn limit is ~3000)")
        score -= 15

    if len(hashtags) < 3:
        issues.append(f"Too few hashtags: {len(hashtags)} (recommended 8-12)")
        score -= 10

    if len(hashtags) > 15:
        issues.append(f"Too many hashtags: {len(hashtags)}")
        score -= 5

    paragraphs = [p for p in content.split("\n\n") if p.strip()]
    if len(paragraphs) < 2:
        issues.append("Needs more paragraph breaks for LinkedIn readability")
        score -= 10

    return {
        "is_valid": score >= 60,
        "score": max(0, score),
        "issues": issues,
        "char_count": char_count,
        "hashtag_count": len(hashtags),
    }


def compute_quality_score(content: str, content_type: str) -> float:
    """Return overall quality score 0-100 for given content type."""
    if content_type == "blog":
        return validate_blog_post(content)["score"]
    elif content_type == "linkedin":
        return validate_linkedin_post(content)["score"]
    else:
        # Generic scoring based on length and structure
        score = 70.0
        if len(content.split()) > 300:
            score += 15
        if re.search(r"^##?\s+", content, re.MULTILINE):
            score += 15
        return min(100.0, score)
