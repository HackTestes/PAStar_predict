import plotly.express as px
import pandas as pd
import plotly.io
#plotly.io.renderers.default = 'chromium'

data = pd.read_feather("./data/4000_samples.feather")

def plot_graph()

#fig = px.scatter(y=data.Nodes, x=data.Seq_size)
#
#fig.update_layout(xaxis={"tickmode":"array", "tickvals": data.Seq_size})
#
#fig.update_layout(
#    title={
#        'text': "Relação de nós e tamanho das sequências",
#        'x': 0.5,
#        'xanchor': 'center',
#        'yanchor': 'top'},
#    xaxis_title="Tamanho das sequências",
#    yaxis_title="Nós",
#    font=dict(
#        family="Courier New, monospace",
#        size=18,
#        color="Black"
#    )
#)
#
##fig.show()
#fig.write_image("./graphs/Nos.png", scale=3.0, width=1100, height=1000)
#
#
#fig = px.scatter(y=(data.Nodes/(data.Seq_size**3))*100, x=data.Seq_size)
#
#fig.update_layout(xaxis={"tickmode":"array", "tickvals": data.Seq_size})
#
#fig.update_layout(
#    title={
#        'text': "Relação de nós e tamanho das sequências",
#        'x': 0.5,
#        'xanchor': 'center',
#        'yanchor': 'top'},
#    xaxis_title="Tamanho das sequências",
#    yaxis_title="Nós / Pior caso",
#    font=dict(
#        family="Courier New, monospace",
#        size=18,
#        color="Black"
#    )
#)
#fig.write_image("./graphs/Nos_PiorCaso.png", scale=3.0, width=1100, height=1000)
#
#
fig = px.box(y=data.Nodes, x=data.Seq_size)

fig.update_layout(xaxis={"tickmode":"array", "tickvals": data.Seq_size})

fig.show()
