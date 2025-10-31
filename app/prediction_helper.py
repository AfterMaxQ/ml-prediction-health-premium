from joblib import load
import pandas as pd
import sklearn

model_rest = load("artifacts\model_rest.joblib")
model_young = load("artifacts\model_young.joblib")

scaler_rest = load("artifacts\scaler_rest.joblib")
scaler_young = load("artifacts\scaler_young.joblib")

def calculate_normalized_risk(medical_history_list):
    RISK_SCORES = {
        "diabetes": 6,
        "heart disease": 8,
        "high blood pressure": 6,
        "thyroid": 5,
        "no disease": 0,
        "none": 0  # 'none' is a placeholder for empty slots after splitting
    }
    total_risk_score = 0
    MIN_SCORE_TRAIN = 0.0  # The minimum possible raw score (e.g., 'No Disease')
    MAX_SCORE_TRAIN = 14.0  # The maximum possible raw score (e.g., 'Heart Disease' + 'Diabetes')

    if not isinstance(medical_history_list, list):
        medical_history_list = [medical_history_list]

    if not medical_history_list or 'No disease' in medical_history_list:
        return 0.0

    for condition in medical_history_list:
        clean_condition = condition.lower().strip()
        total_risk_score += RISK_SCORES.get(clean_condition, 0)

    nomalized_score = (total_risk_score - MIN_SCORE_TRAIN)/(MAX_SCORE_TRAIN - MIN_SCORE_TRAIN)
    return max(0.0, min(1.0, nomalized_score))


MODEL_FINAL_COLS = [
    'age', 'number_of_dependants', 'income_lakhs', 'insurance_plan',
    'genetical_risk', 'normalized_risk_score', 'gender_Male',
    'region_Northwest', 'region_Southeast', 'region_Southwest',
    'marital_status_Unmarried', 'bmi_category_Obesity',
    'bmi_category_Overweight', 'bmi_category_Underweight',
    'smoking_status_Occasional', 'smoking_status_Regular',
    'employment_status_Salaried', 'employment_status_Self-Employed'
]


def preprocess_input(input_dict):
    # This list contains all columns needed for ANY preprocessing step (like scaling)
    initial_columns = [
        'age', 'number_of_dependants', 'income_level', 'income_lakhs',
        'insurance_plan', 'normalized_risk_score', 'genetical_risk',
        'gender_Male', 'region_Northwest', 'region_Southeast', 'region_Southwest',
        'marital_status_Unmarried', 'bmi_category_Obesity', 'bmi_category_Overweight',
        'bmi_category_Underweight', 'smoking_status_Occasional', 'smoking_status_Regular',
        'employment_status_Salaried', 'employment_status_Self-Employed'
    ]
    df = pd.DataFrame(columns=initial_columns, index=[0])

    # --- 1. Fill all columns with values or placeholders ---
    df['age'] = input_dict.get('age', 0)
    df['number_of_dependants'] = input_dict.get('number_of_dependants', 0)
    df['income_lakhs'] = input_dict.get("income_lakhs", 0.0)
    df['genetical_risk'] = input_dict.get('genetical_risk', 1)
    df['income_level'] = 0  # Placeholder for the scaler

    insurance_plan_encoding = {'Bronze': 1, 'Silver': 2, 'Gold': 3}
    plan = input_dict.get('insurance_plan', "Bronze")
    df["insurance_plan"] = insurance_plan_encoding.get(plan, 1)

    user_medical_history = input_dict.get('medical_history', ['No Disease'])
    risk_score = calculate_normalized_risk(user_medical_history)
    df["normalized_risk_score"] = risk_score

    one_hot_cols = ['gender', 'region', 'marital_status', 'bmi_category',
                    'smoking_status', 'employment_status']
    for col in one_hot_cols:
        user_choice = input_dict.get(col)
        if user_choice:
            # Clean up the user choice for column name matching
            # E.g., 'Self-Employed' -> 'Self-Employed'
            cleaned_choice = user_choice.replace(' ', '_').replace('-', '_')
            target_column = f"{col}_{cleaned_choice}"
            if target_column in df.columns:
                df[target_column] = 1

    df.fillna(0, inplace=True)

    # --- 2. Perform Scaling (df still has 'income_level' at this point) ---
    df = handle_scaling(df['age'].item(), df)

    # --- 3. THE CRITICAL FIX: Prepare the final DataFrame for the MODEL ---
    # After all preprocessing is done, select and reorder columns to match the model's contract.
    # This action BOTH drops 'income_level' AND guarantees the correct order.
    final_df = df[MODEL_FINAL_COLS]

    return final_df


def handle_scaling(age, df):
    # This function is now correct and doesn't need changes.
    scaler_object = scaler_young if age <= 25 else scaler_rest
    cols_to_scale = scaler_object['cols_to_scale']
    scaler = scaler_object['scaler']

    df[cols_to_scale] = scaler.transform(df[cols_to_scale])
    return df


def predict(input_dict):
    # This function now correctly receives a perfectly formatted DataFrame
    input_df = preprocess_input(input_dict)

    age_value = input_df['age'].item()

    if age_value <= 25:
        prediction = model_young.predict(input_df)
    else:
        prediction = model_rest.predict(input_df)

    return int(prediction[0])
