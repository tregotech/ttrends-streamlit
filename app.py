from packages import *
from utils import Utils

Utils = Utils()

MAX_DISPLAY = 10
CORS_URL = "https://cors-anywhere.herokuapp.com/"

menu_items = {"About": "www.trego.tech"}
line_HTML = (
    """<hr style="height:1px;border:none;color:#333;background-color:#333;" /> """
)

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
        
        st.image("assets/favicon.png", width=50)
        st.title("Trego Category Search Trends")
  
        # components.html(line_HTML)

        ################# sidebar - seed kws #################
        st.subheader("1). Start with some keywords in your category...")
        st.text_input(
            "",
            key="seed_kws",
            help="Enter seed terms separated by commas, semicolons, or new lines",
        )

        col1, col2 = st.columns(2)
        related_button = col1.button("🔍 Find related terms")
        add_kws_button = col2.button("➕ Add keywords")

        if related_button:
            clean_seed_kws = Utils.clean_kws(st.session_state.seed_kws)
            result = Utils.API_related_kws(clean_seed_kws)
            data = json.loads(result.json()["message"])
            st.session_state.api_related_kws.update(set(data))
            # st.session_state.api_related_kws.update(set(random.choices(WORDS, k=50)))

        if add_kws_button:
            clean_seed_kws = Utils.clean_kws(st.session_state.seed_kws)
            st.session_state.kws.update(set(clean_seed_kws))

        ################# sidebar - related kws #################
        st.subheader("2. Find related keywords (optional)")

        selected = sorted(list(st.session_state.api_related_kws))[:MAX_DISPLAY]
        selection_text = "{} related keywords found, showing first {}".format(
            str(len(st.session_state.api_related_kws)), len(selected)
        )

        st.code(selection_text)

        if len(st.session_state.api_related_kws) > 0:
            st.multiselect(
                "",
                sorted(list(st.session_state.api_related_kws)),
                key="selected_related_kws",
                default=selected,
            )

        if st.button("➕ Add Selected", help="Click 'Get related kws' & select below"):
            if len(st.session_state.selected_related_kws) > 0:
                st.session_state.kws.update(set(st.session_state.selected_related_kws))
                # st.session_state.selected_related_kws = set()
                # st.session_state.api_related_kws = set()

        ################# display #################
        st.subheader("3. Visualise category trends")

        st.code(sorted(st.session_state.kws))

        col3, col4 = st.columns(2)
        get_trends_button = col3.button("📈 Get trends")
        restart_button = col4.button("🗑️ Restart")

        if get_trends_button:
            result = Utils.API_trends(list(st.session_state.kws))
            df = pd.DataFrame(result.json()["message"]["data"])
            self.DATECOLUMN = df.columns.tolist()[0]
            df[self.DATECOLUMN] = pd.to_datetime(df[self.DATECOLUMN])
            st.session_state.trends_df = df.copy()


            summary = Utils.summary(st.session_state.trends_df.set_index(self.DATECOLUMN))
            
            category_summary = Utils.summary(
                st.session_state.trends_df.set_index(self.DATECOLUMN).sum(axis=1).to_frame()
            )
            category_summary = category_summary[
                [
                    i
                    for i in category_summary.columns
                    if "kw" not in i.lower() and "size" not in i.lower()
                ]
            ]

            st.subheader("Category Summmary")
            st.text(('all keywords'))

            col1, col2 = st.columns(2)
            kpi1 = category_summary.columns[0]
            kpi2 = category_summary.columns[1]
            col1.metric(kpi1, category_summary[kpi1])
            col2.metric(kpi2, category_summary[kpi2])

            st.subheader("Keyword Detail")
            gb = GridOptionsBuilder.from_dataframe(summary)
            # gb.configure_selection(selection_mode="multiple", use_checkbox=True)
            gridOptions = gb.build()

            data = AgGrid(
                summary,
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
            #     allow_unsafe_jscode=True,
            #     update_mode=GridUpdateMode.SELECTION_CHANGED,
            )
            data

            # selected_rows = pd.DataFrame(data["selected_rows"])

            ## plot chart if rows are selected
            # if len(selected_rows) != 0:
            #     selected_kws = selected_rows.kw.tolist()

            fig = px.line(st.session_state.trends_df.reset_index(), x=self.DATECOLUMN, y=st.session_state.trends_df.columns)
            fig.update_layout(paper_bgcolor="rgb(211,220,220)")
            st.plotly_chart(fig)

            st.download_button(
                "💾 Download (.csv)",
                st.session_state.trends_df.to_csv().encode("utf-8"),
                file_name="trends_data.csv",
            )

        if restart_button:
            st.session_state.kws = set()


if __name__ == "__main__":
    trend = Trends()
    trend.main()
