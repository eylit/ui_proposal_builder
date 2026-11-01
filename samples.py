"""Sample inputs for the demo. Everything here is invented. Edit freely.

Each sample fills the Client Name box and the draft points box. A sample with a "report" also attaches that
invented vendor lab report PDF (made by make_sample_reports.py).
"""

SAMPLES = [
    {
        "name": "Sample 1: Clinic lab results",
        "company": "Maple Grove Clinics",
        "report": "samples/meridian_bioage_report.pdf",
        "brief": (
            "- Build a patient web page and a report layout from the attached Meridian Biosciences BioAge report (invented).\n"
            "- Show the key test patients can influence with lifestyle: Aging Tempo. Add Cellular Age Index as a second test.\n"
            "- Show each result with its value and unit, and the normal range where the report has one "
            "(Aging Tempo has one, Cellular Age Index has none).\n"
            "- Status labels: Aging Tempo = Slower pace, Average pace, Faster pace. "
            "Cellular Age Index = Younger, Similar, Older.\n"
            "- Nurses key in the results by hand; patients only view the report.\n"
            "- Show the last three sessions as a trend for each test.\n"
            "- Show a recommendation only for abnormal results, for example: talk to your doctor about slowing the pace.\n"
            "- Audience: patients, non-technical. Keep the wording simple and reassuring."
        ),
    },
    {
        "name": "Sample 2: Kidney health (text only)",
        "company": "LiveFull Health",
        "report": None,
        "brief": (
            "- Build a kidney health panel for our wellness clinics.\n"
            "- Key test: eGFR (kidney filtration), unit mL/min/1.73 m2, normal range 90 or higher. "
            "Status labels: Normal, Mildly reduced, Reduced.\n"
            "- Second test: Serum creatinine, result value 50 umol/L, normal range 45 to 90. "
            "Status labels: Normal, Slightly high, High.\n"
            "- Result will automatically sync in from lab; patients only view the report.\n"
            "- Show the last three sessions for eGFR as a trend: Jan 2025 = 98, Apr 2025 = 92, Jul 2025 = 88.\n"
            "- Show a recommendation only when a result is abnormal, for example: drink enough water and talk to your "
            "doctor about your kidney results.\n"
            "- The report shows the panel icon, the value with its unit, the normal range and a one-line summary."
        ),
    },
    {
        "name": "Sample 3: Gut wellness report",
        "company": "Greenfield Digestive Care",
        "report": "samples/fernhill_gut_report.pdf",
        "brief": (
            "- Build a patient web page and a report layout from the attached Fernhill Microbiome Labs gut wellness report (invented).\n"
            "- Use one panel, Gut Health, with 4 tests: Mind-Gut Link, Defence Balance, Energy Balance and Nutrient Processing.\n"
            "- Each test is a score from 1 to 10. Show the score as the result, with a normal range of 5 to 10.\n"
            "- Status labels for all four tests: Poor (1 to 4), Good (5 to 7), Great (8 to 10).\n"
            "- Nurses key in the scores by hand; patients only view the report.\n"
            "- Show a recommendation only for Poor results, for example: eat more fibre and plant foods, sleep 7 to 8 hours, "
            "and talk to your doctor.\n"
            "- Audience: patients, non-technical. Keep the wording simple and reassuring."
        ),
    },
]
