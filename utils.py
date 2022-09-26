import plotly.graph_objects as go
import plotly.subplots as sp
from packages import *

class Utils:
    def __init__(self):
        pass

    def render_svg(self, svg_file):

        with open(svg_file, "r") as f:
            lines = f.readlines()
            svg = "".join(lines)

            """Renders the given svg string."""
            # b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
            # html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
            return svg

    def API_related_kws(self, kw_list):
        """request to API gateway"""
        # API details
        # url = "https://cors-anywhere.herokuapp.com/https://z2azhrecpd.execute-api.us-east-1.amazonaws.com/Prod/related/"
        url = "https://z2azhrecpd.execute-api.us-east-1.amazonaws.com/Prod/related/"
        headers = {
            "Content-Type": "text/plain",
            "Origin": "/",
            "Access-Control-Allow-Origin": "*",
        }
        body = str(kw_list).encode('utf-8')
        # Making http post request

        response = requests.post(url, headers=headers, data=body)
        if response.ok:
            return response
        else:
            exit("issue with request")

    def API_trends(self, kw_list):
        """request to API gateway"""
        # API details
        #url = "https://cors-anywhere.herokuapp.com/https://z2azhrecpd.execute-api.us-east-1.amazonaws.com/Prod/trends/"
        url = "https://z2azhrecpd.execute-api.us-east-1.amazonaws.com/Prod/trends/"
        headers = {
            "Content-Type": "text/plain",
            "Origin": "/",
            "Access-Control-Allow-Origin": "*",
        }
        body = str(kw_list).encode('utf-8')
        # Making http post request

        response = requests.post(url, headers=headers, data=body)
        if response.ok:
            return response
        else:
            exit(
                "issue with request: {}, {}".format(
                    response.status_code, response.reason
                )
            )

    def clean_kws(self, kw_text):
        return [i.strip().replace("'","") for i in re.split(";|,|\n", kw_text) if len(i) > 0]

    def summary(self, df):
        """summary stats for trends df"""
        year_counts = pd.Series(df.index.year).value_counts()
        full_years = year_counts[year_counts == year_counts.max()].index.tolist()

        # LY growth rate
        growth_rates = (
            df.resample("YS").sum() / df.resample("YS").sum().shift(1, axis=0)
        ) - 1
        growth_rates = growth_rates[growth_rates.index.year == full_years[-1]]
        growth_rates = (growth_rates * 100).round(1)
        growth_rates.index = [
            "LY % Growth (FY{})".format(str(growth_rates.index.year[0])[-2:])
        ]
        growth_rates = growth_rates.T.reset_index().rename(
            mapper={"index": "kw"}, axis=1
        )

        # relative size
        totals = df.resample("YS").sum()
        ly_total = totals[totals.index.year == full_years[-1]]
        ly_total.index = [
            "LY Share of Search (FY{})".format(str(ly_total.index.year[0])[-2:])
        ]

        ly_total = (ly_total / ly_total.sum().sum() * 100).round(1)

        ly_total = ly_total.T.reset_index().rename(mapper={"index": "kw"}, axis=1)

        # CAGR
        periods = len(full_years)
        full_year_annuals = totals[totals.index.year.isin(full_years)]
        cagrs = (
            full_year_annuals.iloc[-1, :] / full_year_annuals.iloc[-periods, :]
        ) ** (1 / periods) - 1
        cagrs = (cagrs * 100).round(1)
        cagrs = cagrs.to_frame().reset_index().round(2)
        cagrs.columns = [
            "kw",
            "{}yr CAGR (FY{}-{})".format(
                periods, str(full_years[-periods])[-2:], str(full_years[-1])[-2:]
            ),
        ]

        summary_df = ly_total.merge(
            growth_rates, how="outer", right_on="kw", left_on="kw"
        ).merge(cagrs, how="outer", right_on="kw", left_on="kw")
        return summary_df

    def plotly_fig(self, df):
        """plotly figure for trends df"""

        # Create figure with secondary y-axis
        fig = sp.make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Scatter(
                x=df.index.values, y=df.sum(axis=1).values, name="Category Total", line_width=3,line_color='Black'
            ),
            secondary_y=True,
        )

        for i in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index.values, y=df[i].values, name=i, line_width=1,visible = "legendonly"),
                secondary_y=False,
            )

        # Set x-axis title
        fig.update_xaxes(title_text="Date")

        # Set y-axes titles
        fig.update_yaxes(title_text="Keyword Axis", secondary_y=False)
        fig.update_yaxes(title_text="Category Axis", secondary_y=True)

        return fig

    def test_plotly(self):
        return sp
