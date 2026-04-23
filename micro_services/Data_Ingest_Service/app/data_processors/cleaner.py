# app/services/cleaning.py
class CleaningService:

    def clean(self, articles):
        cleaned = []

        for a in articles:

            # basic validation
            if not a.get("title") or not a.get("content"):
                continue

            if len(a["content"]) < 100:
                continue

            # normalize text
            a["title"] = a["title"].strip()
            a["content"] = a["content"].strip()
            a["summary"] = (a.get("summary") or "").strip()

            cleaned.append(a)

        return cleaned