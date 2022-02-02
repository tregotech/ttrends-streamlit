import streamlit as st
import streamlit.components.v1 as components



import pandas as pd
import numpy as np
import re
import requests
import random
import json

f = open("assets/words.rtf", "r")
text = f.read()
WORDS = text.split("\\\n")

MAX_DISPLAY = 10
CORS_URL = "https://cors-anywhere.herokuapp.com/"

menu_items = {"About": "www.trego.tech"}
line_HTML = """<hr style="height:2px;border:none;color:#333;background-color:#333;" /> """

st.set_page_config(
    page_title="ttrends-streamlit",
    page_icon="assets/favicon.png",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=menu_items,
)


class Trends:
    def __init__(self):
        pass

    def main(self):

        ################# state vars #################
        if "kws" not in st.session_state:
            st.session_state.kws = set()
        if "api_related_kws" not in st.session_state:
            st.session_state.api_related_kws = set()
        if "selected_related_kws" not in st.session_state:
            st.session_state.selected_related_kws = set()
        if "trends_df" not in st.session_state:
            st.session_state.trends_df = pd.DataFrame()

        ################# intro #################
        st.title("Ttrends")
        st.text("some description text")
        components.html(line_HTML)


        ################# sidebar - seed kws #################
        st.sidebar.subheader("Expand Keywords")
        st.sidebar.text_area(
            "",
            "adele",
            key="seed_kws",
            help="Enter seed terms separated by commas, semicolons, or new lines",
        )
        if st.sidebar.button("Get related kws"):
            clean_seed_kws = self.clean_kws(st.session_state.seed_kws)
            result = self.API_related_kws(clean_seed_kws)
            data = json.loads(result.json()["message"])
            st.session_state.api_related_kws.update(set(data))
            # st.session_state.api_related_kws.update(set(random.choices(WORDS, k=50)))

        if st.sidebar.button("Add to my kws"):
            clean_seed_kws = self.clean_kws(st.session_state.seed_kws)
            st.session_state.kws.update(set(clean_seed_kws))

        ################# sidebar - related kws #################
        st.sidebar.subheader("Related terms")

        if len(st.session_state.api_related_kws) > 0:
            self.multi()

        if st.sidebar.button(
            "Add related kws", help="Click 'Get related kws' & select below"
        ):
            if len(st.session_state.selected_related_kws) > 0:
                st.session_state.kws.update(set(st.session_state.selected_related_kws))
                # st.session_state.selected_related_kws = set()
                # st.session_state.api_related_kws = set()

        ################# display #################
        st.subheader("My kws", anchor=None)

        if len(st.session_state.kws) > 0:
            st.write(str(sorted(st.session_state.kws)))

            fake_data = pd.DataFrame(
                columns=sorted(st.session_state.kws),
                index=pd.date_range(start="2018-01-01", end="2021-01-01", freq="M"),
            )

        if st.button("Get trends", help="Click 'Get related kws' & select below"):
            result = self.API_trends(list(st.session_state.kws))
            df = pd.DataFrame(result.json()["message"]["data"])
            df["date"] = pd.to_datetime(df.date)
            df.set_index("date", inplace=True)
            st.session_state.trends_df = df
            st.line_chart(df)


        components.html(line_HTML)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Category 5y CAGR", "", "8%")
        col2.metric("LY Growth Rate", "", "-8%")

    def multi(self):
        selection_text = "{} suggested keywords".format(
            str(len(st.session_state.api_related_kws))
        )

        st.sidebar.multiselect(
            selection_text,
            sorted(list(st.session_state.api_related_kws)),
            key="selected_related_kws",
            default=sorted(list(st.session_state.api_related_kws))[:MAX_DISPLAY],
        )
        return None

    def API_related_kws(self, kw_list):
        """request to API gateway"""
        # API details
        url = "https://cors-anywhere.herokuapp.com/https://z2azhrecpd.execute-api.us-east-1.amazonaws.com/Prod/related/"
        headers = {
            "Content-Type": "text/plain",
            "Origin": "/",
            "Access-Control-Allow-Origin": "*",
        }
        body = str(kw_list)
        # Making http post request

        response = requests.post(url, headers=headers, data=body)
        if response.ok:
            return response
        else:
            exit("issue with request")

    def API_trends(self, kw_list):
        """request to API gateway"""
        # API details
        url = "https://cors-anywhere.herokuapp.com/https://z2azhrecpd.execute-api.us-east-1.amazonaws.com/Prod/trends/"
        headers = {
            "Content-Type": "text/plain",
            "Origin": "/",
            "Access-Control-Allow-Origin": "*",
        }
        body = str(kw_list)
        # Making http post request

        response = requests.post(url, headers=headers, data=body)
        if response.ok:
            return response
        else:
            exit("issue with request: {}, {}".format(response.status_code,response.reason))

    def clean_kws(self, kw_text):
        return [
                i.strip()
                for i in re.split("; |, |\n", kw_text)
                if len(i) > 0
            ]


if __name__ == "__main__":
    trend = Trends()
    trend.main()
