
import streamlit as st
from prediction_helper import predict

# ==============================================================================
# 1. 页面基础配置 (Page Configuration)
# ==============================================================================
st.set_page_config(page_title="Health Insurance Prediction", layout="wide")

# ==============================================================================
# 2. UI 数据源 (Data Source for UI Widgets)
# ==============================================================================

# --- 数值输入配置 (Numerical Inputs Configuration) ---
# 将数值型输入也配置化，方便管理
# 我们可以从df.describe()的结果中获取合理的min/max值
numerical_inputs_config = {
    'age': {'label': 'Age', 'min_value': 18, 'max_value': 100, 'step': 1, 'help': 'Please enter your age.'},
    'income_lakhs': {'label': 'Income (Lakhs)', 'min_value': 1.0, 'max_value': 1000.0, 'step': 1.0,
                     'help': 'Enter your annual income in Lakhs.'},
    'number_of_dependants': {'label': 'Number of Dependants', 'min_value': 0, 'max_value': 10, 'step': 1,
                             'help': 'How many dependants do you have?'},
'genetical_risk': {'label': 'Genetical Risk Level', 'min_value': 1, 'max_value': 5, 'step': 1,
                   'help': 'Select your assessed genetical risk level (1-5).'}
}

# --- 分类输入配置 (Categorical Inputs Configuration) ---
# 在这里添加 'region'
categorical_options = {
    'gender': ['Male', 'Female'],
    'region': ['Northwest', 'Southeast', 'Northeast', 'Southwest'],  # <-- 新增
    'marital_status': ['Married', 'Unmarried'],
    'bmi_category': ['Normal', 'Overweight', 'Obesity', 'Underweight'],
    'smoking_status': ['Non-Smoker', 'Occasional', 'Regular'],
    'employment_status': ['Salaried', 'Self-Employed', 'Freelancer'],
    'income_level': ['<10L', '10L - 25L', '25L - 40L', '> 40L'],
    'medical_history': [
        'No Disease', 'Diabetes', 'High blood pressure', 'Thyroid', 'Heart disease',
        'Diabetes & High blood pressure', 'Diabetes & Thyroid',
        'High blood pressure & Heart disease', 'Diabetes & Heart disease'
    ],
    'insurance_plan': ['Bronze', 'Silver', 'Gold']
}

# ==============================================================================
# 3. UI 界面渲染 (UI Rendering)
# ==============================================================================

# --- 主标题 ---
st.title("🏥 Health Insurance Prediction App")
st.markdown("---")

# --- 输入表单区域 ---
st.header("Please provide your details below:")

# 用于存储用户输入的字典
user_inputs = {}

# --- 动态生成数值输入网格 (Dynamic Numerical Input Grid) ---
# 现在数值输入也变成了动态网格
num_numerical = len(numerical_inputs_config)
numerical_cols = st.columns(num_numerical)

for i, (key, config) in enumerate(numerical_inputs_config.items()):
    with numerical_cols[i]:
        user_inputs[key] = st.number_input(
            label=config['label'],
            min_value=config['min_value'],
            max_value=config['max_value'],
            step=config['step'],
            help=config['help']
        )

st.markdown("<br>", unsafe_allow_html=True)

# --- 动态生成选项卡网格 (Dynamic Categorical Input Grid) ---
# 这部分代码完全不需要修改！
COLS_PER_ROW = 3
options_list = list(categorical_options.items())
num_options = len(options_list)

for i in range(0, num_options, COLS_PER_ROW):
    cols = st.columns(COLS_PER_ROW)
    row_options = options_list[i: i + COLS_PER_ROW]

    for j, (key, options) in enumerate(row_options):
        # 检查是否还有剩余的列可以使用
        if j < len(cols):
            with cols[j]:
                label = key.replace('_', ' ').title()
                if key == 'medical_history':
                    user_inputs[key] = st.multiselect(label, options, help=f"Select all applicable medical conditions.")
                else:
                    user_inputs[key] = st.selectbox(label, options, help=f"Select your {label.lower()}.")

st.markdown("<br><br>", unsafe_allow_html=True)

_, button_col = st.columns([4, 1])  # 调整比例以适应更宽的布局

with button_col:
    if st.button("✨ Get Prediction", use_container_width=True):
        print("Predict Button Clicked")
        prediction = predict(user_inputs)
        st.success(f"Prediction Premium: {prediction}")

