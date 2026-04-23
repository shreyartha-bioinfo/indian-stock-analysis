"""
Static ticker lists for NSE and BSE indices.
Tickers follow yfinance convention: .NS suffix for NSE, .BO for BSE.
"""

NIFTY50 = [
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "sector": "IT"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "sector": "Banking"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel", "sector": "Telecom"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "sector": "Banking"},
    {"symbol": "INFOSYS.NS", "name": "Infosys", "sector": "IT"},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "sector": "Banking"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever", "sector": "FMCG"},
    {"symbol": "ITC.NS", "name": "ITC", "sector": "FMCG"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "sector": "Banking"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro", "sector": "Infrastructure"},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank", "sector": "Banking"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance", "sector": "Finance"},
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints", "sector": "Consumer"},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki", "sector": "Auto"},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies", "sector": "IT"},
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharmaceutical", "sector": "Pharma"},
    {"symbol": "TITAN.NS", "name": "Titan Company", "sector": "Consumer"},
    {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv", "sector": "Finance"},
    {"symbol": "NTPC.NS", "name": "NTPC", "sector": "Power"},
    {"symbol": "ONGC.NS", "name": "Oil & Natural Gas Corp", "sector": "Energy"},
    {"symbol": "POWERGRID.NS", "name": "Power Grid Corp", "sector": "Power"},
    {"symbol": "WIPRO.NS", "name": "Wipro", "sector": "IT"},
    {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement", "sector": "Cement"},
    {"symbol": "NESTLEIND.NS", "name": "Nestle India", "sector": "FMCG"},
    {"symbol": "JSWSTEEL.NS", "name": "JSW Steel", "sector": "Metals"},
    {"symbol": "TATAMOTORS.NS", "name": "Tata Motors", "sector": "Auto"},
    {"symbol": "ADANIENT.NS", "name": "Adani Enterprises", "sector": "Conglomerate"},
    {"symbol": "ADANIPORTS.NS", "name": "Adani Ports", "sector": "Logistics"},
    {"symbol": "COALINDIA.NS", "name": "Coal India", "sector": "Mining"},
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel", "sector": "Metals"},
    {"symbol": "HINDALCO.NS", "name": "Hindalco Industries", "sector": "Metals"},
    {"symbol": "BPCL.NS", "name": "BPCL", "sector": "Energy"},
    {"symbol": "DRREDDY.NS", "name": "Dr. Reddy's Laboratories", "sector": "Pharma"},
    {"symbol": "GRASIM.NS", "name": "Grasim Industries", "sector": "Cement"},
    {"symbol": "CIPLA.NS", "name": "Cipla", "sector": "Pharma"},
    {"symbol": "DIVISLAB.NS", "name": "Divi's Laboratories", "sector": "Pharma"},
    {"symbol": "TECHM.NS", "name": "Tech Mahindra", "sector": "IT"},
    {"symbol": "EICHERMOT.NS", "name": "Eicher Motors", "sector": "Auto"},
    {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals", "sector": "Healthcare"},
    {"symbol": "SHRIRAMFIN.NS", "name": "Shriram Finance", "sector": "Finance"},
    {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp", "sector": "Auto"},
    {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto", "sector": "Auto"},
    {"symbol": "BRITANNIA.NS", "name": "Britannia Industries", "sector": "FMCG"},
    {"symbol": "TATACONSUM.NS", "name": "Tata Consumer Products", "sector": "FMCG"},
    {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank", "sector": "Banking"},
    {"symbol": "M&M.NS", "name": "Mahindra & Mahindra", "sector": "Auto"},
    {"symbol": "SBILIFE.NS", "name": "SBI Life Insurance", "sector": "Insurance"},
    {"symbol": "HDFCLIFE.NS", "name": "HDFC Life Insurance", "sector": "Insurance"},
    {"symbol": "BEL.NS", "name": "Bharat Electronics", "sector": "Defence"},
]

SENSEX30 = [
    {"symbol": "RELIANCE.BO", "name": "Reliance Industries", "sector": "Energy"},
    {"symbol": "TCS.BO", "name": "Tata Consultancy Services", "sector": "IT"},
    {"symbol": "HDFCBANK.BO", "name": "HDFC Bank", "sector": "Banking"},
    {"symbol": "BHARTIARTL.BO", "name": "Bharti Airtel", "sector": "Telecom"},
    {"symbol": "ICICIBANK.BO", "name": "ICICI Bank", "sector": "Banking"},
    {"symbol": "INFOSYS.BO", "name": "Infosys", "sector": "IT"},
    {"symbol": "SBIN.BO", "name": "State Bank of India", "sector": "Banking"},
    {"symbol": "HINDUNILVR.BO", "name": "Hindustan Unilever", "sector": "FMCG"},
    {"symbol": "ITC.BO", "name": "ITC", "sector": "FMCG"},
    {"symbol": "KOTAKBANK.BO", "name": "Kotak Mahindra Bank", "sector": "Banking"},
    {"symbol": "LT.BO", "name": "Larsen & Toubro", "sector": "Infrastructure"},
    {"symbol": "AXISBANK.BO", "name": "Axis Bank", "sector": "Banking"},
    {"symbol": "BAJFINANCE.BO", "name": "Bajaj Finance", "sector": "Finance"},
    {"symbol": "ASIANPAINT.BO", "name": "Asian Paints", "sector": "Consumer"},
    {"symbol": "MARUTI.BO", "name": "Maruti Suzuki", "sector": "Auto"},
    {"symbol": "HCLTECH.BO", "name": "HCL Technologies", "sector": "IT"},
    {"symbol": "SUNPHARMA.BO", "name": "Sun Pharmaceutical", "sector": "Pharma"},
    {"symbol": "TITAN.BO", "name": "Titan Company", "sector": "Consumer"},
    {"symbol": "BAJAJFINSV.BO", "name": "Bajaj Finserv", "sector": "Finance"},
    {"symbol": "NTPC.BO", "name": "NTPC", "sector": "Power"},
    {"symbol": "ONGC.BO", "name": "Oil & Natural Gas Corp", "sector": "Energy"},
    {"symbol": "POWERGRID.BO", "name": "Power Grid Corp", "sector": "Power"},
    {"symbol": "WIPRO.BO", "name": "Wipro", "sector": "IT"},
    {"symbol": "ULTRACEMCO.BO", "name": "UltraTech Cement", "sector": "Cement"},
    {"symbol": "NESTLEIND.BO", "name": "Nestle India", "sector": "FMCG"},
    {"symbol": "JSWSTEEL.BO", "name": "JSW Steel", "sector": "Metals"},
    {"symbol": "TATAMOTORS.BO", "name": "Tata Motors", "sector": "Auto"},
    {"symbol": "COALINDIA.BO", "name": "Coal India", "sector": "Mining"},
    {"symbol": "TATASTEEL.BO", "name": "Tata Steel", "sector": "Metals"},
    {"symbol": "M&M.BO", "name": "Mahindra & Mahindra", "sector": "Auto"},
]

# Sector index tickers (yfinance)
SECTOR_INDICES = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY Bank": "^NSEBANK",
    "NIFTY IT": "^CNXIT",
    "NIFTY Pharma": "^CNXPHARMA",
    "NIFTY Auto": "^CNXAUTO",
    "NIFTY FMCG": "^CNXFMCG",
    "NIFTY Metal": "^CNXMETAL",
    "NIFTY Energy": "^CNXENERGY",
    "NIFTY Realty": "^CNXREALTY",
}

# Extended NIFTY 500 — top 200 most actively traded beyond NIFTY 50
NIFTY500_EXTRA = [
    {"symbol": "ZOMATO.NS", "name": "Zomato", "sector": "Consumer"},
    {"symbol": "PAYTM.NS", "name": "One 97 Communications (Paytm)", "sector": "Fintech"},
    {"symbol": "NYKAA.NS", "name": "FSN E-Commerce (Nykaa)", "sector": "Consumer"},
    {"symbol": "POLICYBZR.NS", "name": "PB Fintech (PolicyBazaar)", "sector": "Fintech"},
    {"symbol": "IRCTC.NS", "name": "IRCTC", "sector": "Tourism"},
    {"symbol": "HAL.NS", "name": "Hindustan Aeronautics", "sector": "Defence"},
    {"symbol": "SIEMENS.NS", "name": "Siemens India", "sector": "Industrial"},
    {"symbol": "ABB.NS", "name": "ABB India", "sector": "Industrial"},
    {"symbol": "HAVELLS.NS", "name": "Havells India", "sector": "Consumer"},
    {"symbol": "VOLTAS.NS", "name": "Voltas", "sector": "Consumer"},
    {"symbol": "PIDILITIND.NS", "name": "Pidilite Industries", "sector": "Chemicals"},
    {"symbol": "BERGEPAINT.NS", "name": "Berger Paints", "sector": "Consumer"},
    {"symbol": "MARICO.NS", "name": "Marico", "sector": "FMCG"},
    {"symbol": "GODREJCP.NS", "name": "Godrej Consumer Products", "sector": "FMCG"},
    {"symbol": "DABUR.NS", "name": "Dabur India", "sector": "FMCG"},
    {"symbol": "COLPAL.NS", "name": "Colgate-Palmolive India", "sector": "FMCG"},
    {"symbol": "EMAMILTD.NS", "name": "Emami", "sector": "FMCG"},
    {"symbol": "MUTHOOTFIN.NS", "name": "Muthoot Finance", "sector": "Finance"},
    {"symbol": "CHOLAFIN.NS", "name": "Cholamandalam Investment", "sector": "Finance"},
    {"symbol": "LICHSGFIN.NS", "name": "LIC Housing Finance", "sector": "Finance"},
    {"symbol": "RECLTD.NS", "name": "REC Limited", "sector": "Finance"},
    {"symbol": "PFC.NS", "name": "Power Finance Corp", "sector": "Finance"},
    {"symbol": "IRFC.NS", "name": "Indian Railway Finance Corp", "sector": "Finance"},
    {"symbol": "FEDERALBNK.NS", "name": "Federal Bank", "sector": "Banking"},
    {"symbol": "IDFCFIRSTB.NS", "name": "IDFC First Bank", "sector": "Banking"},
    {"symbol": "BANDHANBNK.NS", "name": "Bandhan Bank", "sector": "Banking"},
    {"symbol": "RBLBANK.NS", "name": "RBL Bank", "sector": "Banking"},
    {"symbol": "PNB.NS", "name": "Punjab National Bank", "sector": "Banking"},
    {"symbol": "CANBK.NS", "name": "Canara Bank", "sector": "Banking"},
    {"symbol": "BANKBARODA.NS", "name": "Bank of Baroda", "sector": "Banking"},
    {"symbol": "UNIONBANK.NS", "name": "Union Bank of India", "sector": "Banking"},
    {"symbol": "AUROPHARMA.NS", "name": "Aurobindo Pharma", "sector": "Pharma"},
    {"symbol": "TORNTPHARM.NS", "name": "Torrent Pharma", "sector": "Pharma"},
    {"symbol": "ALKEM.NS", "name": "Alkem Laboratories", "sector": "Pharma"},
    {"symbol": "LALPATHLAB.NS", "name": "Dr Lal PathLabs", "sector": "Healthcare"},
    {"symbol": "METROPOLIS.NS", "name": "Metropolis Healthcare", "sector": "Healthcare"},
    {"symbol": "MFSL.NS", "name": "Max Financial Services", "sector": "Insurance"},
    {"symbol": "ICICIGI.NS", "name": "ICICI Lombard", "sector": "Insurance"},
    {"symbol": "NIACL.NS", "name": "New India Assurance", "sector": "Insurance"},
    {"symbol": "STARHEALTH.NS", "name": "Star Health Insurance", "sector": "Insurance"},
    {"symbol": "TATAPOWER.NS", "name": "Tata Power", "sector": "Power"},
    {"symbol": "ADANIGREEN.NS", "name": "Adani Green Energy", "sector": "Power"},
    {"symbol": "TORNTPOWER.NS", "name": "Torrent Power", "sector": "Power"},
    {"symbol": "CESC.NS", "name": "CESC", "sector": "Power"},
    {"symbol": "HINDZINC.NS", "name": "Hindustan Zinc", "sector": "Metals"},
    {"symbol": "NATIONALUM.NS", "name": "National Aluminium", "sector": "Metals"},
    {"symbol": "SAIL.NS", "name": "Steel Authority of India", "sector": "Metals"},
    {"symbol": "NMDC.NS", "name": "NMDC", "sector": "Mining"},
    {"symbol": "VEDL.NS", "name": "Vedanta", "sector": "Metals"},
    {"symbol": "APOLLOTYRE.NS", "name": "Apollo Tyres", "sector": "Auto"},
    {"symbol": "BALKRISIND.NS", "name": "Balkrishna Industries", "sector": "Auto"},
    {"symbol": "MOTHERSON.NS", "name": "Samvardhana Motherson", "sector": "Auto"},
    {"symbol": "BOSCHLTD.NS", "name": "Bosch India", "sector": "Auto"},
    {"symbol": "MHRIL.NS", "name": "Mahindra Holidays", "sector": "Tourism"},
    {"symbol": "INDHOTEL.NS", "name": "Indian Hotels (Taj)", "sector": "Tourism"},
    {"symbol": "LEMONTREE.NS", "name": "Lemon Tree Hotels", "sector": "Tourism"},
    {"symbol": "DLF.NS", "name": "DLF", "sector": "Realty"},
    {"symbol": "GODREJPROP.NS", "name": "Godrej Properties", "sector": "Realty"},
    {"symbol": "OBEROIRLTY.NS", "name": "Oberoi Realty", "sector": "Realty"},
    {"symbol": "PRESTIGE.NS", "name": "Prestige Estates", "sector": "Realty"},
    {"symbol": "MUTHOOTFIN.NS", "name": "Muthoot Finance", "sector": "Finance"},
    {"symbol": "COFORGE.NS", "name": "Coforge", "sector": "IT"},
    {"symbol": "MPHASIS.NS", "name": "Mphasis", "sector": "IT"},
    {"symbol": "LTIM.NS", "name": "LTIMindtree", "sector": "IT"},
    {"symbol": "PERSISTENT.NS", "name": "Persistent Systems", "sector": "IT"},
    {"symbol": "OFSS.NS", "name": "Oracle Financial Services", "sector": "IT"},
    {"symbol": "KPITTECH.NS", "name": "KPIT Technologies", "sector": "IT"},
]

NIFTY500 = NIFTY50 + NIFTY500_EXTRA


def get_all_symbols(exchange="NSE"):
    """Return flat list of ticker symbols for an exchange."""
    if exchange == "NSE":
        return [s["symbol"] for s in NIFTY500]
    elif exchange == "BSE":
        return [s["symbol"] for s in SENSEX30]
    return []


def get_symbol_name_map():
    """Return dict of symbol -> name for autocomplete."""
    result = {}
    for s in NIFTY500:
        result[s["symbol"]] = s["name"]
    for s in SENSEX30:
        result[s["symbol"]] = s["name"]
    return result


def get_nifty50_symbols():
    return [s["symbol"] for s in NIFTY50]


def get_sensex30_symbols():
    return [s["symbol"] for s in SENSEX30]
