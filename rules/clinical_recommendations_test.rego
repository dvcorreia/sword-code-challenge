package clinical_recommendations.rules.test

import data.clinical_recommendations.rules

test_elderly_with_chronic_pain if {
    patient_data := {
        "age": 70,
        "has_chronic_pain": true,
        "bmi": 25,
        "recent_surgery": false
    }

    recommendations := rules.recommendations with input as patient_data
    recommendations["Physical Therapy"]
    count(recommendations) == 1
}

test_overweight_patient if {
    patient_data := {
        "age": 45,
        "has_chronic_pain": false,
        "bmi": 32,
        "recent_surgery": false
    }

    recommendations := rules.recommendations with input as patient_data
    recommendations["Weight Management Program"]
    count(recommendations) == 1
}

test_post_surgery_patient if {
    patient_data := {
        "age": 50,
        "has_chronic_pain": false,
        "bmi": 27,
        "recent_surgery": true
    }

    recommendations := rules.recommendations with input as patient_data
    recommendations["Post-Op Rehabilitation Plan"]
    count(recommendations) == 1
}

test_multiple_recommendations if {
    patient_data := {
        "age": 68,
        "has_chronic_pain": true,
        "bmi": 31,
        "recent_surgery": false
    }

    recommendations := rules.recommendations with input as patient_data

    recommendations["Physical Therapy"]
    recommendations["Weight Management Program"]
    count(recommendations) == 2
}

test_surgery_with_chronic_pain if {
    patient_data := {
        "age": 55,
        "has_chronic_pain": true,
        "bmi": 28,
        "recent_surgery": true
    }

    recommendations := rules.recommendations with input as patient_data
    recommendations["Post-Op Rehabilitation Plan"]
    count(recommendations) == 1
}

test_no_recommendations if {
    patient_data := {
        "age": 30,
        "has_chronic_pain": false,
        "bmi": 22,
        "recent_surgery": false
    }

    recommendations := rules.recommendations with input as patient_data
    count(recommendations) == 0
}