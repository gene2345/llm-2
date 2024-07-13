import streamlit as st
from dataFunc import add_user_behaviour  
from dataFunc import llm_ask, llm_ask_food, user_summary

def main():
    st.set_page_config(page_title="Driving Behaviour Log", layout="wide")

    st.markdown("""
        <style>
            .reportview-container {
                display: flex;
                flex-direction: column;
                align-items: stretch;
                margin-top: -3rem; /* Adjust the top margin to move content upwards */
            }
            .reportview-container .main .block-container {
                flex: 1 1 auto;
                overflow-y: auto;
                padding: 1rem;
            }
            .reportview-container .main {
                display: flex;
                flex-direction: row;
                align-items: flex-start; /* Align items at the start of the row */
            }
            .reportview-container .sidebar .sidebar-content {
                padding: 1rem;
            }
            .reportview-container .main .sidebar.affected {
                display: none;
            }
            .reportview-container .main .block-container {
                flex: 1;
                padding: 20px;
                background-color: #f0f0f0;
                overflow-y: auto;
            }
            footer {
                visibility: hidden;
            }
            .stDeployButton {
                display: none;
            }
            #stDecoration {
                display: none;
            }
            .day-counter {
                position: absolute;
                top: 10px;
                right: 10px;
                font-size: 24px;
                font-weight: bold;
            }
            .insight-container {
                padding: 10px;
                margin-top: 20px;
                color: gray; /* Black text color */
                border-radius: 5px;
                color: #e6e6e6;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); /* Soft shadow effect */
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.title('Driving Behaviour Log')

    if 'day_count' not in st.session_state:
        st.session_state.day_count = 0
    
    st.markdown(f'<div class="day-counter">Day: {st.session_state.day_count}</div>', unsafe_allow_html=True)

    with st.form(key='input_form', clear_on_submit=True):
        car1 = st.text_input('Locations visited', key='car1')
        car2 = st.text_input('Travelling Time', key='car2')
        car3 = st.text_input('Engine Load Sensor', key='car3')
        car4 = st.text_input('MAP Sensor', key='car4')
        car5 = st.text_input('Acceleration Pattern Sensor', key='car5')
        car6 = st.text_input('Fuel Temperature Sensor', key='car6')
        car7 = st.text_input('Voltage Sensor', key='car7')
        car8 = st.text_input('RPM Sensor', key='car8')
        car9 = st.text_input('Max Speed Sensor', key='car9')
        car10 = st.text_input('Maintenance Alerts', key='car10')

        # Submit button
        submit_button = st.form_submit_button('Submit')

    # Process input after form submission
    if submit_button:
        process_input(car1, car2, car3, car4, car5, car6, car7, car8, car9, car10)

    if st.button('Generate Insight', key='generate_insight_button'):
        generate_insight()

    if st.button('Generate Food Recommendations', key='gen'):
        generate_food_insight()

def process_input(car1, car2, car3, car4, car5, car6, car7, car8, car9, car10):
    context1 = "Locations visited" + str(car1) + "Travelling Time:" + str(car2) + "Engine Load Sensor:" + str(car3) + "MAP Sensor:" + str(car4) + "Acceleration Pattern Sensor:" + str(car5) + "Fuel Temperature Sensor:" + str(car6)
    context2 = context1 + "Voltage Sensor:" + car7 + "RPM Sensor:" + car8 + "Max Speed Sensor:" + car9 + "Maintainence Alerts:" + car10
    
    last_day = str(st.session_state.day_count)
    context = "DAY RECORDED: " + last_day*100 + str(context2)
    # Add user behavior with the context string
    add_user_behaviour(context)
    
    # Display success message
    st.success('Data submitted successfully!')

    # Increment day count
    st.session_state.day_count += 1


def generate_insight():

    st.markdown(f'<div class="insight-container"">Insight: {llm_ask(user_summary(5))} </div>', unsafe_allow_html=True)

def generate_food_insight():

    st.markdown(f'<div class="insight-container"">Insight: {llm_ask_food(user_summary(5))} </div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
