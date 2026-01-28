import plotly.express as px

def plot_asset_history(df, symbol: str):
    """
    Interactive historical price chart for a single asset.
    """
    df_asset = df[df["symbol"] == symbol].copy()
    df_asset = df_asset.sort_values("date")

    fig = px.line(
        df_asset,
        x="date",
        y="value_pln",
        title=f"Historical price – {symbol} (PLN)",
        labels={
            "date": "Date",
            "value_pln": "Value (PLN)"
        }
    )

    # Enable range slider and zoom
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(step="all", label="All")
            ])
        )
    )

    fig.update_layout(
        hovermode="x unified",
        template="plotly_white"
    )

    fig.show()
