# SEO / AEO / GEO + Conversion Plan

Audit date: July 13, 2026  
Site reviewed: https://anthony-baptiste.com/  
Pages reviewed: `/`, `/consulting/`, `/projects/`, `/experience/`, `/research/`  

Confirmed status: Anthony Baptiste is a Northern Illinois University graduate. Use graduate/alumni wording consistently across page copy, schema, `llms.txt`, and social profiles.

## 1. Quick Audit

| Priority | Problem hurting traffic or conversion | Fix | Effort |
|---:|---|---|---|
| 1 | Identity inconsistency weakens trust and entity clarity. Homepage previously used student-status wording while schema said NIU alumnus and experience used undergraduate wording. | Use one status everywhere: Northern Illinois University graduate. Update homepage bio, Person schema, experience labels, resume page, `llms.txt`, and social bios. | Low |
| 2 | The site has one strong consulting page, but each core offer does not have its own search-intent page. | Create focused service pages: `/consulting/analytics-audit/`, `/consulting/dashboard-reporting/`, `/consulting/digital-analytics-experimentation/`, `/consulting/applied-ai-workflows/`. | Med |
| 3 | Homepage title is brand-led and broad, not local or buyer-intent-led. | Use a clearer title: `Analytics Consultant in Chicago | Dashboards & KPI Reporting`. | Low |
| 4 | `/projects/`, `/experience/`, and `/research/` have schema but weaker lead capture than `/consulting/`. | Add a small “Work with me on this type of problem” CTA after each proof section, linking to the relevant offer anchor or service page. | Low |
| 5 | FAQ schema exists, but service-specific FAQs are too thin. | Add 4-6 FAQs per service page and keep each answer self-contained. | Med |
| 6 | Proof is credible, but some logo/proof sections could be mistaken for client endorsements. | Keep the existing disclaimer and repeat “roles, internships, student consulting, competitions, and projects; not endorsements” near proof grids and schema descriptions. | Low |
| 7 | Above-the-fold copy is good but slightly tool-heavy. | Lead with the buyer problem and outcome, then tools. Use the hero rewrite below. | Low |
| 8 | Lead magnet uses `mailto:` form submission, which creates friction and weak tracking. | Replace with a simple form endpoint later; for now keep the direct PDF plus email CTA and track clicks in GA4. | Med |
| 9 | Local SEO is underdeveloped: no address/phone is listed, and “Chicago / Northern Illinois” appears but is not reinforced off-page. | If you have a public business address/phone, add consistent NAP. If not, use service-area language and build citations that allow service-area businesses. | Med |
| 10 | Sitemap/robots are present, but structured data should be tested after each schema change. | Validate JSON-LD with Schema.org Validator and Rich Results Test after edits; submit updated sitemap in Search Console. | Low |

## 2. Keyword & Intent Map

| Query | Intent group | Page that should own it | Primary keyword | Secondary keyword |
|---|---|---|---|---|
| analytics consultant chicago | Local/service | `/consulting/` | analytics consultant chicago | BI consultant chicago |
| power bi consultant chicago | Local/service | new `/consulting/dashboard-reporting/` | power bi consultant chicago | dashboard consultant chicago |
| tableau consultant chicago | Local/service | new `/consulting/dashboard-reporting/` | tableau consultant chicago | tableau dashboard consultant |
| small business dashboard consultant | Local/service | new `/consulting/dashboard-reporting/` | small business dashboard consultant | KPI dashboard consultant |
| nonprofit dashboard consultant | Local/service | new `/consulting/dashboard-reporting/` | nonprofit dashboard consultant | grant reporting dashboard |
| ecommerce analytics consultant | Local/service | new `/consulting/digital-analytics-experimentation/` | ecommerce analytics consultant | conversion analytics consultant |
| salesforce reporting consultant | Local/service | new `/consulting/dashboard-reporting/` | salesforce reporting consultant | CRM reporting dashboards |
| clean up messy sales data | Problem-aware | new `/resources/clean-up-sales-data/` | clean up messy sales data | data cleanup consultant |
| how to build a KPI dashboard | Problem-aware | new `/resources/kpi-dashboard-guide/` | how to build a KPI dashboard | KPI dashboard checklist |
| dashboard data is wrong | Problem-aware | new `/consulting/analytics-audit/` | dashboard data is wrong | dashboard audit |
| too many spreadsheets reporting | Problem-aware | new `/consulting/analytics-audit/` | spreadsheet reporting cleanup | manual reporting automation |
| how to read A/B test results | Problem-aware | new `/resources/ab-test-readout/` | how to read A/B test results | A/B test analysis |
| Adobe Target test analysis | Bottom-funnel | new `/consulting/digital-analytics-experimentation/` | Adobe Target test analysis | Adobe Target consultant |
| Adobe Analytics consultant | Bottom-funnel | new `/consulting/digital-analytics-experimentation/` | Adobe Analytics consultant | Customer Journey Analytics consultant |
| hire tableau freelancer | Bottom-funnel | new `/consulting/dashboard-reporting/` | hire tableau freelancer | Tableau freelancer |
| hire power bi freelancer | Bottom-funnel | new `/consulting/dashboard-reporting/` | hire power bi freelancer | Power BI dashboard freelancer |
| fractional analytics consultant | Bottom-funnel | `/consulting/` | fractional analytics consultant | monthly reporting support |
| KPI reporting consultant | Bottom-funnel | `/consulting/` | KPI reporting consultant | KPI reporting system |
| business intelligence consultant for startups | Bottom-funnel | `/consulting/` | business intelligence consultant startups | startup analytics consultant |
| custom GPT workflow consultant | Bottom-funnel | new `/consulting/applied-ai-workflows/` | custom GPT workflow consultant | AI workflow automation consultant |
| Streamlit app consultant | Bottom-funnel | new `/consulting/applied-ai-workflows/` | Streamlit app consultant | analytics app consultant |

## 3. Page-by-Page On-Page SEO

### Homepage `/`

Title:
```html
<title>Analytics Consultant in Chicago | Dashboards & KPI Reporting</title>
<meta name="description" content="Analytics consulting for teams with messy data. Dashboards, KPI reporting, A/B test readouts, data cleanup, and practical AI workflows.">
```

H1: `Analytics consulting for messy reporting, unclear KPIs, and tests your team needs to trust.`

Recommended structure:
- H2: Quick answer: what I do, who I help, what it costs
- H2: Consulting offers
- H2: Proof from analytics roles and projects
- H2: How engagements work
- H2: Start with a focused analytics problem

Copy rewrite near hero:
> I help startups, ecommerce teams, nonprofits, research groups, and operations teams turn scattered data into dashboards, KPI reporting, A/B test readouts, and practical AI workflows. The goal is simple: make the numbers easier to trust and the next decision easier to explain.

Internal links to add:
- Homepage “Dashboard & Reporting Sprint” -> `/consulting/dashboard-reporting/` with anchor `dashboard and reporting sprint`.
- Homepage “A/B test readouts” -> `/consulting/digital-analytics-experimentation/` with anchor `A/B test analysis and Adobe Target readouts`.
- Homepage “AI workflow systems” -> `/consulting/applied-ai-workflows/` with anchor `applied AI workflow systems`.

Image alt text:
- Portrait: `Anthony Baptiste, Chicago analytics consultant and BI developer`.
- Logos: keep brand logo alt text, but ensure visible disclaimer stays nearby.

### Consulting `/consulting/`

Title:
```html
<title>Analytics Consulting Services | Dashboards, A/B Tests & AI</title>
<meta name="description" content="Hire Anthony Baptiste for analytics audits, KPI dashboards, Adobe Analytics and A/B test readouts, reporting systems, and AI workflow tools.">
```

H1: `Analytics consulting services for teams that need cleaner reporting and clearer decisions.`

Recommended structure:
- H2: When to bring me in
- H2: Analytics Clarity Audit
- H2: Dashboard & Reporting Sprint
- H2: Digital Analytics & Experimentation Sprint
- H2: Applied AI Workflow Sprint
- H2: Process
- H2: FAQ

Copy rewrite under intro:
> Use this page when your team has data, but not a reporting system people fully trust. I help define the decision, clean up the data path, build the dashboard or readout, and hand off documentation your team can use after the project.

Internal links:
- Consulting -> `/projects/` anchor `analytics case studies`.
- Consulting -> `/experience/` anchor `experience behind the work`.
- Consulting -> `/research/` anchor `applied AI research`.

### New Service Page: `/consulting/analytics-audit/`

Title:
```html
<title>Analytics Audit Consultant | KPI & Dashboard Review</title>
<meta name="description" content="Find broken KPIs, dashboard gaps, reporting issues, and messy data paths before you spend money on a bigger analytics build.">
```

H1: `Analytics audit for teams that do not trust their reporting yet.`

Recommended structure:
- H2: What the audit finds
- H2: What you get
- H2: Best-fit teams
- H2: Price and timeline
- H2: FAQ

### New Service Page: `/consulting/dashboard-reporting/`

Title:
```html
<title>Dashboard Consultant | Power BI, Tableau & KPI Reporting</title>
<meta name="description" content="Dashboard and KPI reporting builds using Tableau, Power BI, SQL, Excel, Salesforce data, and clean metric definitions.">
```

H1: `Dashboard and KPI reporting consultant for teams with messy data.`

Recommended structure:
- H2: What I build
- H2: Data sources and tools
- H2: Proof from Shipt and Innovation DuPage
- H2: Typical sprint deliverables
- H2: FAQ

### New Service Page: `/consulting/digital-analytics-experimentation/`

Title:
```html
<title>A/B Test Analysis Consultant | Adobe Analytics & Target</title>
<meta name="description" content="A/B test analysis, Adobe Target readouts, Adobe Analytics, Customer Journey Analytics, funnel diagnostics, and conversion KPI reporting.">
```

H1: `A/B test and digital analytics readouts your team can act on.`

Recommended structure:
- H2: When a test needs a clearer readout
- H2: Adobe Analytics, CJA, Adobe Target, and AB Tasty context
- H2: What the sprint delivers
- H2: Risks I check before recommending action
- H2: FAQ

### New Service Page: `/consulting/applied-ai-workflows/`

Title:
```html
<title>AI Workflow Consultant | Custom GPT, Claude & Streamlit</title>
<meta name="description" content="Practical AI workflow consulting for Custom GPTs, Claude, Streamlit apps, MCP-style tools, n8n automation, and reporting assistants.">
```

H1: `AI workflow consulting for useful reporting, research, and decision support.`

Recommended structure:
- H2: Where AI actually helps
- H2: Workflow examples
- H2: What I build
- H2: Evaluation and responsible-use notes
- H2: FAQ

## 4. AEO / GEO Layer

### Quotable Answer Blocks

Homepage:
> Anthony Baptiste is a Chicago-area analytics consultant and BI developer who helps startups, ecommerce teams, nonprofits, research groups, and operations teams turn messy data into trusted dashboards, KPI reporting, A/B test readouts, and practical AI workflow systems. His work combines Tableau, Power BI, SQL, Python, Adobe Analytics, Adobe Target, Salesforce reporting, Streamlit, and Custom GPT-style workflows.

Consulting:
> Anthony Baptiste offers analytics consulting for teams that need cleaner metrics, better dashboards, clearer experiment readouts, and practical AI workflow tools. Engagements include analytics audits, dashboard and reporting sprints, digital analytics and experimentation sprints, and applied AI workflow builds.

Dashboard service:
> A dashboard and reporting sprint turns scattered spreadsheets, CRM exports, database tables, or analytics exports into a reporting system your team can use. The deliverable can include cleaned data, Tableau or Power BI dashboards, KPI definitions, QA checks, and handoff notes.

Experimentation service:
> A digital analytics and experimentation sprint helps teams understand whether funnels, campaigns, A/B tests, Adobe Target tests, or personalization ideas produced a trustworthy signal. The work checks setup quality, audience logic, KPI movement, segmentation, and next-step recommendations.

AI workflow service:
> An applied AI workflow sprint builds a practical workflow around a real task: summarizing research, comparing transcripts, assisting reporting, generating structured drafts, or connecting tools through Custom GPT, Claude, Streamlit, n8n, or MCP-style patterns.

### Service FAQs

Analytics Audit:
- What does an analytics audit include? An analytics audit reviews your current dashboards, spreadsheets, KPI definitions, data sources, and reporting workflow. The goal is to find where numbers are duplicated, unclear, manually maintained, or hard to trust.
- When should we do an audit before building a dashboard? Do the audit first when stakeholders disagree on definitions, reports take too long to create, or no one knows which data source is correct. It prevents a dashboard build from copying the same confusion into a nicer interface.
- What do we get at the end? You get a prioritized roadmap, a plain-language summary of reporting issues, and recommendations for what to fix first. If a build makes sense, the audit defines the scope.
- How much does it cost? Analytics Clarity Audits start at $750. Final scope depends on the number of systems, dashboards, stakeholders, and data quality issues.

Dashboard & Reporting:
- What dashboard tools do you work with? I work with Tableau, Power BI, Excel, SQL, Python, Pandas, PostgreSQL, dbt, Salesforce reporting, and Looker Studio depending on the team’s current stack.
- What makes a dashboard useful? A useful dashboard has clear metric definitions, a known audience, clean source data, QA checks, and a decision it supports. It should reduce manual reporting, not become another place to debate numbers.
- Can you clean the data before building? Yes. A reporting sprint can include data cleanup, SQL modeling, Python/Pandas transformations, and dashboard-ready tables before the visual layer is built.
- What does a sprint cost? Dashboard and Reporting Sprints typically range from $3,500-$10,000 depending on data sources, dashboard complexity, cleanup work, and handoff needs.

Digital Analytics & Experimentation:
- Can you analyze Adobe Target or A/B test results? Yes. I can review Adobe Target, AB Tasty, Adobe Analytics, Customer Journey Analytics, A/B tests, and multivariate tests for setup quality, traffic splits, audience logic, KPI movement, and business implications.
- What makes an A/B test readout trustworthy? A trustworthy readout checks whether the test was set up cleanly, whether the right KPI was used, whether segments behaved differently, and whether the result is strong enough to act on.
- Do you help with funnel diagnostics? Yes. I can review conversion paths, customer journey behavior, campaign or experiment movement, and segment-level performance to find where the signal changes.
- What does this sprint cost? Digital Analytics and Experimentation Sprints typically range from $1,500-$6,000 depending on the test, data sources, and reporting depth.

Applied AI Workflow:
- What is an applied AI workflow? It is a practical tool or process that uses AI to support a real business task, such as summarizing research, drafting reporting notes, comparing transcripts, routing data, or helping analysts work faster.
- What tools do you use? Depending on the project, I can work with Claude, Custom GPTs, MCP-style tool connections, n8n, Streamlit, Python, and structured prompts.
- How do you keep AI work useful? I start with the task, the user, the data, and the decision. Then I add evaluation notes, limitations, and human review points so the workflow does not become blind automation.
- What does it cost? Applied AI Workflow Sprints are scoped by project because effort depends on data access, workflow complexity, tool choice, and review requirements.

### FAQPage JSON-LD

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "@id": "https://anthony-baptiste.com/consulting/#service-faq",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What does an analytics audit include?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "An analytics audit reviews current dashboards, spreadsheets, KPI definitions, data sources, and reporting workflow. The goal is to find where numbers are duplicated, unclear, manually maintained, or hard to trust."
      }
    },
    {
      "@type": "Question",
      "name": "What dashboard tools does Anthony Baptiste work with?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Anthony Baptiste works with Tableau, Power BI, Excel, SQL, Python, Pandas, PostgreSQL, dbt, Salesforce reporting, and Looker Studio depending on the team's current stack."
      }
    },
    {
      "@type": "Question",
      "name": "Can Anthony Baptiste analyze Adobe Target or A/B test results?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. Anthony Baptiste can review Adobe Target, AB Tasty, Adobe Analytics, Customer Journey Analytics, A/B tests, and multivariate tests for setup quality, traffic splits, audience logic, KPI movement, segmentation, and business implications."
      }
    },
    {
      "@type": "Question",
      "name": "What is an applied AI workflow?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "An applied AI workflow is a practical tool or process that uses AI to support a real business task, such as summarizing research, drafting reporting notes, comparing transcripts, routing data, or helping analysts work faster."
      }
    }
  ]
}
</script>
```

### Comparison / Decision Content Pieces

1. `Power BI vs Tableau for a small business dashboard`  
Outline: who each tool fits, cost and licensing, data prep needs, stakeholder sharing, maintenance, final recommendation by team size.

2. `When do you need a data warehouse instead of spreadsheets?`  
Outline: warning signs, spreadsheet limits, database/data warehouse basics, low-cost starting stack, what to do before buying tools.

3. `A/B test readout checklist: what to check before trusting the result`  
Outline: hypothesis, traffic split, sample quality, primary KPI, segment effects, novelty effects, recommendation format.

4. `Dashboard audit vs dashboard rebuild: which do you need?`  
Outline: symptoms, cost tradeoffs, decision tree, examples, recommended first step.

5. `Custom GPT vs Streamlit app for internal analytics workflows`  
Outline: use cases, data access, review requirements, repeatability, security considerations, maintenance.

### Machine-Readable Expertise

Use one entity everywhere:
- Name: `Anthony Baptiste`
- Role: `Analytics Consultant and BI Developer`
- Location/service area: `Chicago, Northern Illinois, United States, Remote`
- Status: `Northern Illinois University graduate`
- Services: `Analytics audits`, `Dashboard and reporting sprints`, `Digital analytics and experimentation sprints`, `Applied AI workflow sprints`

Add a consistent author bio at the bottom of resources:
> Anthony Baptiste is a Chicago-area analytics consultant and BI developer who builds dashboards, KPI reporting systems, A/B test readouts, and applied AI workflow tools for startups, ecommerce teams, nonprofits, research groups, and operations teams. His experience includes analytics work connected to Ulta Beauty, Shipt, Innovation DuPage, HAVI, Northern Illinois University, and Mystery Street Recording in roles, internships, research, student consulting, competitions, and projects.

## 5. Structured Data Package

Paste one `@graph` on the homepage or split relevant pieces per page. Keep URLs updated when new service pages exist.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Person",
      "@id": "https://anthony-baptiste.com/#anthony-baptiste",
      "name": "Anthony Baptiste",
      "url": "https://anthony-baptiste.com/",
      "image": "https://anthony-baptiste.com/images/abimage.jpeg",
      "email": "mailto:bapanalytics00@gmail.com",
      "jobTitle": "Analytics Consultant and BI Developer",
      "sameAs": [
        "https://www.linkedin.com/in/anthony-baptiste00/",
        "https://github.com/AntBap23",
        "https://calendly.com/anthonybaptiste00"
      ],
      "alumniOf": {
        "@type": "CollegeOrUniversity",
        "name": "Northern Illinois University"
      },
      "description": "Anthony Baptiste is a Northern Illinois University graduate, analytics consultant, and BI developer who helps teams turn messy data into dashboards, KPI reporting, A/B test readouts, and practical AI workflow systems.",
      "knowsAbout": [
        "Business intelligence consulting",
        "Tableau dashboards",
        "Power BI dashboards",
        "KPI reporting",
        "SQL",
        "Python",
        "Pandas",
        "dbt",
        "PostgreSQL",
        "Salesforce reporting",
        "Adobe Analytics",
        "Adobe Customer Journey Analytics",
        "Adobe Target",
        "A/B testing analysis",
        "Applied AI workflows",
        "Custom GPTs",
        "Streamlit"
      ]
    },
    {
      "@type": "ProfessionalService",
      "@id": "https://anthony-baptiste.com/#analytics-consulting",
      "name": "Anthony Baptiste Analytics Consulting",
      "url": "https://anthony-baptiste.com/",
      "description": "Analytics consulting for teams that need trusted dashboards, KPI reporting, data cleanup, A/B test readouts, and practical AI workflow systems.",
      "founder": {
        "@id": "https://anthony-baptiste.com/#anthony-baptiste"
      },
      "areaServed": [
        { "@type": "City", "name": "Chicago" },
        { "@type": "AdministrativeArea", "name": "Northern Illinois" },
        { "@type": "Country", "name": "United States" },
        "Remote"
      ],
      "email": "bapanalytics00@gmail.com",
      "priceRange": "$750-$10000+",
      "sameAs": [
        "https://www.linkedin.com/in/anthony-baptiste00/",
        "https://github.com/AntBap23"
      ],
      "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "Analytics Consulting Services",
        "itemListElement": [
          { "@id": "https://anthony-baptiste.com/consulting/#analytics-clarity-audit-offer" },
          { "@id": "https://anthony-baptiste.com/consulting/#dashboard-reporting-sprint-offer" },
          { "@id": "https://anthony-baptiste.com/consulting/#digital-analytics-experimentation-sprint-offer" },
          { "@id": "https://anthony-baptiste.com/consulting/#applied-ai-workflow-sprint-offer" }
        ]
      },
      "potentialAction": {
        "@type": "ReserveAction",
        "target": "https://calendly.com/anthonybaptiste00",
        "name": "Book a discovery call"
      }
    },
    {
      "@type": "Service",
      "@id": "https://anthony-baptiste.com/consulting/#analytics-clarity-audit",
      "name": "Analytics Clarity Audit",
      "serviceType": "Analytics audit",
      "provider": { "@id": "https://anthony-baptiste.com/#analytics-consulting" },
      "areaServed": ["Chicago", "Northern Illinois", "United States", "Remote"],
      "description": "KPI review, dashboard audit, data quality review, reporting workflow assessment, and prioritized analytics roadmap for teams with messy or unclear reporting.",
      "offers": {
        "@type": "Offer",
        "@id": "https://anthony-baptiste.com/consulting/#analytics-clarity-audit-offer",
        "priceCurrency": "USD",
        "price": "750",
        "priceSpecification": {
          "@type": "PriceSpecification",
          "priceCurrency": "USD",
          "minPrice": 750
        }
      }
    },
    {
      "@type": "Service",
      "@id": "https://anthony-baptiste.com/consulting/#dashboard-reporting-sprint",
      "name": "Dashboard and Reporting Sprint",
      "serviceType": "Business intelligence consulting",
      "provider": { "@id": "https://anthony-baptiste.com/#analytics-consulting" },
      "description": "Tableau, Power BI, SQL, Excel, Salesforce reporting, or Looker Studio reporting systems with cleaned data, KPI definitions, QA checks, and handoff notes.",
      "offers": {
        "@type": "Offer",
        "@id": "https://anthony-baptiste.com/consulting/#dashboard-reporting-sprint-offer",
        "priceCurrency": "USD",
        "priceSpecification": {
          "@type": "PriceSpecification",
          "priceCurrency": "USD",
          "minPrice": 3500,
          "maxPrice": 10000
        }
      }
    },
    {
      "@type": "Service",
      "@id": "https://anthony-baptiste.com/consulting/#digital-analytics-experimentation-sprint",
      "name": "Digital Analytics and Experimentation Sprint",
      "serviceType": "Digital analytics consulting",
      "provider": { "@id": "https://anthony-baptiste.com/#analytics-consulting" },
      "description": "Adobe Analytics, Customer Journey Analytics, Adobe Target, AB Tasty, A/B test analysis, funnel diagnostics, conversion KPI reporting, segmentation, and post-test recommendations.",
      "offers": {
        "@type": "Offer",
        "@id": "https://anthony-baptiste.com/consulting/#digital-analytics-experimentation-sprint-offer",
        "priceCurrency": "USD",
        "priceSpecification": {
          "@type": "PriceSpecification",
          "priceCurrency": "USD",
          "minPrice": 1500,
          "maxPrice": 6000
        }
      }
    },
    {
      "@type": "Service",
      "@id": "https://anthony-baptiste.com/consulting/#applied-ai-workflow-sprint",
      "name": "Applied AI Workflow Sprint",
      "serviceType": "Applied AI workflow consulting",
      "provider": { "@id": "https://anthony-baptiste.com/#analytics-consulting" },
      "description": "Custom GPT, Claude, MCP-style tool connections, n8n, Streamlit, transcript analysis, summarization, reporting assistant, and decision-support workflow design.",
      "offers": {
        "@type": "Offer",
        "@id": "https://anthony-baptiste.com/consulting/#applied-ai-workflow-sprint-offer",
        "priceCurrency": "USD",
        "price": "[NEEDS INPUT: starting price or keep scoped-by-project visible on page]"
      }
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://anthony-baptiste.com/consulting/#breadcrumb",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://anthony-baptiste.com/"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Consulting",
          "item": "https://anthony-baptiste.com/consulting/"
        }
      ]
    }
  ]
}
</script>
```

## 6. Lead Conversion Optimization

### Hero Rewrite

Primary CTA: `Book a 20-minute analytics fit call`  
Secondary CTA: `See consulting offers`

Hero:
> Messy reporting, unclear KPIs, and test results your team does not fully trust?
>
> I build analytics systems that turn scattered business, customer, and operations data into dashboards, KPI reporting, A/B test readouts, and practical AI workflows.
>
> Best fit: startups, ecommerce teams, nonprofits, research groups, and operations teams in Chicago, Northern Illinois, and remote markets.

Above-the-fold structure:
1. One-line problem: `Messy reporting, unclear KPIs, or tests you need to explain?`
2. H1 with service and outcome.
3. 2-sentence answer block.
4. CTAs: Calendly and consulting offers.
5. Proof strip: `30,000+ ZIP codes analyzed`, `10+ hrs saved weekly`, `20+ KPIs standardized`, `40% faster reporting`.
6. Small disclaimer link: `Proof includes roles, internships, student consulting, competitions, and projects; not endorsements.`

Proof section design:
- Card format: `Context`, `Problem`, `What I built`, `Result`, `Client relevance`.
- Use only known proof:
  - Shipt: 30,000+ ZIP codes, 10+ hrs saved weekly, 5+ planning teams.
  - Innovation DuPage: 40% faster reporting, 20+ KPIs.
  - Ulta Beauty: digital experimentation, A/B and multivariate analysis context. `[NEEDS INPUT: any public result metric you are allowed to share]`
  - HAVI: forecasting challenge and 1st place if already true on site.
  - NIU research: AI interview simulation and NLP workflows.

Lead magnets:
- KPI / Dashboard Readiness Checklist: place on `/consulting/`, `/consulting/dashboard-reporting/`, and after the homepage services grid.
- A/B Test Readout Checklist: place on `/consulting/digital-analytics-experimentation/`.
- Messy Data Intake Template: place on `/consulting/analytics-audit/`.
- AI Workflow Use Case Scorecard: place on `/consulting/applied-ai-workflows/`.

Booking/contact flow:
- Calendly CTA text: `Book a 20-minute analytics fit call`.
- Email CTA text: `Email the data problem`.
- Ask for only 4 fields if you add a form: name, email, organization, problem summary.
- Response promise: `I usually reply within 1-2 business days.`
- Confirmation copy: `Send the decision you are trying to support, the data you have, and what your team is doing manually now.`

Trust signals:
- Tools row: Tableau, Power BI, SQL, Python, Pandas, PostgreSQL, dbt, Salesforce, Adobe Analytics, Adobe Target, Streamlit, Custom GPTs.
- Process row: Discover -> Clean -> Build -> Handoff.
- First engagement: Start with a paid Analytics Clarity Audit when scope is unclear.

## 7. Off-Page & Authority

1. Create or clean Google Business Profile only if you have a real service-area setup and can keep contact details consistent.
2. Add Bing Places if using Google Business Profile.
3. Keep NAP consistent: Anthony Baptiste Analytics Consulting, email, website, service area. Use phone/address only if you want them public.
4. LinkedIn: post one teardown per week from the comparison topics above.
5. GitHub: pin analytics repos and add README links back to relevant case study pages.
6. NIU alumni networks and student organization contacts: share the consulting page and AI research page where appropriate.
7. Chicago startup communities: 1871, Built In Chicago, local founder Slack groups, nonprofit tech communities.
8. Guest content targets: local startup blogs, nonprofit operations newsletters, ecommerce analytics newsletters, university entrepreneurship centers.
9. Directory/citation targets: Clutch, UpCity, DesignRush, LinkedIn Services, Contra, Wellfound, and local chamber/service directories if they fit.
10. Podcast/webinar angle: “How small teams can stop making decisions from broken dashboards.”
11. Add partner/referral language for agencies that build sites but need analytics/reporting help.
12. Ask allowed project contacts for LinkedIn recommendations only when appropriate; do not imply company endorsement.

## 8. Technical SEO Checklist

| Item | How to check | Good looks like |
|---|---|---|
| Sitemap | Visit `/sitemap.xml`; submit in Google Search Console. | All indexable pages included with current `lastmod`. |
| Robots | Visit `/robots.txt`. | `Allow: /` and sitemap URL present; no accidental blocks. |
| Canonicals | View page source. | Each page points to its final HTTPS URL with trailing slash. |
| JSON-LD | Use Schema.org Validator and Rich Results Test. | Valid JSON; no factual mismatches; FAQ only where visible on page. |
| Titles | Crawl with Screaming Frog or browser source. | Unique, under ~60 chars, query-aligned. |
| Meta descriptions | Crawl or inspect source. | Unique, under ~155 chars, plain value proposition. |
| Mobile | Use Chrome DevTools and PageSpeed Insights. | No horizontal scroll, readable tap targets, CTA visible. |
| Core Web Vitals | PageSpeed Insights / Search Console. | LCP under 2.5s, INP under 200ms, CLS under 0.1. |
| Images | Inspect rendered page and file sizes. | Correct dimensions, lazy loading below fold, descriptive alt. |
| HTTPS | Browser lock and Search Console. | All pages resolve HTTPS; no mixed content. |
| Indexing | Search Console URL Inspection. | Indexed canonical selected by Google. |
| Analytics | GA4 Realtime and DebugView. | Calendly, email, PDF, and outbound GitHub clicks tracked. |
| 404s | Crawl site. | No broken internal links; external GitHub/Drive links still work. |

## 9. 30-Day Rollout Plan

### Week 1: Fix entity clarity and high-impact copy

- Keep NIU graduate/alumni wording consistent across homepage, schema, experience, resume, `llms.txt`, and social bios.
- Update homepage title/meta/H1/hero CTA.
- Validate existing JSON-LD.
- Add GA4 click tracking for Calendly, email, PDF, and outbound links.

Measure:
- Search Console indexing status.
- CTR for homepage and consulting page.
- Calendly/email click events.

### Week 2: Build bottom-funnel service pages

- Publish `/consulting/dashboard-reporting/`.
- Publish `/consulting/digital-analytics-experimentation/`.
- Add service-specific FAQ and Service schema.
- Add internal links from homepage, consulting, projects, and footer.

Measure:
- Impressions for dashboard, Power BI, Tableau, A/B test, Adobe Analytics queries.
- Engagement rate on service pages.
- CTA clicks by service page.

### Week 3: Build trust and AEO assets

- Publish `/consulting/analytics-audit/` and `/consulting/applied-ai-workflows/`.
- Add FAQ blocks and answer summaries to each service page.
- Rewrite project cards into `Context / Problem / Build / Result / Relevance` format.
- Add one comparison article: `Dashboard audit vs dashboard rebuild`.

Measure:
- New indexed pages.
- Long-tail impressions.
- Scroll depth and CTA clicks on proof pages.

### Week 4: Authority and conversion tightening

- Create LinkedIn posts from each comparison article.
- Update GitHub READMEs with links back to relevant case studies.
- Add or improve lead magnets: KPI checklist, A/B test checklist, messy data intake template.
- Submit updated sitemap in Search Console.

Measure:
- 3-4 primary KPIs:
  - Qualified inquiry clicks: Calendly + email.
  - Search Console impressions for service-intent queries.
  - Organic CTR on homepage and consulting pages.
  - Service page engagement: scroll depth, time, CTA clicks.

Best first move: fix the NIU status/entity inconsistency, then publish the dashboard/reporting and experimentation service pages. Those two pages are the clearest path to qualified bottom-funnel traffic.
