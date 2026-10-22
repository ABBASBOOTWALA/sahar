"""Re-fetch only the concepts whose samples came back empty.

The first pass hit OpenAlex's anonymous rate limit about forty requests in and
silently recorded empty lists. Empty is a claim, so it has to be either true or
refetched. This paces the requests and retries with backoff.
"""
import io
import json
import time
import urllib.parse
import urllib.request

from sahar import concepts, controls_v2, openalex, resolve, threshold

C_REF, BETA = 12, 0.0
API = "https://api.openalex.org/works"
STEM = "|".join(f"https://openalex.org/fields/{j}"
                for j in [11, 12, 13, 16, 17, 21, 22, 25, 27, 31])


def works(filters, per_page=6):
    url = API + "?" + urllib.parse.urlencode(
        {"filter": ",".join(filters), "per-page": per_page, "sort": "publication_year"})
    req = urllib.request.Request(url, headers={"User-Agent": "SaharProject"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.load(r)
            out = []
            for w in d.get("results", []):
                src = ((w.get("primary_location") or {}).get("source") or {})
                out.append({"y": w.get("publication_year"),
                            "t": (w.get("title") or "untitled")[:150],
                            "v": (src.get("display_name") or "")[:70],
                            "ty": w.get("type") or ""})
            return out, True
        except Exception as e:
            if attempt == 4:
                print(f"      gave up: {e}")
                return [], False
            time.sleep(2 ** attempt)
    return [], False


def main():
    b = json.loads(io.open('data/ui_bundle.json', encoding='utf-8').read())
    samples = b["samples"]
    totals = openalex.total_counts()
    strat = resolve.PhraseField()
    pool = {c.terms[0].lower(): c for c in
            controls_v2.UNCONTESTED + list(concepts.CONTROLS) + controls_v2.CONTESTED}

    todo = [k for k, s in samples.items() if s.get("na")]
    print(f"re-fetching {len(todo)} concepts with no samples")

    for i, key in enumerate(todo, 1):
        c = pool[key]
        phrase = openalex.phrase_query(c.terms)
        on = threshold.onset(strat.counts(c), totals, C_REF, BETA)

        earliest, ok1 = works([f"title_and_abstract.search:{phrase}",
                               openalex.exclude_leonardo(),
                               f"publication_year:<{c.science_origin}"])
        time.sleep(6.0)
        around, ok2 = ([], True)
        if on:
            around, ok2 = works([f"title_and_abstract.search:{phrase}",
                                 openalex.exclude_leonardo(),
                                 f"primary_topic.field.id:{STEM}",
                                 f"publication_year:{on}-{on + 1}"])
            time.sleep(6.0)

        samples[key] = {"e": earliest, "a": around, "on": on}
        if not (ok1 and ok2):
            samples[key]["na"] = True
        flag = "" if (ok1 and ok2) else "  (request failed)"
        print(f"{i:>3}/{len(todo)}  {c.name:<34} earliest {len(earliest):>2}  "
              f"onset {len(around):>2}{flag}")

    b["samples"] = samples
    s = json.dumps(b, separators=(',', ':'))
    io.open('data/ui_bundle.json', 'w', encoding='utf-8').write(s)
    still = [k for k, v in samples.items() if v.get("na")]
    print(f"\nbundle {len(s)/1024:.0f} KB; still empty: {len(still)}")
    if still:
        print("  ", ", ".join(still))


if __name__ == "__main__":
    main()
