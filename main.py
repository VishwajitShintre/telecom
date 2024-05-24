import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import joblib
import os
from user_management import authenticate, add_user
from preprocessing import preprocess


def main():
    st.title('Telco Customer Churn Prediction App')

    current_dir = os.path.dirname(__file__)
    image_path = os.path.join(current_dir, 'App.jpg')

    if os.path.exists(image_path):
        image = Image.open(image_path)
        st.image(image, caption='App Image')
    else:
        st.error(f"Image file not found at {image_path}")

    model_path = os.path.join(current_dir, 'notebook', 'model.sav')
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        st.write("Model loaded successfully!")
    else:
        st.error(f"Model file not found at {model_path}")

    st.markdown("""
     :dart:  This Streamlit app is made to predict customer churn in a fictional telecommunication use case.
    The application is functional for both online prediction and batch data prediction. \n
    """)

    add_selectbox = st.sidebar.selectbox(
        "How would you like to predict?", ("Online", "Batch")
    )
    st.sidebar.info('This app is created to predict Customer Churn')
    if os.path.exists(image_path):
        st.sidebar.image(image)

    if add_selectbox == "Online":
        st.info("Input data below")
        st.subheader("Demographic data")
        seniorcitizen = st.selectbox('Senior Citizen:', ('Yes', 'No'))
        dependents = st.selectbox('Dependent:', ('Yes', 'No'))

        st.subheader("Payment data")
        tenure = st.slider('Number of months the customer has stayed with the company', min_value=0, max_value=72,
                           value=0)
        contract = st.selectbox('Contract', ('Month-to-month', 'One year', 'Two year'))
        paperlessbilling = st.selectbox('Paperless Billing', ('Yes', 'No'))
        payment_method = st.selectbox('PaymentMethod', (
        'Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)'))
        monthlycharges = st.number_input('The amount charged to the customer monthly', min_value=0, max_value=150,
                                         value=0)
        totalcharges = st.number_input('The total amount charged to the customer', min_value=0, max_value=10000,
                                       value=0)

        st.subheader("Services signed up for")
        mutliplelines = st.selectbox("Does the customer have multiple lines", ('Yes', 'No', 'No phone service'))
        phoneservice = st.selectbox('Phone Service:', ('Yes', 'No'))
        internetservice = st.selectbox("Does the customer have internet service", ('DSL', 'Fiber optic', 'No'))
        onlinesecurity = st.selectbox("Does the customer have online security", ('Yes', 'No', 'No internet service'))
        onlinebackup = st.selectbox("Does the customer have online backup", ('Yes', 'No', 'No internet service'))
        techsupport = st.selectbox("Does the customer have technology support", ('Yes', 'No', 'No internet service'))
        streamingtv = st.selectbox("Does the customer stream TV", ('Yes', 'No', 'No internet service'))
        streamingmovies = st.selectbox("Does the customer stream movies", ('Yes', 'No', 'No internet service'))

        data = {
            'SeniorCitizen': seniorcitizen,
            'Dependents': dependents,
            'tenure': tenure,
            'PhoneService': phoneservice,
            'MultipleLines': mutliplelines,
            'InternetService': internetservice,
            'OnlineSecurity': onlinesecurity,
            'OnlineBackup': onlinebackup,
            'TechSupport': techsupport,
            'StreamingTV': streamingtv,
            'StreamingMovies': streamingmovies,
            'Contract': contract,
            'PaperlessBilling': paperlessbilling,
            'PaymentMethod': payment_method,
            'MonthlyCharges': monthlycharges,
            'TotalCharges': totalcharges
        }
        features_df = pd.DataFrame.from_dict([data])
        st.write('Overview of input is shown below')
        st.dataframe(features_df)

        preprocess_df = preprocess(features_df, 'Online')

        if st.button('Predict'):
            prediction = model.predict(preprocess_df)
            prediction_proba = model.predict_proba(preprocess_df)[0][1]

            if prediction == 1:
                st.warning(f'Yes, the customer will terminate the service. Probability: {prediction_proba:.2f}')
            else:
                st.success(f'No, the customer is happy with Telco Services. Probability: {1 - prediction_proba:.2f}')
    else:
        st.subheader("Dataset upload")
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)
            st.write(data.head())

            preprocess_df = preprocess(data, "Batch")
            if st.button('Predict'):
                prediction = model.predict(preprocess_df)
                prediction_proba = model.predict_proba(preprocess_df)[:, 1]
                prediction_df = pd.DataFrame({
                    "Predictions": prediction,
                    "Probability": prediction_proba
                })
                prediction_df["Predictions"] = prediction_df["Predictions"].replace(
                    {1: 'Yes, the customer will terminate the service.',
                     0: 'No, the customer is happy with Telco Services.'})

                st.subheader('Prediction')
                st.write(prediction_df)


def register():
    st.title("User Registration")
    new_username = st.text_input("Enter a username")
    new_password = st.text_input("Enter a password", type="password")

    if st.button("Register"):
        if new_username and new_password:
            success = add_user(new_username, new_password)
            if success:
                st.success("You have successfully registered!")
                st.session_state['registered'] = True
                st.session_state['is_registering'] = False
            else:
                st.warning("Username already exists. Please choose a different one.")
        else:
            st.warning("Please fill out all fields.")

    if st.button("Back to Login"):
        st.session_state['is_registering'] = False


def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(username, password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success("Logged in successfully!")
        else:
            st.error("Username or password is incorrect")

    if st.button("Register Here"):
        st.session_state['is_registering'] = True


if __name__ == '__main__':
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'is_registering' not in st.session_state:
        st.session_state['is_registering'] = False
    if 'registered' not in st.session_state:
        st.session_state['registered'] = False

    if st.session_state['is_registering']:
        register()
    elif st.session_state['logged_in']:
        main()
    elif st.session_state['registered']:
        st.session_state['registered'] = False
        login()
    else:
        login()
