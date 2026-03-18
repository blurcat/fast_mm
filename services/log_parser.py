import re
from typing import Dict


def _normalize_line(line: str) -> str:
    """Normalize a log line for deduplication (strip dynamic parts)."""
    line = re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[\.,\d]*(\+\d+)?Z?', '', line)
    line = re.sub(r'\d{2}:\d{2}:\d{2}[\.,\d]*', '', line)
    line = re.sub(r'0x[0-9a-fA-F]+', '0xHEX', line)
    line = re.sub(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', 'UUID', line)
    line = re.sub(r'\b\d{5,}\b', 'N', line)
    line = re.sub(r'\s+', ' ', line).strip()
    return line[:120]


def preprocess_logs(log_text: str, max_chars: int = 8000) -> Dict:
    """
    Preprocess logs to reduce token usage while preserving important information.

    Strategy:
    - Extract ERROR/CRITICAL/FATAL lines with surrounding context
    - Deduplicate similar messages (keep first occurrence + count)
    - Fall back to sampling if no errors found
    - Hard truncate at max_chars
    """
    lines = log_text.strip().split('\n')

    level_pattern = re.compile(
        r'\b(ERROR|CRITICAL|FATAL|WARN(?:ING)?|INFO|DEBUG|TRACE|EXCEPTION|SEVERE)\b',
        re.IGNORECASE,
    )

    parsed = []
    for i, line in enumerate(lines):
        match = level_pattern.search(line)
        level = match.group(1).upper() if match else None
        if level == 'WARNING':
            level = 'WARN'
        parsed.append({'idx': i, 'text': line, 'level': level})

    error_levels = {'ERROR', 'CRITICAL', 'FATAL', 'SEVERE', 'EXCEPTION'}
    warn_levels = {'WARN'}

    stats = {
        'total_lines': len(lines),
        'error_count': sum(1 for p in parsed if p['level'] in error_levels),
        'warning_count': sum(1 for p in parsed if p['level'] in warn_levels),
        'info_count': sum(1 for p in parsed if p['level'] == 'INFO'),
    }

    seen: dict[str, int] = {}
    kept_indices: set[int] = set()

    for i, p in enumerate(parsed):
        level = p['level']
        text = p['text']

        if level in error_levels:
            key = _normalize_line(text)
            if key not in seen:
                # Keep 1 line before + error line + 2 lines after for context
                for j in range(max(0, i - 1), min(len(parsed), i + 3)):
                    kept_indices.add(j)
            seen[key] = seen.get(key, 0) + 1

        elif level in warn_levels:
            key = _normalize_line(text)
            if key not in seen:
                kept_indices.add(i)
            seen[key] = seen.get(key, 0) + 1

    result_lines = []

    # Add dedup summary
    repeated = [(k, v) for k, v in seen.items() if v > 1]
    if repeated:
        result_lines.append("=== Repeated Messages (deduplicated) ===")
        for key, count in repeated[:8]:
            result_lines.append(f"  [x{count}] {key[:80]}")
        result_lines.append("")

    # Add filtered key lines
    if kept_indices:
        result_lines.append("=== Key Log Entries ===")
        prev_idx = -2
        for idx in sorted(kept_indices):
            if idx > prev_idx + 1 and prev_idx >= 0:
                result_lines.append("  ...")
            result_lines.append(parsed[idx]['text'])
            prev_idx = idx
    else:
        # No errors/warnings: send beginning + tail as sample
        result_lines.append("=== Log Sample (no explicit errors detected) ===")
        head = lines[:40]
        tail = lines[-15:] if len(lines) > 55 else []
        result_lines.extend(head)
        if tail:
            result_lines.append("  ...")
            result_lines.extend(tail)

    filtered_text = '\n'.join(result_lines)

    if len(filtered_text) > max_chars:
        filtered_text = filtered_text[:max_chars] + '\n...[truncated: log too large]'

    return {
        'filtered_text': filtered_text,
        'stats': stats,
    }
