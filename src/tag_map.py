# src/tag_map.py

TAGS = {
    "operating_cash_flow": [
        "us-gaap:NetCashProvidedByUsedInOperatingActivities",
        "ifrs-full:CashFlowsFromUsedInOperatingActivities",
        "us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
        "us-gaap:CashProvidedByUsedInOperatingActivitiesDirect",
    ],
    "cash_and_cash_equivalents": [
        "us-gaap:CashAndCashEquivalentsAtCarryingValue",
        "ifrs-full:CashAndCashEquivalents",
    ],
    "current_portion_of_long-term_debt": [
        "us-gaap:LongTermDebtCurrent",
        "ifrs-full:CurrentPortionOfLongTermBorrowings",
        "ifrs-full:CurrentPortionOfLongtermBorrowings",
    ],
    "long-term_debt": [
        "us-gaap:LongTermDebtNoncurrent",
        "us-gaap:LongTermDebt",
        "ifrs-full:NoncurrentPortionOfNoncurrentBondsIssued",
        "ifrs-full:NoncurrentBorrowings",
    ],
    "short-term_borrowings": [
        "us-gaap:ShortTermBorrowings",
        "us-gaap:ShortTermDebt",
        "ifrs-full:CurrentBorrowings",
    ],
    "total_stockholders_equity": [
        "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        "us-gaap:StockholdersEquity",
        "ifrs-full:Equity",
    ],
    "net_revenues": [
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "us-gaap:Revenues",
        "ifrs-full:Revenue",
    ],
    "gross_profit": [
        "us-gaap:GrossProfit",
        "ifrs-full:GrossProfit",
    ],
    "operating_income": [
        "us-gaap:OperatingIncomeLoss",
        "ifrs-full:ProfitLossFromOperatingActivities",
    ],
    "earnings_before_income_tax": [
        "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        "us-gaap:IncomeBeforeEquityMethodInvestments",
        "ifrs-full:ProfitLossBeforeTax",
    ],
    "basic_and_diluted_earnings_per_share": [
        "us-gaap:EarningsPerShareBasicAndDiluted",
        "us-gaap:EarningsPerShareBasic",
        "us-gaap:EarningsPerShareDiluted",
        "ifrs-full:BasicEarningsLossPerShare",
    ],
    "provision_for_income_taxes": [
        "us-gaap:IncomeTaxExpenseBenefit",
        "ifrs-full:IncomeTaxExpenseContinuingOperations",
    ],
    "capital_expenditures": [
        "us-gaap:PaymentsToAcquirePropertyPlantAndEquipment",
        "us-gaap:CapitalExpendituresIncurredButNotYetPaid",
        "us-gaap:CapitalExpenditures",
        "ifrs-full:PaymentsForPropertyPlantAndEquipment",
        "ifrs-full:PurchaseOfPropertyPlantAndEquipment",
        "ifrs-full:PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities",
    ],
    "capital_stock": [
        "us-gaap:CommonStockSharesOutstanding",
        "dei:EntityCommonStockSharesOutstanding",
        "ifrs-full:NumberOfSharesIssued",
        "ifrs-full:SharesIssued",
        "ifrs-full:SharesOutstanding",
    ],
    "interest_expense": [
        "us-gaap:InterestExpense",
        "ifrs-full:FinanceCosts",
    ],
    "depreciation": [
        "us-gaap:Depreciation",
        "us-gaap:DepreciationExpense",
        "ifrs-full:Depreciation",
        "ifrs-full:DepreciationExpense",
    ],
    "amortization": [
        "us-gaap:AmortizationOfIntangibleAssets",
        "ifrs-full:Amortisation",
        "ifrs-full:AmortisationExpense",
    ],
    "dividends_paid_on_common_stock": [
        "us-gaap:PaymentsOfDividendsCommonStock",
        "us-gaap:DividendsCommonStockCash",
        "ifrs-full:DividendsPaid",
    ],
}

