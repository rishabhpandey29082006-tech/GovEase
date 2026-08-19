def check_eligibility(user, scheme):
    eligibility = scheme.get("eligibility", {})

    score = 100
    reasons = []
    matched = []
    missing_documents = []

    age = user.get("age")
    gender = user.get("gender")
    occupation = user.get("occupation")
    category = user.get("category")
    education = user.get("education")
    percentage = user.get("percentage")
    documents = user.get("documents", {})

    # AGE
    if age is not None:

        if "minimum_age" in eligibility:
            if age >= eligibility["minimum_age"]:
                matched.append("Age requirement matched")
            else:
                score -= 30
                reasons.append(
                    f"Minimum age required: {eligibility['minimum_age']}"
                )

        if "maximum_age" in eligibility:
            if age <= eligibility["maximum_age"]:
                matched.append("Age requirement matched")
            else:
                score -= 30
                reasons.append(
                    f"Maximum age allowed: {eligibility['maximum_age']}"
                )

    # GENDER
    if "gender" in eligibility:
        if gender in eligibility["gender"]:
            matched.append("Gender requirement matched")
        else:
            score -= 35
            reasons.append("Gender requirement not matched")

    # OCCUPATION
    if "occupations" in eligibility:
        if occupation in eligibility["occupations"]:
            matched.append("Occupation requirement matched")
        else:
            score -= 35
            reasons.append("Occupation requirement not matched")

    # CATEGORY
    if "categories" in eligibility:
        if category in eligibility["categories"]:
            matched.append("Social category matched")
        else:
            score -= 35
            reasons.append("Social category not matched")

    # EDUCATION
    if "education" in eligibility:
        if education in eligibility["education"]:
            matched.append("Education requirement matched")
        else:
            score -= 25
            reasons.append("Education requirement not matched")

    # PERCENTAGE
    if "minimum_percentage" in eligibility:

        minimum = eligibility["minimum_percentage"]

        if percentage is not None:

            if percentage >= minimum:
                matched.append("Percentage requirement matched")
            else:
                score -= 30
                reasons.append(
                    f"Minimum percentage required: {minimum}%"
                )

    # DOCUMENTS
    required_documents = eligibility.get("documents", [])

    for document in required_documents:

        if documents.get(document, False):
            matched.append(f"{document} available")
        else:
            missing_documents.append(document)

    if missing_documents:

        score -= min(30, len(missing_documents) * 10)

        reasons.append(
            "Missing documents: " + ", ".join(missing_documents)
        )

    # SCORE LIMIT
    score = max(0, min(100, score))

    # STATUS
    if score >= 80:
        status = "Eligible"

    elif score >= 50:
        status = "Partially Eligible"

    else:
        status = "Not Eligible"

    # RESULT
    return {
        "scheme_id": scheme.get("id"),
        "scheme_name": scheme.get("name"),
        "category": scheme.get("category"),
        "benefit": scheme.get("benefit"),
        "status": status,
        "eligibility_percentage": score,
        "matched": matched,
        "reasons": reasons,
        "missing_documents": missing_documents
    }


def check_all_schemes(user, schemes):

    results = []

    for scheme in schemes:

        result = check_eligibility(user, scheme)

        results.append(result)

    results.sort(
        key=lambda item: item["eligibility_percentage"],
        reverse=True
    )

    return results