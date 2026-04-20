"""
knowledge.py — Hardcoded Mutual Fund FAQ knowledge base for Groww chatbot.
Covers: expense ratio, exit load, SIP, ELSS, riskometer, benchmark,
        CAS statement, direct vs regular, NAV, KYC.
"""

FAQ_DATA = [
    # ── Expense Ratio ─────────────────────────────────────────────
    {
        "question": "What is expense ratio in mutual funds?",
        "answer": (
            "The expense ratio is the annual fee a mutual fund charges to manage your investment. "
            "It is expressed as a percentage of your average daily net assets. For example, an "
            "expense ratio of 1% means ₹1 is charged per ₹100 invested per year. SEBI caps expense "
            "ratios — equity funds can charge up to 2.25% for the first ₹500 crore of AUM, "
            "declining in slabs after that. The fee covers fund management, administration, "
            "marketing, and distribution. It is deducted daily from the NAV, so you never pay it "
            "separately — it is already reflected in the NAV you see."
        ),
        "source": "https://www.amfiindia.com/investor-corner/knowledge-center/expense-ratio.html",
    },
    {
        "question": "How does expense ratio affect mutual fund returns?",
        "answer": (
            "Expense ratio directly reduces your net returns. If a fund earns 12% but has an "
            "expense ratio of 1.5%, your effective return is approximately 10.5%. Over long periods "
            "this compounding effect is significant — on a ₹1 lakh investment over 20 years at 12%, "
            "a 1% higher expense ratio can cost you more than ₹2 lakh in final corpus. Direct plans "
            "have lower expense ratios than regular plans because there is no distributor commission, "
            "making them more cost-efficient for long-term investors."
        ),
        "source": "https://www.amfiindia.com/investor-corner/knowledge-center/expense-ratio.html",
    },
    {
        "question": "What is a good expense ratio for a mutual fund?",
        "answer": (
            "For equity mutual funds, an expense ratio below 1% (direct plan) is considered good. "
            "Index funds typically have expense ratios of 0.05%–0.20%, while actively managed equity "
            "funds range from 0.5%–1.5% for direct plans. Debt funds generally have lower expense "
            "ratios of 0.1%–0.5%. SEBI has set maximum limits: equity funds can charge up to 2.25% "
            "and debt funds up to 2%. Always compare the expense ratio of a fund within its own "
            "category, not across different types."
        ),
        "source": "https://www.sebi.gov.in/legal/circulars/sep-2018/total-expense-ratio-ter-of-mutual-funds_40386.html",
    },

    # ── Exit Load ─────────────────────────────────────────────────
    {
        "question": "What is exit load in mutual funds?",
        "answer": (
            "Exit load is a fee charged when you redeem your mutual fund units before a specified "
            "holding period. It is designed to discourage early redemptions and protect long-term "
            "investors. For example, many equity funds charge a 1% exit load if you redeem within "
            "1 year of investment. If you invest ₹1 lakh and the NAV has grown to ₹1.1 lakh at "
            "redemption within 1 year, you pay 1% of ₹1.1 lakh = ₹1,100 as exit load. The exit "
            "load is deducted from the redemption proceeds, not from NAV."
        ),
        "source": "https://www.amfiindia.com/investor-corner/knowledge-center/exit-load.html",
    },
    {
        "question": "How is exit load calculated on mutual funds?",
        "answer": (
            "Exit load is calculated on the redemption amount (number of units × applicable NAV) "
            "at the time of redemption. The formula is: Exit Load Amount = Redemption Value × Exit "
            "Load Percentage. For example, if you redeem 1,000 units at NAV of ₹50 (redemption "
            "value = ₹50,000) and the exit load is 1%, you pay ₹500 as exit load, receiving "
            "₹49,500 net. SEBI requires funds to disclose exit load clearly in the Scheme "
            "Information Document (SID). Many liquid and ultra-short-duration funds have zero exit "
            "load, while most equity funds charge 1% for redemptions within 1 year."
        ),
        "source": "https://www.amfiindia.com/investor-corner/knowledge-center/exit-load.html",
    },

    # ── SIP ───────────────────────────────────────────────────────
    {
        "question": "What is the minimum SIP amount in mutual funds?",
        "answer": (
            "The minimum SIP (Systematic Investment Plan) amount varies by fund house and scheme. "
            "Most equity mutual funds allow SIPs starting from ₹100 or ₹500 per month. On Groww, "
            "you can start a SIP with as little as ₹100/month for many funds. Some fund houses "
            "like HDFC, SBI, and Axis allow ₹100 minimum SIPs. ELSS funds typically start at "
            "₹500/month. The minimum SIP amount is specified in the Scheme Information Document "
            "(SID) and can differ between weekly, monthly, and quarterly SIP frequencies."
        ),
        "source": "https://groww.in/mutual-funds/sip-calculator",
    },
    {
        "question": "How does SIP work in mutual funds?",
        "answer": (
            "A Systematic Investment Plan (SIP) lets you invest a fixed amount in a mutual fund "
            "at regular intervals — daily, weekly, monthly, or quarterly. On the SIP date, the "
            "amount is auto-debited from your bank account and units are allocated at that day's "
            "NAV. SIPs leverage rupee cost averaging: when NAV is high you get fewer units, when "
            "NAV is low you get more units, reducing the average cost over time. SIPs also enforce "
            "investment discipline and benefit from compounding. You can start, pause, increase "
            "(Step-up SIP), or stop a SIP at any time on Groww."
        ),
        "source": "https://groww.in/mutual-funds/sip",
    },
    {
        "question": "Can I change or stop my SIP anytime on Groww?",
        "answer": (
            "Yes, you can pause, modify, or cancel your SIP anytime on Groww without any penalty. "
            "To stop a SIP: go to Portfolio → SIPs → select the SIP → click 'Cancel SIP'. The "
            "cancellation must be done at least 7–10 business days before the next SIP date for "
            "it to take effect for that installment. Your existing units remain invested until you "
            "choose to redeem them. Stopping a SIP does not mean redemption; your accumulated "
            "corpus continues to stay invested in the fund."
        ),
        "source": "https://groww.in/help/mutual-funds/sip",
    },

    # ── ELSS & Lock-in ────────────────────────────────────────────
    {
        "question": "What is the lock-in period for ELSS mutual funds?",
        "answer": (
            "ELSS (Equity Linked Savings Scheme) funds have a mandatory lock-in period of 3 years "
            "from the date of each investment. This is the shortest lock-in among all tax-saving "
            "instruments under Section 80C. For SIP investments in ELSS, each installment has its "
            "own 3-year lock-in from the date of that specific installment. For example, a SIP "
            "installment made in January 2022 can be redeemed from January 2025, while a March "
            "2022 installment can only be redeemed from March 2025. You cannot redeem any units "
            "before completing 3 years."
        ),
        "source": "https://www.incometaxindia.gov.in/pages/tools/80c-deduction.aspx",
    },
    {
        "question": "How much tax can I save with ELSS mutual funds?",
        "answer": (
            "ELSS investments qualify for tax deduction under Section 80C of the Income Tax Act, "
            "1961. You can claim a deduction of up to ₹1.5 lakh per financial year. At the "
            "highest tax bracket of 30%, this saves up to ₹46,800 in taxes (including 4% cess). "
            "After the 3-year lock-in, gains above ₹1 lakh per year are taxed at 10% as Long-Term "
            "Capital Gains (LTCG). ELSS combines tax savings with equity market exposure, making "
            "it attractive compared to PPF or NSC which offer fixed but lower returns. Note: "
            "these benefits apply under the old tax regime."
        ),
        "source": "https://www.incometaxindia.gov.in/pages/tools/80c-deduction.aspx",
    },

    # ── Riskometer ───────────────────────────────────────────────
    {
        "question": "What are the riskometer levels in mutual funds?",
        "answer": (
            "SEBI's riskometer classifies mutual fund risk into six levels: (1) Low — principal "
            "at very low risk, e.g., overnight and liquid funds; (2) Low to Moderate — low interest "
            "rate and credit risk; (3) Moderate — moderate risk, e.g., balanced advantage funds; "
            "(4) Moderately High — equity exposure, e.g., large-cap funds; (5) High — significant "
            "equity volatility, e.g., mid-cap and small-cap funds; (6) Very High — very high risk, "
            "e.g., sectoral, thematic, and small-cap funds. Every fund's riskometer must be "
            "displayed on all scheme documents and monthly factsheets. The riskometer must be "
            "reviewed monthly by fund houses."
        ),
        "source": "https://www.sebi.gov.in/legal/circulars/oct-2020/product-labeling-in-mutual-funds_48012.html",
    },
    {
        "question": "What does the riskometer in mutual funds mean for investors?",
        "answer": (
            "The riskometer helps investors understand the risk level of a mutual fund before "
            "investing. It is a dial-like graphic with six levels from Low to Very High. Investors "
            "should match the fund's riskometer with their own risk appetite: conservative investors "
            "should stick to Low/Low to Moderate funds; moderate risk-takers can consider Moderate "
            "to Moderately High funds; aggressive investors can consider High or Very High funds. "
            "The riskometer accounts for credit risk, interest rate risk, liquidity risk, and "
            "market (equity) risk. It is updated monthly and must be displayed on all fund "
            "communications as per SEBI regulations."
        ),
        "source": "https://www.sebi.gov.in/legal/circulars/oct-2020/product-labeling-in-mutual-funds_48012.html",
    },

    # ── Benchmark Index ───────────────────────────────────────────
    {
        "question": "What is a benchmark index in mutual funds?",
        "answer": (
            "A benchmark index is a standard against which a mutual fund's performance is measured. "
            "For example, a large-cap equity fund may use Nifty 50 or BSE Sensex as its benchmark, "
            "while a mid-cap fund may use Nifty Midcap 150. The benchmark helps investors evaluate "
            "whether the fund manager is generating 'alpha' (returns above the benchmark) or "
            "underperforming it. SEBI mandates every scheme to declare a Tier-1 and Tier-2 "
            "benchmark. If a fund consistently underperforms its benchmark after costs, investors "
            "may be better served by a passive index fund that tracks the same benchmark at a "
            "much lower expense ratio."
        ),
        "source": "https://www.sebi.gov.in/legal/circulars/sep-2021/benchmarks-for-mutual-fund-schemes_52614.html",
    },
    {
        "question": "What benchmark does a large-cap mutual fund use?",
        "answer": (
            "SEBI mandates that large-cap mutual funds use either Nifty 100 TRI (Total Return "
            "Index) or BSE 100 TRI as their Tier-1 benchmark. The Nifty 100 TRI includes the top "
            "100 companies by market capitalisation on NSE, including dividends. TRI benchmarks "
            "are preferred over Price Return Index (PRI) because they reflect actual returns "
            "including dividends — making fund comparison more accurate. Other common benchmarks: "
            "mid-cap funds use Nifty Midcap 150 TRI; small-cap funds use Nifty Smallcap 250 TRI; "
            "flexi-cap funds use Nifty 500 TRI; ELSS funds use Nifty 500 TRI."
        ),
        "source": "https://www.sebi.gov.in/legal/circulars/sep-2021/benchmarks-for-mutual-fund-schemes_52614.html",
    },

    # ── CAS Statement ─────────────────────────────────────────────
    {
        "question": "How to download CAS statement for mutual funds?",
        "answer": (
            "You can download your Consolidated Account Statement (CAS) in two ways: "
            "(1) CAMS website (www.camsonline.com): Go to Investor Services → Consolidated Account "
            "Statement → enter your registered email and PAN → choose period → download PDF. "
            "(2) NSDL website (www.nsdl.co.in or www.nsdlcas.nsdl.com): Go to CAS → enter PAN, "
            "email, date range → download. The CAS consolidates all mutual fund holdings across "
            "all fund houses, linked to your PAN. It shows current holdings, transaction history, "
            "NAV, and current value. You can also get CAS on Groww by going to Reports → "
            "Account Statement."
        ),
        "source": "https://www.camsonline.com/Investors/Statements/Consolidated-Account-Statement",
    },
    {
        "question": "What is a CAS statement and what does it contain?",
        "answer": (
            "A Consolidated Account Statement (CAS) is a single document that shows all your "
            "mutual fund holdings across all fund houses, consolidated by PAN. It is generated "
            "by CAMS or KFintech (formerly Karvy) — the two registrar and transfer agents (RTAs) "
            "in India. A CAS contains: fund name and scheme, folio number, current units held, "
            "average cost NAV, current NAV, current value, unrealised gain/loss, and all "
            "transactions (purchases, redemptions, switches, dividends) for the chosen period. "
            "It is the official document for tracking your complete mutual fund portfolio and is "
            "accepted as proof of investment by tax authorities."
        ),
        "source": "https://www.camsonline.com/Investors/Statements/Consolidated-Account-Statement",
    },

    # ── Direct vs Regular Plans ───────────────────────────────────
    {
        "question": "What is the difference between direct and regular mutual fund plans?",
        "answer": (
            "A mutual fund scheme comes in two variants: Direct and Regular. In a Direct Plan, "
            "you invest directly with the fund house (via their website, Groww, or other direct "
            "platforms) — there is no intermediary, so there is no distributor commission. This "
            "results in a lower expense ratio (typically 0.5%–1% lower than regular). In a "
            "Regular Plan, you invest through a distributor or broker — the fund house pays them "
            "a commission from the expense ratio, making it costlier. The same underlying "
            "portfolio and fund manager manages both plans; only the expense ratio differs. "
            "Over long periods, this difference compounds significantly."
        ),
        "source": "https://groww.in/blog/direct-vs-regular-mutual-fund",
    },
    {
        "question": "Should I choose direct or regular mutual fund plan?",
        "answer": (
            "Choose a Direct Plan if you are a self-directed investor comfortable doing your own "
            "research — you save on distributor commissions and get better long-term returns. "
            "On ₹10 lakh invested for 20 years at 12% return, a 0.75% lower expense ratio in a "
            "direct plan can mean ₹5–7 lakh extra corpus at maturity. Choose a Regular Plan if "
            "you need ongoing financial advice and hand-holding from a certified financial planner "
            "(CFP) or distributor — the commission is the cost of their service. Platforms like "
            "Groww offer Direct Plans, making it easy for self-directed investors to access all "
            "funds at lower costs."
        ),
        "source": "https://groww.in/blog/direct-vs-regular-mutual-fund",
    },

    # ── NAV ───────────────────────────────────────────────────────
    {
        "question": "What is NAV in mutual funds and how is it calculated?",
        "answer": (
            "NAV (Net Asset Value) is the per-unit price of a mutual fund scheme. It represents "
            "the market value of the fund's total assets minus liabilities, divided by the total "
            "number of units outstanding. Formula: NAV = (Total Assets − Total Liabilities) ÷ "
            "Total Units Outstanding. For example, if a fund holds stocks worth ₹100 crore, has "
            "liabilities of ₹2 crore, and has 5 crore units outstanding, NAV = (100 − 2) ÷ 5 = "
            "₹19.6 per unit. SEBI mandates that NAV be declared for all schemes by 11 PM on all "
            "business days. Equity fund NAV is published after market close (3:30 PM)."
        ),
        "source": "https://www.amfiindia.com/investor-corner/knowledge-center/nav.html",
    },
    {
        "question": "Does a lower NAV mean a cheaper mutual fund?",
        "answer": (
            "No. A lower NAV does not mean the fund is cheaper or a better buy. NAV is simply "
            "the current price per unit based on the fund's underlying portfolio. A fund with "
            "NAV of ₹10 and one with NAV of ₹100 can have identical portfolios if they started "
            "at different times. What matters is the fund's performance (returns vs benchmark), "
            "expense ratio, fund manager track record, and portfolio quality — not the absolute "
            "NAV value. When you invest ₹10,000, you simply get more units at a lower NAV and "
            "fewer units at a higher NAV; your actual invested value is the same."
        ),
        "source": "https://www.amfiindia.com/investor-corner/knowledge-center/nav.html",
    },
    {
        "question": "When is NAV applied for mutual fund purchases on Groww?",
        "answer": (
            "For equity and hybrid mutual funds: if you submit a purchase order before 3:00 PM on "
            "a business day and your payment is cleared the same day, you get that day's closing "
            "NAV. Orders submitted after 3:00 PM get the next business day's NAV. For liquid and "
            "overnight funds: orders submitted before 1:30 PM with cleared payment get the same "
            "day's NAV. SEBI's cut-off time rule ensures uniform NAV treatment for all investors. "
            "On Groww, the app clearly shows the applicable NAV cut-off time for each transaction "
            "type before you confirm your investment."
        ),
        "source": "https://groww.in/help/mutual-funds/nav",
    },

    # ── KYC ───────────────────────────────────────────────────────
    {
        "question": "What are the KYC requirements for investing in mutual funds?",
        "answer": (
            "KYC (Know Your Customer) is mandatory for all mutual fund investments in India. "
            "You need: (1) PAN card — mandatory for investments above ₹50,000; (2) Aadhaar card "
            "for address proof and e-KYC; (3) A bank account linked to your name. For e-KYC on "
            "Groww: Aadhaar OTP-based verification allows investments up to ₹50,000/year per fund "
            "house. For full KYC: complete in-person verification (IPV) via video KYC to remove "
            "limits. KYC is done once and is valid across all SEBI-registered intermediaries. "
            "You can check your KYC status at www.cvlkra.com or www.camskra.com."
        ),
        "source": "https://www.amfiindia.com/investor-corner/knowledge-center/kyc.html",
    },
    {
        "question": "How to complete KYC for mutual funds on Groww?",
        "answer": (
            "On Groww, KYC is done digitally: (1) Enter your PAN, date of birth, and personal "
            "details; (2) Upload Aadhaar and PAN card images; (3) Complete in-app video KYC "
            "(take a short selfie video); (4) Sign the digital consent form. The entire process "
            "takes 5–10 minutes. If you are already KYC-compliant with SEBI (via any registered "
            "intermediary), Groww fetches your existing KYC status automatically — no "
            "re-verification needed. KYC is a one-time process valid for lifetime across all "
            "mutual fund investments in India."
        ),
        "source": "https://groww.in/help/kyc",
    },
    {
        "question": "Can I invest in mutual funds without PAN card?",
        "answer": (
            "For investments above ₹50,000, PAN is mandatory per SEBI regulations. For "
            "micro-SIPs up to ₹50,000 per year (total across all fund houses), you can invest "
            "without PAN by submitting other officially valid documents (OVDs) like Aadhaar, "
            "Voter ID, or Driving License. However, on Groww, PAN is required for account "
            "creation as it is used for KYC verification and tax reporting. NRIs also need PAN "
            "for mutual fund investments along with their foreign address proof and FEMA "
            "declarations."
        ),
        "source": "https://www.amfiindia.com/investor-corner/knowledge-center/kyc.html",
    },

    # ── General & How-To ──────────────────────────────────────────
    {
        "question": "What types of mutual funds are available in India?",
        "answer": (
            "SEBI classifies mutual funds into five broad categories: (1) Equity Funds — invest "
            "primarily in stocks (large-cap, mid-cap, small-cap, flexi-cap, sectoral, ELSS, etc.); "
            "(2) Debt Funds — invest in fixed-income securities like bonds and government "
            "securities (liquid, overnight, short-duration, gilt, credit risk funds); (3) Hybrid "
            "Funds — mix of equity and debt (balanced advantage, aggressive hybrid, arbitrage); "
            "(4) Solution-Oriented Funds — retirement and children's funds with lock-ins; "
            "(5) Other Funds — index funds, ETFs, fund of funds. Each category has specific SEBI "
            "guidelines on minimum equity/debt allocation."
        ),
        "source": "https://www.sebi.gov.in/legal/circulars/oct-2017/categorization-and-rationalization-of-mutual-fund-schemes_36199.html",
    },
    {
        "question": "How to redeem mutual funds on Groww?",
        "answer": (
            "To redeem mutual funds on Groww: (1) Go to Portfolio → Mutual Funds → select the "
            "fund; (2) Tap 'Withdraw'; (3) Choose amount or number of units to redeem; (4) "
            "Confirm the order. Redemption proceeds are credited to your linked bank account "
            "within 2–3 business days for equity funds (T+3 working days) and same/next business "
            "day for liquid funds (T+1). If you have multiple SIP installments in ELSS, only the "
            "units completing 3 years are available for redemption. Exit load (if applicable) and "
            "capital gains tax will apply."
        ),
        "source": "https://groww.in/help/mutual-funds/redemption",
    },
    {
        "question": "What is SWP (Systematic Withdrawal Plan) in mutual funds?",
        "answer": (
            "A Systematic Withdrawal Plan (SWP) allows you to withdraw a fixed amount from your "
            "mutual fund investment at regular intervals (monthly, quarterly). It is the opposite "
            "of SIP. SWP is useful for creating a regular income stream, especially in retirement. "
            "The withdrawn amount is redeemed at the applicable NAV on the withdrawal date. For "
            "example, if you have ₹50 lakh invested, you can set up a monthly SWP of ₹25,000 to "
            "get regular income. Capital gains tax applies on each withdrawal based on the holding "
            "period. SWP can be set up on Groww under Portfolio → select fund → SWP option."
        ),
        "source": "https://groww.in/blog/systematic-withdrawal-plan-swp",
    },
    {
        "question": "What is the difference between growth and dividend (IDCW) option in mutual funds?",
        "answer": (
            "In the Growth option, all profits remain invested and compound over time — no payouts "
            "are made. The NAV grows over time reflecting reinvested gains. In the IDCW (Income "
            "Distribution cum Capital Withdrawal) option (formerly called Dividend option), the "
            "fund periodically distributes a portion of profits or capital to investors. SEBI "
            "renamed 'Dividend' to 'IDCW' in 2021 to clarify that these payouts may include "
            "return of principal, not just income. For long-term wealth creation, Growth option "
            "is preferred as it benefits from compounding. IDCW suits investors who need regular "
            "income or cash flows."
        ),
        "source": "https://www.sebi.gov.in/legal/circulars/dec-2020/amendment-to-sebi-circular-on-categorization-and-rationalization-of-mutual-fund-schemes_48685.html",
    },
    {
        "question": "How are mutual fund gains taxed in India?",
        "answer": (
            "Mutual fund taxation depends on the fund type and holding period: For Equity Funds "
            "(≥65% equity): Short-Term Capital Gains (STCG) — holding < 1 year — taxed at 20% "
            "(revised from 15% in Budget 2024). Long-Term Capital Gains (LTCG) — holding ≥ 1 "
            "year — taxed at 12.5% (revised from 10%) on gains above ₹1.25 lakh/year. For Debt "
            "Funds: Gains are added to income and taxed at your income tax slab rate (applicable "
            "for debt fund investments made after April 1, 2023). For Hybrid Funds: taxation "
            "depends on equity allocation. ELSS gains after 3-year lock-in are taxed as LTCG "
            "(equity) at 12.5% above ₹1.25 lakh."
        ),
        "source": "https://incometaxindia.gov.in/pages/tools/capital-gains.aspx",
    },
    {
        "question": "What is a systematic transfer plan (STP) in mutual funds?",
        "answer": (
            "A Systematic Transfer Plan (STP) automatically transfers a fixed amount from one "
            "mutual fund scheme to another within the same fund house at regular intervals. It is "
            "commonly used to transfer from a debt/liquid fund to an equity fund — this way, "
            "you park a lump sum in a safer fund and gradually move it to equity via STP, reducing "
            "market timing risk (similar to SIP but using existing corpus). For example, invest "
            "₹6 lakh in a liquid fund and set up a monthly STP of ₹50,000 into an equity fund "
            "for 12 months. Each STP transfer is a redemption from the source fund, so capital "
            "gains tax and exit load (if any) may apply."
        ),
        "source": "https://groww.in/blog/systematic-transfer-plan-stp",
    },
    {
        "question": "What is the minimum lump sum investment in mutual funds?",
        "answer": (
            "The minimum lump sum investment in most equity mutual funds is ₹1,000 or ₹5,000 "
            "depending on the fund house and scheme. On Groww, many funds allow lump sum "
            "investments starting from ₹100. Index funds and ETFs often have minimum investments "
            "of ₹100–₹500 for lump sum. ELSS funds typically require a minimum of ₹500. Liquid "
            "and debt funds may have higher minimums of ₹1,000–₹5,000. There is no upper limit "
            "on lump sum investments. The minimum additional investment amount is usually ₹1,000 "
            "or ₹500 for most funds."
        ),
        "source": "https://groww.in/mutual-funds",
    },
    {
        "question": "How to switch mutual funds on Groww?",
        "answer": (
            "To switch between mutual fund schemes on Groww: (1) Go to Portfolio → select the "
            "fund you want to switch from; (2) Tap 'Switch'; (3) Select the destination fund "
            "(must be from the same fund house); (4) Enter the amount or number of units; (5) "
            "Confirm. Switching is treated as a redemption from the source fund and a fresh "
            "purchase in the destination fund — capital gains tax and exit load apply on the "
            "source fund. Switching between direct and regular plan of the same scheme, or between "
            "growth and IDCW options of the same scheme, is also possible and is called a "
            "'switch within a scheme'."
        ),
        "source": "https://groww.in/help/mutual-funds/switch",
    },
    {
        "question": "What is AUM in mutual funds?",
        "answer": (
            "AUM (Assets Under Management) is the total market value of all investments managed "
            "by a mutual fund scheme or AMC (Asset Management Company). For example, if an "
            "equity fund has 1 crore units outstanding and NAV is ₹50, AUM = ₹50 crore. Higher "
            "AUM generally indicates investor confidence but is not a performance indicator. For "
            "small-cap and mid-cap funds, very high AUM (>₹10,000 crore) can be a concern as "
            "deploying large capital in less liquid small-cap stocks becomes difficult. For large-"
            "cap and index funds, higher AUM is generally not a concern. AMFI publishes monthly "
            "AUM data for all schemes."
        ),
        "source": "https://www.amfiindia.com/",
    },
    {
        "question": "Are mutual funds safe? What are the risks?",
        "answer": (
            "Mutual funds are subject to market risk — the value of your investment can go up or "
            "down based on market movements. They are not guaranteed like bank fixed deposits. "
            "Key risks include: Market Risk (equity price fluctuations), Credit Risk (debt "
            "instruments may default), Interest Rate Risk (bond prices fall when rates rise), "
            "Liquidity Risk (difficulty selling assets), and Concentration Risk (sector/stock "
            "specific). However, they are regulated by SEBI and offer professional management "
            "and diversification. Historical data shows that equity mutual funds have delivered "
            "12%–15% annualised returns over 10+ year periods, though past performance does not "
            "guarantee future results."
        ),
        "source": "https://www.amfiindia.com/investor-corner/knowledge-center/risk.html",
    },
]
