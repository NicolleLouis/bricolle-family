import pandas as pd
import plotly.express as px

from finance_simulator.domain.simulation_result import SimulationResult


class InterestTimeseriesChart:
    """Generate a line chart of interests paid per month."""

    @staticmethod
    def generate(simulation_result: SimulationResult) -> str:
        records = [
            {"month": amortization.month, "interest": amortization.interests}
            for amortization in simulation_result.amortizations
        ]
        df = pd.DataFrame(records)
        fig = px.line(df, x="month", y="interest")
        fig.update_layout(xaxis_title="Mois", yaxis_title="Intérêts payés")
        if simulation_result.threshold_marginal_interests_below_rent is not None:
            fig.add_vline(
                x=simulation_result.threshold_marginal_interests_below_rent,
                line_width=2,
                line_dash="dash",
                line_color="red",
                annotation_text="Marginal interests"
            )

        if simulation_result.threshold_regular_sell_below_rent is not None:
            fig.add_vline(
                x=simulation_result.threshold_regular_sell_below_rent,
                line_width=2,
                line_dash="dash",
                line_color="red",
                annotation_text="Blank Operation"
            )

        return fig.to_html(full_html=False, include_plotlyjs="cdn")


class NetCostTimeseriesChart:
    """Generate a line chart of net cost per month when the flat is sold."""

    @staticmethod
    def generate(simulation_result: SimulationResult) -> str:
        records = [
            {"month": amortization.month, "net_cost": amortization.net_sell_cost}
            for amortization in simulation_result.amortizations
        ]
        df = pd.DataFrame(records)
        fig = px.line(df, x="month", y="net_cost")
        fig.update_layout(xaxis_title="Mois", yaxis_title="Intérêts payés")
        if simulation_result.threshold_marginal_interests_below_rent is not None:
            fig.add_vline(
                x=simulation_result.threshold_marginal_interests_below_rent,
                line_width=2,
                line_dash="dash",
                line_color="red",
                annotation_text="Marginal net_costs"
            )

        if simulation_result.threshold_regular_sell_below_rent is not None:
            fig.add_vline(
                x=simulation_result.threshold_regular_sell_below_rent,
                line_width=2,
                line_dash="dash",
                line_color="red",
                annotation_text="Blank Operation"
            )

        return fig.to_html(full_html=False, include_plotlyjs="cdn")
