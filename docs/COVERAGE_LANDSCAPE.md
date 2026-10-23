# Coverage landscape: tech E&O, cyber, and AI-specific wordings

Context only. This document feeds no model and no preregistered metric; it
records what public sources say about how insurance wordings treat AI risk,
one URL per claim. Collected 2026-10-22. Full policy PDFs are stored in
`data/raw/policy/` with MANIFEST entries; their internal wording has not yet
been reviewed page by page (no PDF text tooling in the research environment;
noted as a limitation).

## AI exclusions are spreading in standard lines

- Berkshire Hathaway, Chubb, and Travelers sought state regulatory approval
  to exclude AI-related damages from general liability policies, and state
  regulators approved more than 80% of those requests.
  https://www.hunton.com/insights/publications/how-insurance-policies-are-adapting-to-ai-risk
- W. R. Berkley filed an "absolute" AI exclusion, the broadest public
  example, aimed at D&O, E&O, and fiduciary liability products and reaching
  any use or development of AI.
  https://natlawreview.com/article/continued-proliferation-ai-exclusions
- An ABA survey of AI insurance notes that published carrier statements
  describe marketed positioning, not what would be paid on a specific claim.
  https://www.americanbar.org/groups/tort_trial_insurance_practice/resources/brief/2025-fall/evolving-landscape-ai-insurance-empirical-insights-risks-policy-gaps/

## AI-specific affirmative covers exist and price performance

- Munich Re aiSure is performance-guarantee insurance for AI solutions, in
  variants for vendor contractual liability, self-built AI (underperformance,
  unreliability, and model drift), and third-party damages; insured systems
  pass a technical due diligence first.
  https://munichre.com/en/solutions/for-industry-clients/insure-ai/ai-whitepaper.html
  and https://munichre.com/en/solutions/for-industry-clients/insure-ai/ai-self.html
- Armilla (Lloyd's syndicates including Chaucer) covers hallucinations,
  performance degradation, and algorithmic failures, and declines medical
  diagnostics and mental-health applications.
  https://www.pymnts.com/artificial-intelligence-2/2026/big-insurance-backs-away-from-ai-risk-and-startups-rush-in/
- Beazley added affirmative AI wording to its cyber and tech E&O policies
  (September 2026).
  https://insurancejournal.com/news/national/2026/09/17/885463.htm

## Stored specimen wordings (raw artifacts)

- Markel UK Technology Combined specimen wording, 134 pages, professional
  liability plus property plus cyber in one form:
  https://content.markel.com/api/public/content/specimen-wording-and-product-information-technology-combined
- Hiscox CyberClear policy summary:
  https://hiscox.co.uk/sites/uk/files/documents/2019-03/19326-CyberClear-policy-summary.pdf
- A tech E&O coverage overview explaining that CGL policies typically do not
  cover third-party financial harm from software errors:
  https://cdn.zephyrcms.com/967865c2-afef-4415-91f9-f68e65d09b4c/-/inline/yes/technology-professional-liability-errors-and-omissions-coverage.pdf

## What this means for the study (one paragraph, no model input)

Carriers are simultaneously excluding AI from standard lines and selling
AI-specific performance covers that depend on technical due diligence. Both
movements assume AI failure risk can be identified and priced, which is the
question this study tests; neither movement publishes the rating factors it
uses, so a validated telemetry-based factor would be novel either way the
result lands.
