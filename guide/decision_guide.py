def evaluate_answers(answers):
    scores = {"quickbooks": 0, "odoo": 0}

    rules = {
        "priority": {
            "accounting": {"quickbooks": 6},
            "mixed": {"quickbooks": 3, "odoo": 3},
            "operations": {"odoo": 6},
        },
        "complexity": {
            "low": {"quickbooks": 5},
            "medium": {"quickbooks": 3, "odoo": 3},
            "high": {"odoo": 5},
        },
        "integration": {
            "low": {"quickbooks": 5},
            "medium": {"quickbooks": 3, "odoo": 3},
            "high": {"odoo": 5},
        },
        "growth": {
            "stable": {"quickbooks": 4},
            "growing": {"quickbooks": 2, "odoo": 3},
            "scaling": {"odoo": 5},
        },
        "industry": {
            "services": {"quickbooks": 4},
            "trade": {"quickbooks": 3, "odoo": 2},
            "manufacturing": {"odoo": 5},
            "agriculture": {"odoo": 4},
            "hospitality": {"quickbooks": 2, "odoo": 3},
        },
        "business_size": {
            "small": {"quickbooks": 5},
            "medium": {"quickbooks": 2, "odoo": 3},
            "large": {"odoo": 5},
        },
        "budget": {
            "rapid": {"quickbooks": 5},
            "balanced": {"quickbooks": 2, "odoo": 3},
            "strategic": {"odoo": 5},
        },
        "compliance": {
            "standard": {"quickbooks": 4},
            "regional": {"quickbooks": 2, "odoo": 3},
            "global": {"odoo": 5},
        },
    }

    for key, value in answers.items():
        if key in rules and value in rules[key]:
            for system, score in rules[key][value].items():
                scores[system] += score

    if scores["odoo"] >= scores["quickbooks"] + 4:
        return {
            "system": "Odoo ERP",
            "explanation": "Your organisation is best served by an integrated ERP platform that supports complex operations, multi-entity compliance, and strategic growth.",
            "focus": "Core focus: finance, operations, compliance, and inventory.",
            "modules": "Recommended Odoo modules: Accounting, Sales, Inventory, Purchase, Manufacturing, HR.",
            "risks": "Implementation requires careful planning and investment in process design.",
            "approach": "Adopt core Odoo modules first, align stakeholders, and phase deployment across finance, inventory, and operations."
        }

    if scores["quickbooks"] >= scores["odoo"] + 4:
        return {
            "system": "QuickBooks Online",
            "explanation": "Your current priority is efficient financial control with a fast deployment path and predictable operating cost.",
            "focus": "Core focus: accounting, cash flow, financial reporting, and cost control.",
            "modules": "Recommended QuickBooks setup: accounting, invoicing, bank reconciliation, payroll.",
            "risks": "The solution will be less suitable for deep operational integration or rapid multi-entity scaling.",
            "approach": "Use disciplined accounting structure, automation for invoicing, and review reporting requirements before adding more systems."
        }

    return {
        "system": "Hybrid Strategy",
        "explanation": "A mix of financial agility and long-term operational capability is the best fit for your business profile.",
        "focus": "Core focus: finance stabilization today and ERP readiness for future operations.",
        "modules": "Phase 1: QuickBooks for accounting and cashflow. Phase 2: Odoo for operations, inventory, and compliance.",
        "risks": "You should manage integration and migration carefully to avoid duplicate processes.",
        "approach": "Implement QuickBooks for finance now while planning an Odoo roadmap to support operations, inventory, and compliance in the next 12–18 months."
    }
