package clinical_recommendations.rules

recommendations contains "Physical Therapy" if {
    input.age > 65
    input.has_chronic_pain == true
}

recommendations contains "Weight Management Program" if {
    input.bmi > 30
}

recommendations contains "Post-Op Rehabilitation Plan" if {
    input.recent_surgery == true
}
