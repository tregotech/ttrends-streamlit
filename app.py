from packages import *
from utils import Utils

Utils = Utils()

MAX_DISPLAY = 25
CORS_URL = "https://cors-anywhere.herokuapp.com/"

menu_items = {"About": "www.trego.tech"}
line_HTML = (
    """<hr style="height:1px;border:none;color:#333;background-color:#333;"/> """
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
        st.title("Share of Search Tracker")

        link1 = "https://www.kantar.com/uki/inspiration/advertising-media/share-of-search-your-moment-has-arrived"
        link2 = (
            "https://www.marketingweek.com/mark-ritson-share-of-search-share-of-voice/"
        )
        github_link = "https://github.com/tregotech/ttrends"



        #st.markdown(
        #    "Track **share of search** using Google search trends from **>5 search terms***. \
        #    \
        #    Share of search is a leading indicator of brand strength in a digital world [[1]]({}) [[2]]({}).".format(
        #        link1, link2
        #    )
        #)

        ################# sidebar - seed kws #################
        st.header('Category Keywords')
        st.text_input(label="Start with some 'seed' search terms in your category, separated by commas",key="seed_kws")

        col1, col2 = st.columns(2)
        related_button = col1.button("🔍 Get related")
        add_kws_button = col2.button("➕ Add search terms")

        if related_button:
            with st.spinner('Wait for it...'):
                clean_seed_kws = Utils.clean_kws(st.session_state.seed_kws)
                result = Utils.API_related_kws(clean_seed_kws)
                data = json.loads(result.json()["message"])
                st.session_state.api_related_kws = set(data)
            st.success('Done!')

        if add_kws_button:
            clean_seed_kws = Utils.clean_kws(st.session_state.seed_kws)
            st.session_state.kws.update(set(clean_seed_kws))

        st.code(str(len(st.session_state.api_related_kws)) + " related terms: " + str(sorted(st.session_state.api_related_kws)))

        if st.button("➕ Add all related terms"):
            st.session_state.kws.update(set(st.session_state.api_related_kws))

        ################# display #################
        st.header('Share of Search')

        st.code(str(len(st.session_state.kws)) + " search terms: " + str(sorted(st.session_state.kws)))

        col3, col4 = st.columns(2)
        get_trends_button = col3.button("📈 Get trends")
        restart_button = col4.button("🗑️ Restart")

        if get_trends_button:
            with st.spinner('Wait for it...'):
                result = Utils.API_trends(list(st.session_state.kws))
                df = pd.DataFrame(result.json()["message"]["data"])
                self.DATECOLUMN = df.columns.tolist()[0]
                df[self.DATECOLUMN] = pd.to_datetime(df[self.DATECOLUMN])
                st.session_state.trends_df = df.copy()

                summary = Utils.summary(
                    st.session_state.trends_df.set_index(self.DATECOLUMN)
                )

                category_summary = Utils.summary(
                    st.session_state.trends_df.set_index(self.DATECOLUMN)
                    .sum(axis=1)
                    .to_frame()
                )
                category_summary = category_summary[
                    [
                        i
                        for i in category_summary.columns
                        if "kw" not in i.lower() and "share" not in i.lower()
                    ]
                ]

                st.success('Done!')
                st.subheader("Category Summmary")
                st.text(("all search terms"))

                col1, col2 = st.columns(2)
                kpi1 = category_summary.columns[0]
                kpi2 = category_summary.columns[1]
                col1.metric(kpi1, category_summary[kpi1])
                col2.metric(kpi2, category_summary[kpi2])

                gb = GridOptionsBuilder.from_dataframe(summary)
                # gb.configure_selection(selection_mode="multiple", use_checkbox=True)
                gridOptions = gb.build()

                data = AgGrid(
                    summary,
                    gridOptions=gridOptions,
                    enable_enterprise_modules=True,
                )
                data

                # chart
                fig = Utils.plotly_fig(
                    st.session_state.trends_df.set_index(self.DATECOLUMN)
                )
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
