def evaluate_answers(answers):
    """
    Evaluate user answers and recommend an ERP system based on database-driven scoring rules.
    """
    from .models import ERPSystem, ScoringRule, DecisionThreshold, Question, QuestionOption

    # Get all active ERP systems
    erp_systems = ERPSystem.objects.filter(
        is_active=True).values_list('name', flat=True)
    scores = {system: 0 for system in erp_systems}

    # Apply scoring rules from database
    for field_key, answer_value in answers.items():
        # Skip non-question fields
        if field_key in ['company_name', 'anonymous']:
            continue

        try:
            # Find the question and its option
            question = Question.objects.get(field_key=field_key)
            question_option = QuestionOption.objects.get(
                question=question, key=answer_value, is_active=True)

            # Get all scoring rules for this option
            rules = ScoringRule.objects.filter(
                question_option=question_option,
                is_active=True
            )

            # Apply scores
            for rule in rules:
                scores[rule.erp_system.name] += rule.score
        except (Question.DoesNotExist, QuestionOption.DoesNotExist):
            # Skip if question or option not found (in case system configuration changes)
            continue

    # Determine recommendation based on thresholds
    thresholds = {
        t.erp_system.name: t for t in DecisionThreshold.objects.all()}

    # Sort systems by score
    sorted_systems = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    if not sorted_systems:
        # Fallback if no systems are configured
        return get_fallback_recommendation()

    top_system = sorted_systems[0][0]
    top_score = sorted_systems[0][1]
    second_score = sorted_systems[1][1] if len(sorted_systems) > 1 else 0

    # Get the ERP system object for details
    top_erp = ERPSystem.objects.get(name=top_system)

    # Check if we should recommend the top system or use fallback
    threshold = thresholds.get(top_system)

    if threshold and threshold.is_fallback:
        # This is a fallback system (e.g., Hybrid), check if scores are too close
        if len(sorted_systems) > 1:
            # Get the first non-fallback system
            for system_name, system_score in sorted_systems:
                sys_threshold = thresholds.get(system_name)
                if sys_threshold and not sys_threshold.is_fallback:
                    if system_score >= (sorted_systems[0][1] - 5):
                        top_erp = ERPSystem.objects.get(name=system_name)
                        break
    elif threshold:
        # Check if advantage is large enough
        min_advantage = threshold.min_score_advantage
        if len(sorted_systems) > 1 and (top_score - second_score) < min_advantage:
            # Advantage not large enough, check for fallback
            fallback_systems = DecisionThreshold.objects.filter(
                is_fallback=True)
            if fallback_systems.exists():
                top_erp = fallback_systems.first().erp_system

    # Calculate confidence score (0-100)
    max_possible_score = sum(scores.values()) if scores.values() else 1
    confidence = (top_score / max_possible_score *
                  100) if max_possible_score > 0 else 50

    return {
        'system': top_erp.name,
        'explanation': top_erp.description,
        'focus': top_erp.focus,
        'modules': top_erp.modules,
        'risks': top_erp.risks,
        'approach': top_erp.approach,
        'confidence': confidence,
    }


def get_fallback_recommendation():
    """Fallback recommendation if no scoring rules are configured"""
    from .models import ERPSystem

    try:
        default_system = ERPSystem.objects.filter(is_active=True).first()
        if default_system:
            return {
                'system': default_system.name,
                'explanation': default_system.description,
                'focus': default_system.focus,
                'modules': default_system.modules,
                'risks': default_system.risks,
                'approach': default_system.approach,
                'confidence': 50.0,
            }
    except:
        pass

    # Ultimate fallback
    return {
        'system': 'Hybrid Strategy',
        'explanation': 'Please configure scoring rules in the admin panel.',
        'focus': 'System not fully configured',
        'modules': 'N/A',
        'risks': 'N/A',
        'approach': 'Please set up ERP systems and scoring rules',
        'confidence': 0.0,
    }
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
