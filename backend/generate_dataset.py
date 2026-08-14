"""
Generates datasets/clause_dataset.csv — a labeled, bilingual (English +
Nepali) dataset of legal clause sentences by clause type.

This is template-generated (documented honestly, not passed off as a
scraped "real-world" corpus) so the labels are trustworthy and it's
reproducible. It exists so trainer.py has actual data to train and
evaluate a real classifier on, instead of the empty `datasets/` folder
that shipped before.

Run: python generate_dataset.py
"""
import csv
import random
from pathlib import Path

random.seed(42)

PARTIES = ["employee", "contractor", "tenant", "borrower", "supplier",
           "service provider", "buyer", "seller", "vendor", "consultant"]
DUTIES = ["submit the required documents", "complete the assigned work",
          "maintain accurate records", "attend all scheduled meetings",
          "follow the company's code of conduct", "report any changes in circumstances",
          "provide monthly progress reports", "comply with safety regulations",
          "deliver the goods as specified", "maintain the property in good condition"]
TIMEFRAMES = ["thirty days", "fifteen days", "one month", "sixty days",
              "seven business days", "the agreed period", "two weeks"]
AMOUNTS = ["Rs. 50,000", "Rs. 1,00,000", "the outstanding balance",
           "the total contract value", "Rs. 25,000", "the agreed fee"]
EVENTS = ["delivery of goods", "completion of the project", "signing of this agreement",
          "the end of the fiscal year", "receipt of invoice"]
REASONS = ["material breach of contract", "non-payment", "failure to perform duties",
           "mutual written consent", "insolvency of either party"]
INFO = ["business information", "trade secrets", "client data",
        "financial records", "proprietary technical information"]
RISKS = ["third-party claims", "property damage", "personal injury",
         "losses arising from negligence", "defective goods"]
TERMS = ["party", "goods", "effective date", "confidential information", "agreement"]
MEANINGS = ["either the buyer or the seller", "all items listed in the attached schedule",
            "the date on which this agreement is signed", "any non-public business data",
            "this written contract and its appendices"]
JURISDICTIONS = ["Nepal", "the applicable jurisdiction", "the courts of Kathmandu"]

OBLIGATION_TEMPLATES = [
    "The {party} shall {duty}.",
    "The {party} must {duty} within {timeframe}.",
    "It is the responsibility of the {party} to {duty}.",
    "The {party} is required to {duty} at all times.",
]
PAYMENT_TEMPLATES = [
    "The {party} shall pay {amount} within {timeframe}.",
    "Payment of {amount} is due upon {event}.",
    "A late fee shall apply to any overdue payment of {amount}.",
    "The {party} agrees to pay {amount} in accordance with the agreed schedule.",
]
TERMINATION_TEMPLATES = [
    "This agreement may be terminated by either party with {timeframe} written notice.",
    "The contract shall terminate upon {event}.",
    "Either party may terminate this agreement in the event of {reason}.",
    "This agreement shall automatically expire upon {event}.",
]
CONFIDENTIALITY_TEMPLATES = [
    "The parties agree to keep all {info} confidential.",
    "Neither party shall disclose {info} to third parties without prior written consent.",
    "All {info} shared under this agreement shall remain confidential.",
]
PENALTY_TEMPLATES = [
    "Failure to comply will result in a penalty of {amount}.",
    "Any breach of this clause shall attract a fine of {amount}.",
    "Late performance shall be subject to liquidated damages of {amount}.",
]
INDEMNITY_TEMPLATES = [
    "The {party} shall indemnify and hold harmless the other party against {risk}.",
    "Each party agrees to be liable for damages caused by {risk}.",
    "The {party} shall bear full responsibility for {risk}.",
]
DEFINITION_TEMPLATES = [
    "For the purposes of this agreement, '{term}' means {meaning}.",
    "The term '{term}' refers to {meaning}.",
    "'{term}' shall be interpreted to mean {meaning}.",
]
GOVERNING_LAW_TEMPLATES = [
    "This agreement shall be governed by the laws of {jurisdiction}.",
    "Any dispute arising from this contract shall be subject to the jurisdiction of {jurisdiction}.",
    "This contract shall be interpreted in accordance with the law of {jurisdiction}.",
]
GENERAL_SENTENCES = [
    "The meeting was held in the main conference room.",
    "The company was founded in the year 2010.",
    "This document contains five sections and two appendices.",
    "The parties met on multiple occasions to discuss the terms.",
    "A copy of this agreement shall be kept on file by both parties.",
    "This document is written in both English and Nepali.",
    "The signatures of both parties appear at the end of this document.",
    "The following terms are used throughout this agreement.",
    "Both parties have read and understood the contents of this agreement.",
    "This agreement consists of the main body and attached schedules.",
]

NEPALI_EXAMPLES = {
    "obligation": [
        "कर्मचारीले मासिक प्रतिवेदन पेश गर्नु अनिवार्य छ ।",
        "ठेकेदारले तोकिएको समयभित्र काम सम्पन्न गर्नुपर्छ ।",
        "पक्षले यो सम्झौता अनुसार आफ्नो कर्तव्य पालना गर्नु पर्दछ ।",
        "भाडावालले सम्पत्ति राम्रो अवस्थामा राख्नुपर्नेछ ।",
        "आपूर्तिकर्ताले गुणस्तरीय सामान उपलब्ध गराउनु पर्नेछ ।",
    ],
    "payment": [
        "खरिदकर्ताले तोकिएको रकम तिर्नु पर्नेछ ।",
        "भुक्तानी सम्झौता भएको मितिले तीस दिनभित्र गर्नुपर्छ ।",
        "तलब प्रत्येक महिनाको अन्तिम दिन भुक्तानी गरिनेछ ।",
        "ढिलो भुक्तानीमा जरिवाना लाग्नेछ ।",
    ],
    "termination": [
        "यो सम्झौता कुनै पनि पक्षले लिखित सूचना दिई खारेज गर्न सक्नेछ ।",
        "सम्झौता उल्लंघन भएमा अर्को पक्षले करार रद्द गर्न सक्नेछ ।",
        "काम सकिएपछि यो सम्झौता स्वतः समाप्त हुनेछ ।",
    ],
    "confidentiality": [
        "गोप्य जानकारी अरु कसैलाई खुलासा गर्न पाइने छैन ।",
        "यस सम्झौता अन्तर्गतको जानकारी गोप्य राखिनेछ ।",
        "व्यापारिक गोप्य कुराहरू तेस्रो पक्षलाई दिन पाइँदैन ।",
    ],
    "penalty": [
        "उल्लंघन गरेमा जरिवाना लाग्नेछ ।",
        "करार भंग गरेमा क्षतिपूर्ति तिर्नुपर्नेछ ।",
        "ढिलाइको लागि दण्ड शुल्क लगाइनेछ ।",
    ],
    "indemnity": [
        "ठेकेदारले सबै दाबी र क्षतिको लागि क्षतिपूर्ति दिनुपर्नेछ ।",
        "कुनै पनि क्षतिको लागि सम्बन्धित पक्ष जिम्मेवार हुनेछ ।",
    ],
    "definition": [
        "यस सम्झौताको प्रयोजनको लागि 'पक्ष' भन्नाले खरिदकर्ता वा बिक्रेता जनाउँछ ।",
        "'सामान' भन्नाले अनुसूचीमा उल्लेखित सबै वस्तुहरू जनाउँछ ।",
    ],
    "governing_law": [
        "यो सम्झौता नेपालको कानून बमोजिम सञ्चालित हुनेछ ।",
        "कुनै विवाद भएमा नेपाली अदालतको अधिकार क्षेत्र हुनेछ ।",
    ],
    "general": [
        "यो सम्झौता अंग्रेजी र नेपाली दुबै भाषामा लेखिएको छ ।",
        "बैठक मुख्य कार्यालयमा आयोजना गरिएको थियो ।",
        "यस कागजातमा पाँच खण्डहरू छन् ।",
        "दुबै पक्षले सम्झौताको सर्तहरू बुझेका छन् ।",
    ],
}


def generate_english(templates, category, count):
    rows = []
    for _ in range(count):
        t = random.choice(templates)
        sentence = t.format(
            party=random.choice(PARTIES),
            duty=random.choice(DUTIES),
            timeframe=random.choice(TIMEFRAMES),
            amount=random.choice(AMOUNTS),
            event=random.choice(EVENTS),
            reason=random.choice(REASONS),
            info=random.choice(INFO),
            risk=random.choice(RISKS),
            term=random.choice(TERMS),
            meaning=random.choice(MEANINGS),
            jurisdiction=random.choice(JURISDICTIONS),
        )
        rows.append((sentence, category, "english"))
    return rows


def main():
    rows = []

    rows += generate_english(OBLIGATION_TEMPLATES, "obligation", 30)
    rows += generate_english(PAYMENT_TEMPLATES, "payment", 25)
    rows += generate_english(TERMINATION_TEMPLATES, "termination", 25)
    rows += generate_english(CONFIDENTIALITY_TEMPLATES, "confidentiality", 20)
    rows += generate_english(PENALTY_TEMPLATES, "penalty", 20)
    rows += generate_english(INDEMNITY_TEMPLATES, "indemnity", 18)
    rows += generate_english(DEFINITION_TEMPLATES, "definition", 18)
    rows += generate_english(GOVERNING_LAW_TEMPLATES, "governing_law", 18)

    # General/negative class — repeat with slight sampling to balance a bit
    for _ in range(25):
        rows.append((random.choice(GENERAL_SENTENCES), "general", "english"))

    # Nepali examples (hand-written, smaller set — repeated with no
    # duplication issues since dedup happens at train time via stratified split)
    for category, examples in NEPALI_EXAMPLES.items():
        for ex in examples:
            rows.append((ex, category, "nepali"))

    # dedupe exact duplicates (English templates can occasionally collide)
    seen = set()
    unique_rows = []
    for r in rows:
        if r[0] not in seen:
            seen.add(r[0])
            unique_rows.append(r)

    random.shuffle(unique_rows)

    out_dir = Path(__file__).parent / "datasets"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "clause_dataset.csv"

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label", "language"])
        writer.writerows(unique_rows)

    print(f"Wrote {len(unique_rows)} labeled examples to {out_path}")
    from collections import Counter
    print("Label distribution:", dict(Counter(r[1] for r in unique_rows)))


if __name__ == "__main__":
    main()
